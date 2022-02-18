# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.require_version ">= 2.0.0"

# Environmental Variables:
ENV['BRIDGED_ADAPTER'] = "enp7s0"
ENV['HOSTNAME'] = 'portal.slateci.local'

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure("2") do |config|

  # The most common configuration options are documented and commented below.
  # For a complete reference, please see the online documentation at
  # https://docs.vagrantup.com.

  # Necessary for mounts (see https://www.puppeteers.net/blog/fixing-vagrant-vbguest-for-the-centos-7-base-box/).
  config.vbguest.installer_options = { allow_kernel_upgrade: true }

  # Specify the Vagrant Box, version, and update check:
  config.vm.box = "centos/7"
  config.vm.box_version = "2004.01"
  config.vm.box_check_update = "false"

  # Customize the hostname:
  config.vm.hostname = ENV['HOSTNAME']

  # Create a bridged network adaptor.
  config.vm.network "public_network", bridge: ENV['BRIDGED_ADAPTER']

  # VirtualBox Provider
  config.vm.provider "virtualbox" do |vb|
    # Customize the number of CPUs on the VM:
    vb.cpus = 2

    # Customize the network drivers:
    vb.default_nic_type = "virtio"

    # Display the VirtualBox GUI when booting the machine:
    vb.gui = false

    # Customize the amount of memory on the VM:
    vb.memory = 2048

    # Customize the name that appears in the VirtualBox GUI:
    vb.name = ENV['HOSTNAME']
  end

  # Run Ansible from the Vagrant host:
  config.vm.provision "ansible", run:"always" do |ansible|
    ansible.extra_vars = {
      slate_debug: true,
      slate_hostname: ENV['HOSTNAME']
    }
    ansible.host_key_checking = false
    ansible.playbook = "./ansible/playbook.yml"
    ansible.verbose = "v"
  end


end
