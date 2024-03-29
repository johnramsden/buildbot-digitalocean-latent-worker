# the inclusion of the tests module is not meant to offer best practices for
# testing in general, but rather to support the `find_packages` example in
# setup.py that excludes installing the "tests" package

from buildbot.plugins import worker, util, schedulers, changes, steps

import sys

from twisted.python import log

import password
import workers

import DigitalOceanLatentWorker

def main():
    log.startLogging(sys.stdout)
    log.msg("Creating test worker")

    bez_git_repo = 'https://{}{}@github.com/johnramsden/bez'.format(
        password.github_token, ":x-oauth-basic")

    dolw = worker.DigitalOceanLatentWorker(
        "bez-worker", password.bez_worker_pass,
        "ubuntu-16-04-x64", password.digitalocean_api_key,
        ssh_keys=['chin_id'], user_data=workers.do_worker_user_data['ubuntu']['user_data'])

    if not dolw.start_instance(True):
        raise ValueError("Failed to start DO droplet")

    if not dolw.stop_instance():
        raise ValueError("Failed to stop DO droplet")

if __name__ == "__main__":
    # execute only if run as a script
    main()