#!/bin/bash
# Bootstrap script to seed the project with config files

echo "Seeding project with config files if they don't already exist..."
cd /vagrant/blockbuster

if [ -e "config.py" ]
then
  echo "NO CHANGE - config.py file already present"
else
	cp /vagrant/blockbuster/example_config_files/example_config.py /vagrant/blockbuster/config.py
  	echo "Seeding project using example config.py file"
fi

if [ -e "config_services.py" ]
then
  echo "NO CHANGE - config_services.py file already present"
else
  cp /vagrant/blockbuster/example_config_files/example_config_services.py /vagrant/blockbuster/config_services.py
  echo "Seeding project using example config_services.py file"
fi

if [ -e "config_celery.py" ]
then
  echo "NO CHANGE - config_celery.py file already present"
else
  cp /vagrant/blockbuster/example_config_files/example_config_celery.py /vagrant/blockbuster/config_celery.py
  echo "Seeding project using example config_celery.py file"
fi