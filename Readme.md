# Consul Firewall configuration tool

This tool includes a bash script for creating the inventory and a playbook to call the ansible role.

## Usage

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
