import digitalocean
from digitalocean import SSHKey

# def create_droplet():
    # actions = droplet.get_actions()
    # for action in actions:
    #     action.load()
    #     # Once it shows complete, droplet is up and running
    #     print(action.status)

def main():
    my_api_token=''

    user_ssh_key = open('/home/john/.ssh/id_ssh_rsa.pub').read()
    key = SSHKey(token=my_api_token,
                 name='chin_id',
                 public_key=user_ssh_key)
    key.create()
    manager = digitalocean.Manager(token=my_api_token)
    keys = manager.get_all_sshkeys()

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
                                      - sudo -H --user buildbot /home/buildbot/venv/bin/buildbot-worker create-worker worker localhost example-worker pass
                                      - mkdir -p /opt/builbotdata
                                      - git clone https://github.com/johnramsden/bez /opt/builbotdata/bez
                                   """)
    droplet.create()


if __name__ == "__main__":
    # execute only if run as a script
    main()
