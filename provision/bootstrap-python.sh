#!/bin/bash
# Bootstrap script to configure python working environment

echo "Creating Install Directory"
mkdir /opt/blockbuster

echo "Creating a Python Virtualenv"
virtualenv /opt/blockbuster/env
source /opt/blockbuster/env/bin/activate


echo "Installing Python module dependencies from requirements.txt"
/opt/blockbuster/env/bin/pip install -r /vagrant/requirements.txt
