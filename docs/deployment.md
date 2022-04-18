# Deployment with Ansible Playbook

The Ansible playbook, an SSH configuration file, and a `hosts.yml` inventory file are used for server deployments.

## Requirements

Use the installation instructions found in [Local Ansible Playbook Development with Vagrant](vagrant.md) to install:
* Ansible
* Vagrant
* Miniconda3

Your SLATE project private RSA key file (e.g. `id_rsa_slate`) will also be required to interact with the Portal servers. If you have not set this up yet contact the team via Slack.

### Create `secrets.yml`

Copy `ansible/secrets.yml.tmpl` to the following place in this project: `ansible/secrets.yml`. Complete the steps described below to modify placeholder key-value pairs and finalize this file.

### Create `hosts.yml`

Copy `ansible/inventory/hosts.yml.tmpl` to the following place in this project `ansible/inventory/hosts.yml`. Complete the steps described below to modify placeholder key-value pairs and finalize this file.

For more information on Ansible inventories see:
* [How to build your inventory](https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html)
* [ansible.builtin.yaml – Uses a specific YAML file as an inventory source.](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/yaml_inventory.html)

### Register a globus Application

> **_IMPORTANT:_** Before proceeding ask the team about existing globus registrations as some development and production projects and applications already exist.

Create your own App registration for use in the Portal.

* Visit the [Globus Developer Pages](https://developers.globus.org) to register an App.
* If this is your first time visiting the Developer Pages you will be asked to create a Project. A Project is a way to group Apps together.
* When registering the App you will be asked for some information, including the redirect URL and any scopes you will be requesting.
    * Redirect URL (if development): `https://portal-dev.slateci.io/authcallback`
    * Redirect URL (if production): `https://portal.slateci.io/authcallback`
* After creating your App the **Client ID** and **Client Secret** can be copied into this project in the following place:
    * `ansible/secrets.yml` in the `slate_portal_client_id` and `slate_portal_client_secret` key values.

### Select a SLATE API Admin Account

* Ask the team for the API token of an appropriate admin account.
* Once in hand the token can be copied to the following place in this project:
    * `ansible/secrets.yml` in the `slate_api_token` key value.

### Select a mailgun API Token

Portal communicates with users via email with [mailgun](https://www.mailgun.com/).
* Ask the team for an appropriate API token.
* Once in hand the token can be copied to the following place in this project:
    * `ansible/secrets.yml` in the `mailgun_api_token` key value.

## Finalize `secrets.yml`

At this point `ansible/secrets.yml` should resemble:

```yaml
---
mailgun_api_token: "SAMPLE"
slate_api_token: "SAMPLE"
slate_portal_client_id: "SAMPLE"
slate_portal_client_secret: "SAMPLE"
```

## Finalize `hosts.yml`

Add actual values in place of `<group>`, `<host>`, `<slate-user>`, and `<priv-key-path>` to `ansible/inventory/hosts.yml` in this project. At this point the file should resemble:

Development:

```yaml
all:
  children:
    dev:
      hosts:
        portal:
          ansible_host: portal-dev.slateci.io
  vars:
    ansible_ssh_common_args: '-o ProxyCommand="ssh -W %h:%p -q SAMPLE@bastion.slateci.net -i /path/to/id_rsa_slate"'
    ansible_ssh_private_key_file: '/path/to/id_rsa_slate'
    ansible_user: 'SAMPLE'
```

Production:

```yaml
all:
  children:
    prod:
      hosts:
        portal:
          ansible_host: portal.slateci.io
  vars:
    ansible_ssh_common_args: '-o ProxyCommand="ssh -W %h:%p -q SAMPLE@bastion.slateci.net -i /path/to/id_rsa_slate"'
    ansible_ssh_private_key_file: '/path/to/id_rsa_slate'
    ansible_user: 'SAMPLE'
```

## Build and Run Portal

Activate the Conda environment, change directories, and verify Ansible can see the host(s):

```shell
[your@localmachine]$ conda activate chpc-ansible
(chpc-ansible) [your@localmachine]$ cd ./ansible
(chpc-ansible) [your@localmachine]$ ansible all -m ping -i ./inventory/hosts.yml
portal | SUCCESS => {
    "ansible_facts": {
        "discovered_interpreter_python": "/usr/bin/python"
    },
    "changed": false,
    "ping": "pong"
}
```

Test permission escalation on the host(s):

```shell
(chpc-ansible) [your@localmachine]$ ansible all -a "/bin/ls -al /root" -i ./inventory/hosts.yml -u <slate-user> --become --become-user root
portal | CHANGED | rc=0 >>
total 40
dr-xr-x---.  3 root root  170 Feb 28 22:27 .
dr-xr-xr-x. 17 root root  224 Jul  3  2017 ..
-rw-------.  1 root root 6913 Jul  3  2017 file.ext
...
```

**Note:** If you receive an error during these steps, double-check the contents of your `hosts.yml` file, paying special attention to the Ansible variables.

Finally, verbosely run the Ansible playbook itself:

```shell
(chpc-ansible) [your@localmachine]$ ansible-playbook -v -i ./inventory/hosts.yml --extra-vars "@./secrets.yml" ./playbook.yml
Using /project-path/ansible/ansible.cfg as config file

PLAY [all] ******************************************************************************************************************

TASK [Gathering Facts] ******************************************************************************************************
...
...
```

## Teardown

Currently, this is a manual process. At some point the playbook will be expanded to help uninstall Portal and return the host to a clean state.

On your local machine deactivate the Conda environment:

```shell
(chpc-ansible) [your@localmachine]$ conda deactivate
[your@localmachine]$
```
