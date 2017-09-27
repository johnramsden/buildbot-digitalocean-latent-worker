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
                 ssh_keys=None, size_slug='512mb', backups=False, user_data=None, **kwargs):

        AbstractLatentWorker.__init__(self, name, password, **kwargs)

        self.api_token = api_token
        self.do_manager = digitalocean.Manager(token=self.api_token)

        usable_region = self._get_available_region(region)
        if usable_region is not None:
            self.region = usable_region
            log.msg("Set region to:", self.region)
        else:
            raise ValueError("No regions available")

        self.name = name
        self.password = password
        self.image = self.get_image(image)
        self.size_slug = size_slug
        self.backups = backups

        if ssh_keys is None:
            self.ssh_keys = []
        else:
            self.ssh_keys = self._get_ssh_keys(ssh_keys)

        if user_data is None:
            self.user_data = ""
        else:
            self.user_data = user_data

    def get_image(self, image_id=None):
        # if self.image is not None:
        #     image = self.image
        # else:
        image = None

        avail_images = self.do_manager.get_all_images()

        for i in avail_images:
            if i.slug == image_id:
                image = i
                log.msg("Found image:", image_id)
                break

        if image is None:
            raise ValueError("No image ", image_id, " available")

        return image

    """
    Note, Doesn't work, cannot get image using image ID
    """
    # def _image_exists(self, image_id):
    #     '''
    #     Note, Doesn't work, cannot get image using image ID
    #     '''
    #     exists = False
    #
    #     avail_images = self.do_manager.get_all_images()
    #
    #     for image in avail_images:
    #         pimage = self.do_manager.get_image(image_id)
    #         print(pimage)
    #         if image.slug == image_id:
    #             exists = True
    #             break
    #
    #     return exists



    def start_instance(self, build):
        # if self.instance is not None:
        #     raise ValueError('instance active')
        # else:
            self._start_instance()

    def _start_instance(self):
        droplet = digitalocean.Droplet(token=self.api_token,
                                       name=self.name,
                                       region=self.region,
                                       image=self.image.slug,
                                       size_slug=self.size_slug,
                                       backups=self.backups,
                                       ssh_keys=self.ssh_keys,
                                       user_data=self.user_data)
        droplet.create()

        actions = droplet.get_actions()

        status = "in-progress"

        while status == "in-progress":
            for action in actions:
                action.load()
                # Once it shows complete, droplet is up and running
                status = action.status
                print(status)

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


    def _get_ssh_keys(self, key_names):
        """
        Look for matches to any keys from list key_names.
        :param key_names: List of wanted keys
        :return keys: A list of key matches on digitalocean
        """
        keys = [self.do_manager.get_ssh_key(k.id)
                for k in self.do_manager.get_all_sshkeys() if k.name in key_names]

        # Check if keys is empty
        if not keys:
            raise Exception("One or more keys couldn't be found ", *key_names)

        return keys

    #- sudo -H --user buildbot /home/buildbot/venv/bin/buildbot-worker create-worker worker localhost example-worker pass

def main():
    start_commands = """
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
   """
    log.startLogging(sys.stdout)
    do_latent_worker = DigitalOceanLatentWorker("Bip", "pass", "ubuntu-16-04-x64",
                                                password.digitalocean_api_key, ssh_keys=['chin_id'],
                                                user_data=start_commands)

    do_latent_worker.start_instance(True)

if __name__ == "__main__":
    # execute only if run as a script
    main()
