#!/bin/bash

## Upgrade system
sudo yum upgrade -y

## Installing docker
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

## Install git client and  python-pip
sudo yum install git -y
sudo yum install python3 -y

## Install docker-compose
sudo pip3 install docker-compose

## Create gmail-cli tool directories
mkdir -p ~/Gmail_Tool && chmod 700 ~/Gmail_Tool -R
mkdir -p ~/mailbox && chmod 700 ~/mailbox -R

## Create project directory and checkout docker project
mkdir -p ~/projects
cd ~/projects && git clone https://github.com/nnaydenov052018/aws_test.git

## Run gmail-cli docker container
cd ~/projects/aws_test/docker-compose && docker-compose -f ./docker-compose.yml up -d
 