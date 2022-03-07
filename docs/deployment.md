# Deployment with Ansible Playbook

The Ansible playbook and an appropriate inventory file are used for server deployments.

## Requirements

Use the installation instructions found in [Local Ansible Playbook Development with Vagrant](vagrant.md) to install:
* Ansible
* Vagrant
* Miniconda3

## Create Ansible Inventory File

Each environment should have a separate inventory file to prevent unexpected deployments. Use the appropriate template below to create your inventory file.

For more information on Ansible inventories see:
* [How to build your inventory](https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html)
* [ansible.builtin.yaml – Uses a specific YAML file as an inventory source.](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/yaml_inventory.html)

### Development

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

### Production

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

## Build and Run Portal

Activate the Conda environment and run the Ansible playbook specifying a user with sudo privileges on the host(s).

```shell
[your@localmachine]$ conda activate chpc-ansible
(chpc-ansible) [your@localmachine]$ ansible-playbook -i ./ansible/inventory/<dev|prod>/hosts.yml -u <sudo-user> ./ansible/playbook.yml
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
