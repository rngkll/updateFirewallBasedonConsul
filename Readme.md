# Consul Firewall configuration tool

## Development

Using vagrant for testing environment:

1. Initialize development environment with `vagrant up`.
1. Access the VM using `vagrant ssh`
1. `cd /mnt/bootstrap`
1. run the script with: `python3 configureFirewall.py`

## Usage

```
configureFirewall.py -s test -z internal -u http://localhost:8500/v1/catalog/service/wireguard
```

options:

* -s --stage
* -z --zone
* -u --url
