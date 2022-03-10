# Deployment with Ansible Playbook

The Ansible playbook, an SSH configuration file, and a `hosts.yml` inventory file are used for server deployments.

## Requirements

Use the installation instructions found in [Local Ansible Playbook Development with Vagrant](vagrant.md) to install:
* Ansible
* Vagrant
* Miniconda3

Your SLATE project private RSA key file (e.g. `id_rsa_slate`) will also be required to interact with the Portal servers. If you have not set this up yet contact the team via Slack.

### Create `ssh-config`

Both the development and production Portal servers are not internet-accessible via SSH and require a jump through a [Bastion server](https://www.learningjournal.guru/article/public-cloud-infrastructure/what-is-bastion-host-server/) (or Jump Box). The easiest way to configure SSH for Ansible is through a configuration file.

Copy `ansible/inventory/ssh-config.tmpl` to the following place in this project `ansible/inventory/<dev|prod>/ssh-config`. Complete the steps described below to modify placeholder settings values and finalize this file.

### Create `hosts.yml`

Each environment should have a separate inventory file to prevent unexpected deployments. Use the appropriate template below to create your inventory file.

For more information on Ansible inventories see:
* [How to build your inventory](https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html)
* [ansible.builtin.yaml – Uses a specific YAML file as an inventory source.](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/yaml_inventory.html)

Copy `ansible/inventory/hosts.yml.tmpl` to the following place in this project `ansible/inventory/<dev|prod>/hosts.yml`. Complete the steps described below to modify placeholder key-value pairs and finalize this file.

### Register a globus Application

> **_IMPORTANT:_** Before proceeding ask the team about existing globus registrations as development, and production projects and applications should already exist.

Create your own App registration for use in the Portal.

* Visit the [Globus Developer Pages](https://developers.globus.org) to register an App.
* If this is your first time visiting the Developer Pages you will be asked to create a Project. A Project is a way to group Apps together.
* When registering the App you will be asked for some information, including the redirect URL and any scopes you will be requesting.
    * Redirect URL (if development): `https://portal-dev.slateci.io/authcallback`
    * Redirect URL (if production): `https://portal.slateci.io/authcallback`
* After creating your App the **Client ID** and **Client Secret** can be copied into this project in the following place:
    * `ansible/inventory/<dev|prod>/hosts.yml` in the `slate_portal_client_id` and `slate_portal_client_secret` key values.

### Select a SLATE API Admin Account

* Ask the team for the API token of an appropriate admin account.
* Once in hand the token can be copied to the following place in this project:
    * `ansible/inventory/<dev|prod>/hosts.yml` in the `slate_api_token` key value.

## Finalize `ssh-config`

Add the remaining setting values to `ansible/inventory/<dev|prod>/ssh-config.yml` in this project.
* Both `IdentityFile` setting values: `/path/to/id_rsa_slate`
* `slate-portal-host`'s `HostName` setting value:
  * Development: `portal-dev.slateci.io`
  * Production: `portal.slateci.io`
* Both `User` setting values: `yourslateuser`

At this point `ansible/inventory/<dev|prod>/ssh-config.yml` should resemble:

```text
## Global Settings
StrictHostKeyChecking no
UserKnownHostsFile /dev/null

### The External SLATE Bastion host
Host slate-bastion-host
  HostName bastion.slateci.net
  IdentitiesOnly yes
  IdentityFile <your-value>
  Port 22
  User <your-value>

### The internal SLATE Portal host
Host slate-portal-host
  HostName <your-value>
  IdentityFile <your-value>
  Port 22
  ProxyJump slate-bastion-host
  User <your-value>
```

## Finalize `hosts.yml`

Add the remaining key-values to `ansible/inventory/<dev|prod>/hosts.yml` in this project.

Development:
* `ansible_ssh_common_args: '-F /project-path/ansible/inventory/dev/ssh-config'`
* `slate_api_endpoint: 'https://api-dev.slateci.io:18080'`

Production:
* `ansible_ssh_common_args: '-F /project-path/ansible/inventory/prod/ssh-config'`
* `slate_api_endpoint: 'https://api.slateci.io:443'`

At this point `ansible/inventory/<dev|prod>/hosts.yml` should resemble:

```yaml
all:
  hosts:
    portal:
      ansible_host: slate-portal-host
  vars:
    ansible_ssh_common_args: '-F <your-value>'
    slate_api_endpoint: '<your-value>'
    slate_api_token: "<your-value>"
    slate_hostname: '<your-value>'
    slate_portal_client_id: '<your-value>'
    slate_portal_client_secret: '<your-value>'
```

## Build and Run Portal

Activate the Conda environment and verify Ansible can see the host(s):

```shell
[your@localmachine]$ conda activate chpc-ansible
(chpc-ansible) [your@localmachine]$ ansible all -m ping -i ./ansible/inventory/dev/hosts.yml
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
(chpc-ansible) [your@localmachine]$ ansible all -a "/bin/ls -al /root" -i ./ansible/inventory/dev/hosts.yml -u <yourslateuser> --become --become-user root
portal | CHANGED | rc=0 >>
total 40
dr-xr-x---.  3 root root  170 Feb 28 22:27 .
dr-xr-xr-x. 17 root root  224 Jul  3  2017 ..
-rw-------.  1 root root 6913 Jul  3  2017 file.ext
...
```

**Note:** If you receive an error during these steps, double-check the contents of your `ssh-config` file, paying special attention to the `IdentityFile`, `User`, and `HostName` setting values.

Finally, verbosely run the Ansible playbook itself:

```shell
(chpc-ansible) [your@localmachine]$ ansible-playbook -v -i ./ansible/inventory/<dev|prod>/hosts.yml --extra-vars "@./ansible/secrets.yml" ./ansible/playbook.yml
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
