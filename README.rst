Buildbot module for latent digitalocean workers
=======================

Readme for buildbot module for latent digitalocean workers.

Requirements:
python-digitalocean

---

Development:

Create virtualenv inside project:
python -m venv venv

Activate venv:
source venv/bin/activate

Install requirements:
pip install -U python-digitalocean

Buildbot:
source venv/bin/activate
pip install -U 'buildbot[bundle]'

Save Requirements:
pip freeze > requirements.txt

---

API:

Create an API token

Setup user_data to run on the droplet. for example:

#cloud-config

runcmd:
  - apt-get update
  - apt-get install -y python-pip
  - apt-get install -y git
  - mkdir -p /opt/builbotdata
  - git clone https://github.com/johnramsden/sample_app /opt/builbotdata/sample_app

To get region info, run:
curl -X GET https://api.digitalocean.com/v2/regions -H 'Authorization: Bearer <TOKEN>'