#!/bin/bash

sudo rm -f /etc/yum.repos.d/docker-ce.repo

echo "* Install Prerequisites ..."
sudo yum update -y

echo "* Install Docker ..."
sudo yum makecache fast
sudo amazon-linux-extras install docker

echo "* Start Docker ..."
sudo systemctl enable docker
sudo systemctl start docker

# Add ec2-user into docker group
sudo usermod -a -G docker ec2-user

# Verify docker
sudo docker info
