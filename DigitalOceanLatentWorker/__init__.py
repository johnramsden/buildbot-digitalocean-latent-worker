import digitalocean
from digitalocean import SSHKey

import os
import sys

from twisted.python import log

from buildbot import config
from buildbot.interfaces import LatentWorkerFailedToSubstantiate
from buildbot.worker import AbstractLatentWorker
from buildbot.worker_transition import reportDeprecatedWorkerNameUsage

class DigitalOceanLatentWorker(AbstractLatentWorker):

    instance = image = None

    def __init__(self, name, password, droplet_image, api_token, region=None,
                 ssh_keys=None, size_slug='512mb', backups=False,
                 user_data=None, **kwargs):

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
        self.droplet_image = None
        self.droplet_image = self.get_do_image(image_slug=droplet_image)
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

        self.droplet = self._configure_droplet()

    def _matching_image(self, droplet_slug):
        """
        Takes slug looking to match, returns None if no match, or the image matched
        :param droplet_slug:
        :param slug_image_pair:
        :return:
        """
        droplet_image = None
        for i in [(i.slug, i) for i in self.do_manager.get_all_images()]:
            if droplet_slug==i[0]:
                droplet_image = i[1]

        return droplet_image

    def get_do_image(self, image_slug=None):
        """
        Set default to current image if no id given, else ask for id if no image
        :param image_id:
        :return: image
        """
        droplet_image = None

        if image_slug is None:
            if self.droplet_image is not None:
                droplet_slug = self.droplet_image.slug
            else:
                raise ValueError("No image currently set or requested.")
        else:
            droplet_slug = image_slug

        droplet_image = self._matching_image(droplet_slug)
        if droplet_image is None:
            raise ValueError("Requested image not in DigitalOcean images.")

        log.msg("Found image:", droplet_image.slug)
        return droplet_image

    def _configure_droplet(self):
        return digitalocean.Droplet(token=self.api_token,
                                    name=self.name,
                                    region=self.region,
                                    image=self.droplet_image.slug,
                                    size_slug=self.size_slug,
                                    backups=self.backups,
                                    ssh_keys=self.ssh_keys,
                                    user_data=self.user_data)


    def start_instance(self, build):
        if self.instance is not None:
            raise ValueError('instance active')

        return self._start_instance()

    def _start_instance(self):
        ret_success = True

        self.droplet.create()
        actions = self.droplet.get_actions()

        status = "in-progress"
        while status == "in-progress":
            for action in actions:
                action.load()
                # Once status shows complete, droplet is up and running
                status = action.status

        if status != "completed":
            ret_success = False
            log.msg("Instance failed to start with message: ", status)
        else:
            log.msg("Started image ", self.droplet_image.slug, " successfully.")

        return ret_success

    def stop_instance(self):
        ret_success = True
        log.msg("Starting instance termination sequence for ", self.name)

        self.droplet.shutdown()

        actions = self.droplet.get_actions()

        status = "in-progress"
        while status == "in-progress":
            for action in actions:
                action.load()
                # Once status shows complete, droplet shutdown
                status = action.status

        if status != "completed":
            ret_success = False
            log.msg("Instance failed to stop with message: ", status)
        else:
            log.msg("Stopped droplet ", self.name, " successfully.")

        log.msg("Destroying droplet ", self.name)
        if not self.droplet.destroy():
            raise ValueError("Droplet failed to destroy")

        return ret_success

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

def main():
    log.startLogging(sys.stdout)

if __name__ == "__main__":
    # execute only if run as a script
    main()
