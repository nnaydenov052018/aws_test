#!/bin/bash

## Upgrade system
yum upgrade -y

## Installing docker
rm -f /etc/yum.repos.d/docker-ce.repo

echo "* Install Prerequisites ..."
yum update -y

echo "* Install Docker ..."
yum makecache fast
amazon-linux-extras install docker

echo "* Start Docker ..."
systemctl enable docker
systemctl start docker

# Add ec2-user into docker group
usermod -a -G docker ec2-user

# Verify docker
docker info

## Install git client and  python-pip
yum install git -y
yum install python3 -y

## Install docker-compose
pip3 install docker-compose

## Create gmail-cli tool directories
mkdir -p ~/Gmail_Tool && chmod 700 ~/Gmail_Tool -R
mkdir -p ~/mailbox && chmod 700 ~/mailbox -R

## Create project directory and checkout docker project
mkdir -p ~/projects
cd ~/projects && git clone https://github.com/nnaydenov052018/aws_test.git

## Run gmail-cli docker container
cd ~/projects/aws_test/docker-compose && docker-compose -f ./docker-compose.yml up -d
 