#!/bin/bash
# Bootstrap script to configure python working environment

echo "Creating a Python Virtualenv"
virtualenv /home/vagrant/env
source /home/vagrant/env/bin/activate


echo "Installing Python module dependencies from requirements.txt"
/home/vagrant/env/bin/pip install -r /vagrant/requirements.txt