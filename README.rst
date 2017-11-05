Buildbot module for latent digitalocean workers
================================================

**NOTE: Work in progress, not ready for use.**

``digitalocean-latent-worker`` is a `Buildbot <https://github.com/buildbot/buildbot>`_ plugin for creating latent DigitalOcean workers.

DigitalOcean virtual machines can be created on the fly, and then destroyed when they are finished doing a build. Setup instructions can be customized with the ``user_data`` variable as `cloud-init <https://cloud-init.io/>`_ data, shell script, or any other type of setup data is supported by DigitalOcean.

Using the DigitalOcean API
--------------------------

Create an API token on DigitalOcean.

The API key, an SSH key and other necessary setup data can be given to the initializer for the worker class.

It's reccomended to put all secret data into a ``password.py`` file so it can be kept separate from the rest of the files that might be committed to a repository.

Examples
^^^^^^^^

Example sample files can be found in the `buildbot/master <buildbot/master>`_ directory.

Secrets in  ``password.py``::

    digitalocean_api_key = "thisisafakeapikey"
    bb_worker_pass = "example_pass"

Configuration in ``master.cfg``::

    c = BuildmasterConfig = {}

    c['workers'] = [
        worker.DigitalOceanLatentWorker(
            "bb-worker", password.bb_worker_pass,
            "ubuntu-16-04-x64", password.digitalocean_api_key,
            ssh_keys=['ssh_id'], user_data=workers.do_worker_user_data)
    ]
