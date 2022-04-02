# Consul Firewall configuration tool

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
