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