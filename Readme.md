# Consul Firewall configuration tool

This tool includes a bash script for creating the inventory and a playbook to call the ansible role.

## Usage

As a firts step consul data is needed, fetch the consul data catalog and create an ansible invetory based on it.

To create a ansible inventory a json parsing script was created, this script is designed for test environment data.

script: `createTestInventory.sh`

This is designed to create y "dynamic inventory" based on the consul data.

Use the dynamic inventory with the available playbook.

```
ansible-playbook -i dynamicInventory/test site.yml --check
```
Note: remove `--check` to apply changes.

# Ansible roles

## Ansible requirements
```
ansible-galaxy collection install ansible.posix
```

## Ansible role development

Ansible role develped using molecule.
```
pip install ansible-core ansible-lint molecule "molecule[docker]"
```

Running the role with molecule.
```
molecule create
molecule converge
molecule test
```
