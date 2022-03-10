# Local Ansible Playbook Development with Vagrant

A local Oracle VirtualBox VM-hosted Portal will provide a near production developer experience as well as the ability to test the Ansible playbook used for server deployments.

## Requirements

### Install Ansible

This project uses Miniconda3 (or Conda) to create a Python interpreter with Ansible and other necessary dependencies.

1. Navigate to the [Miniconda3 downloads page](https://docs.conda.io/en/latest/miniconda.html) to download and install Conda on your system.
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
    * [Intro to playbooks](https://docs.ansible.com/ansible/latest/user_guide/playbooks_intro.html)
    * [Ansible: Module Index](https://docs.ansible.com/ansible/2.9/modules/modules_by_category.html)

### Install Oracle VirtualBox

Oracle VirtualBox is the virtualization provider-of-choice for this project. Download and install VirtualBox using the instructions provided on the [VirtualBox downloads page](https://www.virtualbox.org/wiki/Downloads).

### Install Vagrant

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

### Create `secrets.yml`

Copy `ansible/secrets.yml.tmpl` to the following place in this project: `ansible/secrets.yml`. Complete the steps described below to modify placeholder key-value pairs and finalize this file.

### Register a globus Application

> **_IMPORTANT:_** Before proceeding ask the team about existing globus registrations as some localdev projects and applications already exist.

Create your own App registration for use in the Portal.

* Visit the [Globus Developer Pages](https://developers.globus.org) to register an App.
* If this is your first time visiting the Developer Pages you will be asked to create a Project. A Project is a way to group Apps together.
* When registering the App you will be asked for some information, including the redirect URL and any scopes you will be requesting.
    * Redirect URL: `https://portal.vagrant.test/authcallback`
* After creating your App the **Client ID** and **Client Secret** can be copied into this project in the following place:
    * `ansible/secrets.yml` in the `slate_portal_client_id` and `slate_portal_client_secret` key values.

### Select a SLATE API Admin Account

Portal communicates with a SLATE API server via an admin account.

* Vagrant will always lock the SLATE API server to `https://api-dev.slateci.io:18080` (see ["All" Ansible Group variables](ansible/group_vars/all.yml)). This will prevent unwanted changes from making their way unexpectedly to Production.
* Ask the team for the API token of an appropriate admin account.
* Once in hand the token can be copied to the following place in this project:
    * `ansible/secrets.yml` in the `slate_api_token` key value.

## Finalize `secrets.yml`

At this point `ansible/secrets.yml` should resemble:

```yaml
---
slate_api_token: "SAMPLE"
slate_portal_client_id: "SAMPLE"
slate_portal_client_secret: "SAMPLE"
```

## Build and Run Portal

Activate the Conda environment, create the virtual machine, and run Vagrant providing sudo credentials when prompted:

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

### The Details

* Test any local changes made to the Ansible playbook source on a currently running VM by executing `vagrant provision` one or more times.
* Any local changes made to the Python source instead requires an extra step and must be committed to the currently checked out branch before executing `vagrant provision`.
    * **Reasoning:** One of the Ansible tasks defined in the playbook requires a source branch to clone.
* Rudimentary name resolution is provided by changes to your system's `hosts` file via the `vagrant-hostsupdater` plugin.
* Vagrant creates its own Ansible inventory file and makes use of `ansible/group_vars/all.yml` (see [Ansible and Vagrant](https://www.vagrantup.com/docs/provisioning/ansible_intro) for more information).

## Teardown

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
