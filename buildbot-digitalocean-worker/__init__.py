import digitalocean
from digitalocean import SSHKey

import os
import sys

from twisted.python import log

from buildbot import config
from buildbot.interfaces import LatentWorkerFailedToSubstantiate
from buildbot.worker import AbstractLatentWorker
from buildbot.worker_transition import reportDeprecatedWorkerNameUsage
import password

class DigitalOceanLatentWorker(AbstractLatentWorker):

    instance = image = None

    def __init__(self, name, password, image, api_token, region=None,
                 ssh_key=None, size_slug=None, backups=False, user_data=None, **kwargs):

        AbstractLatentWorker.__init__(self, name, password, **kwargs)

        self.api_token = api_token

        usable_region = self._get_available_region(region)
        if usable_region is not None:
            self.region = usable_region
            log.msg("Set region to:", self.region)
        else:
            raise ValueError("No regions available")

        self.name = name
        self.password = password
        self.image = image
        self.size_slug = size_slug
        self.backups = backups
        self.user_data = user_data
        self.ssh_key = ssh_key

    def get_image(self):
        if self.image is not None:
            image = self.image
        else:
            raise ValueError('no available images match constraints')

        '''
        TODO: Should I return any image if none specified?
        See: https://github.com/buildbot/buildbot/blob/cccd4d6990a1b02fc4653361744eafed0dcaa973/master/buildbot/worker/ec2.py#L331
        '''

        return image



    def start_instance(self, build):
        if self.instance is not None:
            raise ValueError('instance active')

    def _start_instance(self):
        image = self.get_image()

    def stop_instance(self):
        print("Stopping instance.")

    def _get_available_region(self, region=None):
        available_region = None
        do_region = digitalocean.Region(token=self.api_token)

        region_data = do_region.get_data("/v2/regions")

        for r in region_data.get('regions'):
            if r is not None:
                """Default to region specified if unset"""
                if r['slug'] is region:
                    if r['available'] is True:
                        available_region = r['slug']
                    else:
                        available_region = None

                """
                If region unavailable, keep looking for available if region wasn't specified.
                If region was specified and unavailable, print error 
                """
                if region is None:
                    if r['available'] is True:
                        available_region = r['slug']
                else:
                    available_region = None

        if available_region is None:
            raise ValueError("Region", region, "was unavailable.")

        return available_region

    def add_ssh_key(self, path, key_name):
        manager = digitalocean.Manager(token=self.api_token)
        keys = manager.get_all_sshkeys()
        for k in keys:
            if k.name == key_name:
                raise Exception("Key ", key_name, "already exists, use another id")

        #print(manager.get_ssh_key("2213846"))

        # user_ssh_key = open(path).read()
        # key = SSHKey(token=self.api_token,
        #               name=key_name,
        #               public_key=user_ssh_key)
        # key.create()

def create_droplet():
    # user_ssh_key = open('/home/john/.ssh/id_ssh_rsa.pub').read()
    # key = SSHKey(token=my_api_token,
    #              name='chin_id',
    #              public_key=user_ssh_key)
    # key.create()



    droplet = digitalocean.Droplet(token=my_api_token,
                                   name='Buildbot',
                                   region='sfo1',
                                   image='ubuntu-16-04-x64',
                                   size_slug='512mb',
                                   backups=False,
                                   ssh_keys=keys,
                                   user_data="""
                                    #cloud-config

                                    runcmd:
                                      - apt-get update
                                      - apt-get install -y python3-pip python3-venv python3-setuptools
                                      - apt-get install -y git
                                      - addgroup --system buildbot
                                      - adduser buildbot --system --ingroup buildbot --shell /bin/bash
                                      - sudo --user buildbot python3 -m venv /home/buildbot/venv
                                      - sudo -H --user buildbot /home/buildbot/venv/bin/pip install --upgrade pip
                                      - sudo -H --user buildbot /home/buildbot/venv/bin/pip install --upgrade setuptools-trial
                                      - sudo -H --user buildbot /home/buildbot/venv/bin/pip install --upgrade buildbot-worker
                                      - mkdir -p /opt/builbotdata
                                      - git clone https://github.com/johnramsden/bez /opt/builbotdata/bez
                                   """)
    droplet.create()

    #- sudo -H --user buildbot /home/buildbot/venv/bin/buildbot-worker create-worker worker localhost example-worker pass

def main():
    log.startLogging(sys.stdout)
    do_latent_worker = DigitalOceanLatentWorker("Bob", "pass", "image", password.digitalocean_api_key)
    #do_latent_worker.start_instance(False)
    do_latent_worker.add_ssh_key("pip", "chin_id")

if __name__ == "__main__":
    # execute only if run as a script
    main()
