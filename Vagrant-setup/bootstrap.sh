#!/bin/sh -e

# Update package list and upgrade all packages
apt-get update
apt-get -y upgrade

apt-get -y install firewalld
systemctl enable firewalld
systemctl start firewalld
