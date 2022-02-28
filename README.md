# SLATE Portal

This repository contains:
* The web Portal to the [SLATE platform](https://slateci.io/) and uses [globus](https://docs.globus.org/) in order to authenticate users with the [Auth API](https://docs.globus.org/api/auth/).
* The [Ansible playbook](https://docs.ansible.com/ansible/latest/user_guide/playbooks_intro.html) used for server deployments.

## Table of Contents

* [Local Development with Containers](#local-development-with-containers)
* [Local Ansible Playbook Development with Vagrant](#local-ansible-playbook-development-with-vagrant)
* [Deployment with Ansible Playbook](#deployment-with-ansible-playbook)

## Local Development with Containers

A containerized Portal will provide a near live-preview developer experience.

### Requirements

#### Choose a Container Engine

Install **ONE** of the following for developing, managing, and running OCI containers on your system:

* [Docker](https://docs.docker.com/get-docker/)
* [Podman](https://podman.io/)

For the sake of simplicity this page will focus on Docker (see [the podman docs](https://docs.podman.io/en/latest/Commands.html) for alternate syntax).

#### Create `portal.conf`

Copy `instance/portal.conf.tmpl` to the following place of this project: `instance/portal.conf`. Complete the steps described below to modify properties and finalize this file.

#### Register a globus Application

> **_IMPORTANT:_** Before proceeding ask the team about existing globus registrations as some localdev, development, and production projects and applications already exist.

Create your own App registration for use in the Portal.

* Visit the [Globus Developer Pages](https://developers.globus.org) to register an App.
* If this is your first time visiting the Developer Pages you will be asked to create a Project. A Project is a way to group Apps together.
* When registering the App you will be asked for some information, including the redirect URL and any scopes you will be requesting.
  * Redirect URL: `http://localhost:5000/authcallback`
* After creating your App the **Client ID** and **Client Secret** can be copied into this project in the following place:
    * `instance/portal.conf` in the `PORTAL_CLIENT_ID` and `PORTAL_CLIENT_SECRET` properties.

#### Select a SLATE API Admin Account

Portal communicates with a SLATE API server via an admin account.

* Specify the SLATE API server in the following place of this project:
  * `instance/portal.conf` in the `SLATE_API_ENDPOINT` property.
* Ask the team for the API token of an appropriate admin account.
* Once in hand the token can be copied into this project in the following place:
  * `instance/portal.conf` in the `SLATE_API_TOKEN` property.

### Finalize `portal.conf`

At this point `instance/portal.conf` should resemble:

```properties
#------------------------------------------------
# Default MRDP application configuration settings
#------------------------------------------------

SERVER_NAME = '<your-value>'
DEBUG = True
SLATE_WEBSITE_LOGFILE = '/var/log/uwsgi/portal.log'

SECRET_KEY = '=.DKwWzDd}!3}6yeAY+WTF#W:zt5msTI7]2`o}Y!ziU!#CYD+;T9JpW$ud|5C_3'

# globus:
PORTAL_CLIENT_ID = '<your-value>'
PORTAL_CLIENT_SECRET = '<your-value>'
GLOBUS_AUTH_LOGOUT_URI = 'https://auth.globus.org/v2/web/logout'

# SLATE API:
SLATE_API_TOKEN = '<your-value>'
SLATE_API_ENDPOINT = '<your-value>'
```

### Build and Run Portal

Build the Docker image:

```shell
docker build -f Dockerfile -t slate-portal:local .
```

Running the image will create a new tagged container and start Portal:

```shell
[your@localmachine]$ docker run -it -v ${PWD}:/etc/slate/slate-website-python -p 5000:5000 slate-portal:local
 * Serving Flask app 'portal' (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: on
 * Running on all addresses.
   WARNING: This is a development server. Do not use it in a production deployment.
 * Running on http://172.17.0.2:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 123-456-789
```

Point your browser to `http://localhost:5000`, make changes, and enjoy a live-preview experience.

### Teardown

Quit the Flask app (`CTRL + C`) and prune the now-stopped Docker container to release system resources:

```shell
docker container prune
```

For more information on pruning stopped containers see [docker container prune](https://docs.docker.com/engine/reference/commandline/container_prune/)

## Local Ansible Playbook Development with Vagrant

A local Oracle VirtualBox VM-hosted Portal will provide a near production developer experience as well as the ability to test the Ansible playbook used for server deployments.

### Requirements

#### Install Ansible

This project uses Miniconda3 (or Conda) to create a Python interpreter with Ansible and other necessary dependencies.

1. Navigate to the [Miniconda3 downloads page]() to download and install Conda on your system.
2. Execute the following to create the `chpc-ansible` Conda environment on your system:

   ```shell
   conda env create -f ansible/environment.yml
   ```
   
3. Activate the Conda environment and check that Ansible is properly installed:

   ```shell
   [your@localmachine]$ conda activate chpc-ansible
   (chpc-ansible) [your@localmachine]$ ansible --version
     ansible [core 2.12.1]
     config file = None
     configured module search path = ['/home/you/.ansible/plugins/modules', '/usr/share/ansible/plugins/modules']
     ansible python module location = /home/you/miniconda3/envs/chpc-ansible/lib/python3.10/site-packages/ansible
     ansible collection location = /home/you/.ansible/collections:/usr/share/ansible/collections
     executable location = /home/you/miniconda3/envs/chpc-ansible/bin/ansible
     python version = 3.10.2 | packaged by conda-forge | (main, Jan 14 2022, 08:02:09) [GCC 9.4.0]
     jinja version = 3.0.3
     libyaml = True
   ```

4. Use the following resources as references for any Ansible-related questions:
   * [Ansible Quickstart Guide](https://docs.ansible.com/ansible/2.9/user_guide/quickstart.html)
   * [Ansible Concepts](https://docs.ansible.com/ansible/2.9/user_guide/basic_concepts.html)
   * [Ansible: Module Index](https://docs.ansible.com/ansible/2.9/modules/modules_by_category.html)

#### Install Oracle VirtualBox

Oracle VirtualBox is the virtualization provider-of-choice for this project. Download and install VirtualBox using the instructions provided on the [VirtualBox downloads page](https://www.virtualbox.org/wiki/Downloads).

#### Install Vagrant

[Hashicorp Vagrant](https://www.vagrantup.com/) is a tool that "leverages a declarative configuration file which describes all your software requirements, packages, operating system configuration, users, and more". The configuration for this project is described in the `Vagrantfile`.

Download and install Vagrant using the instructions provided on the [Vagrant downloads page](https://www.vagrantup.com/downloads). Once Vagrant is installed execute the following commands on your system to install plugins necessary for this project:

* VirtualBox Guest Additions Plugin:

  ```shell
  vagrant plugin install vagrant-vbguest
  ```

* Hosts Updater Plugin:

  ```shell
  vagrant plugin install vagrant-hostsupdater
  ```

Optionally install the Vagrant `bash` autocompletion (recommended for Linux users):

```shell
vagrant autocomplete install --bash
```

#### Create `secrets.yml`

Copy `ansible/secrets.yml.tmpl` to the following place of this project: `ansible/secrets.yml`. Complete the steps described below to modify placeholder key-value pairs and finalize this file.

#### Register a globus Application

> **_IMPORTANT:_** Before proceeding ask the team about existing globus registrations as some localdev, development, and production projects and applications already exist.

Create your own App registration for use in the Portal.

* Visit the [Globus Developer Pages](https://developers.globus.org) to register an App.
* If this is your first time visiting the Developer Pages you will be asked to create a Project. A Project is a way to group Apps together.
* When registering the App you will be asked for some information, including the redirect URL and any scopes you will be requesting.
    * Redirect URL: `https://portal.vagrant.test/authcallback`
* After creating your App the **Client ID** and **Client Secret** can be copied into this project in the following place:
    * `ansible/secrets.yml` in the `slate_portal_client_id` and `slate_portal_client_secret` key values.

#### Select a SLATE API Admin Account

Portal communicates with a SLATE API server via an admin account.

* The `Vagrantfile` will always lock the SLATE API server to development:
    
  ```text
  ...
  ansible.extra_vars = {
    ...
    slate_api_endpoint: 'https://api-dev.slateci.io:18080',
    ...
  }
  ```

  This will prevent unwanted changes from making their way unexpectedly to Production.

* Ask the team for the API token of an appropriate admin account.
* Once in hand the token can be copied to the following place of this project:
    * `ansible/secrets.yml` in the `slate_api_token` key value.

### Finalize `secrets.yml`

At this point `ansible/secrets.yml` should resemble:

```yaml
---
slate_api_token: "<your-value>"
slate_portal_client_id: "<your-value>"
slate_portal_client_secret: "<your-value>"
```

### Build and Run Portal

Activate the Conda environment, create the virtual machine, and run Ansible providing sudo credentials when prompted:

```shell
[your@localmachine]$ conda activate chpc-ansible
(chpc-ansible) [your@localmachine]$ vagrant up
==> default: [vagrant-hostsupdater] Checking for host entries
[sudo] password for you: []
...
==> default: Running provisioner: ansible...
    default: Running ansible-playbook...
PYTHONUNBUFFERED=1 ANSIBLE_FORCE_COLOR=true ANSIBLE_HOST_KEY_CHECKING=false
ANSIBLE_SSH_ARGS='-o UserKnownHostsFile=/dev/null -o IdentitiesOnly=yes -o ControlMaster=auto -o ControlPersist=60s'
ansible-playbook --connection=ssh --timeout=30 --limit="default"
--inventory-file=/home/you/path/.vagrant/provisioners/ansible/inventory
--extra-vars=\{\"slate_api_endpoint\":\"https://api-dev.slateci.io:18080\",
\"slate_api_token\":\"<your-value>\",\"slate_debug\":true,\"slate_git_version\":\"<git-branch-name>\",
\"slate_hostname\":\"portal.vagrant.test\",\"slate_portal_client_id\":\"<your-value\",
\"slate_portal_client_secret\":\"<your-value>"\} -v ./ansible/playbook.yml
No config file found; using defaults

PLAY [all] *********************************************************************
...
PLAY RECAP *********************************************************************
default                    : ok=43   changed=8    unreachable=0    failed=0    skipped=6    rescued=0    ignored=0
```

Point your browser to `https://portal.vagrant.test`, make changes, and enjoy a near-production experience.

#### The Details

* Test any local changes made to the Ansible playbook on a currently running VM by executing `vagrant provision` one or more times.
* Any local changes made to the Python source itself requires an extra step and must be committed to the currently checked out branch before executing `vagrant provision`.
  * Reasoning: One of the Ansible tasks defined in the playbook requires a source branch to clone. 
* Rudimentary name resolution is provided by changes to your system's hosts file via the `vagrant-hostsupdater` plugin.
* Vagrant creates its own Ansible inventory file (see [Ansible and Vagrant](https://www.vagrantup.com/docs/provisioning/ansible_intro) for more information).

### Teardown

The [Vagrant CLI](https://www.vagrantup.com/docs/cli) is documented at great length but here are some of the highlights:

| Command           | Description                                                                                                                                                                                                                                                                           |
|-------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `vagrant halt`    | This command shuts down the running machine Vagrant is managing and allowing `vagrant up` to start the machine again.                                                                                                                                                                 |
| `vagrant destroy` | This command stops the running machine Vagrant is managing and destroys all resources that were created during the machine creation process. After running this command, your computer should be left at a clean state, as if you never created the guest machine in the first place. |

Finally, deactivate the Conda environment:

```shell
(chpc-ansible) [your@localmachine]$ conda deactivate
[your@localmachine]$
```

## Deployment with Ansible Playbook

The Ansible playbook and an appropriate inventory file are used for server deployments.

### Requirements

Use the installation instructions found in [Local Ansible Playbook Development with Vagrant](#local-ansible-playbook-development-with-vagrant) to install:
* Ansible
* Vagrant
* Miniconda3

### Create Ansible Inventory File

Each environment should have a separate inventory file to prevent unexpected deployments. Use the appropriate template below to create your inventory file.

For more information on Ansible inventories see:
* [How to build your inventory](https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html)
* [ansible.builtin.yaml – Uses a specific YAML file as an inventory source.](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/yaml_inventory.html)

#### Development

Create `hosts.yml` in the following place of this project `ansible/inventory/dev/hosts.yml` and replace the placeholder text with actual values.

```yaml
all:
  hosts:
    portal:
      ansible_host: <public-ipv4>
  vars:
    # If a SSH Bastion server is involved modify and use:
    #ansible_ssh_common_args: '-J you@bastion.slateci.net -i /path/to/id_rsa_slate'
    slate_api_endpoint: 'https://api-dev.slateci.io:18080'
    slate_api_token: 'XXXX'
    slate_hostname: 'portal-dev.slate.io'
    slate_portal_client_id: 'XXXX'
    slate_portal_client_secret: 'XXXX'
```

#### Production

Create `hosts.yml` in the following place of this project `ansible/inventory/prod/hosts.yml` and replace the placeholder text with actual values.

```yaml
all:
  hosts:
    portal:
      ansible_host: <public-ipv4>
  vars:
    # If a SSH Bastion server is involved modify and use:
    #ansible_ssh_common_args: '-J you@bastion.slateci.net -i /path/to/id_rsa_slate'
    slate_api_endpoint: 'https://api.slateci.io:443'
    slate_api_token: 'XXXX'
    slate_hostname: 'portal.slate.io'
    slate_portal_client_id: 'XXXX'
    slate_portal_client_secret: 'XXXX'
```

### Build and Run Portal

Activate the Conda environment and run the Ansible playbook specifying a user with sudo privileges on the host(s).

```shell
[your@localmachine]$ conda activate chpc-ansible
(chpc-ansible) [your@localmachine]$ ansible-playbook -i ./ansible/inventory/<dev|prod>/hosts.yml -u <sudo-user> ./ansible/playbook.yml
...
...
```

### Teardown

Currently, this is a manual process. At some point the playbook will be expanded to help uninstall Portal and return the host to a clean state.

On your local machine deactivate the Conda environment:

```shell
(chpc-ansible) [your@localmachine]$ conda deactivate
[your@localmachine]$
```
