#!/bin/bash
# Bootstrap script to install system packages
echo "Updating system packages"
apt-get update


echo "Installing Git"
apt-get install git -y


echo "Installing Python"
apt-get install python python-pip python-virtualenv python-dev python-nose -y


echo "Installing Nginx"
apt-get install nginx -y


echo "Installing Gunicorn"
apt-get install gunicorn -y

echo "Installing RabbitMQ"
apt-get install rabbitmq-server -y


echo "Activating RabbitMQ Management Plugin"
rabbitmq-plugins enable rabbitmq_management


echo "Restarting RabbitMQ"
service rabbitmq-server restart


echo "Installing Postgresql"
apt-get install postgresql postgresql-contrib -y



echo "And some other bits that I don't know what they do..."
apt-get install -y build-essential libssl-dev libffi-dev libpq-dev
