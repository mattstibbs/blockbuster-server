#!/usr/bin/env bash
# Bootstrap script to seed the project with upstart files

echo "Seeding project with upstart files..."
cd /etc/init/

if [ -e "blockbuster.conf" ]
then
  echo "NO CHANGE - blockbuster.conf file already present"
else
	cp /opt/blockbuster/blockbuster-server/provision/init/blockbuster.conf /etc/init/blockbuster.conf
  	echo "Seeding project using blockbuster.conf upstart file"
fi

if [ -e "blockbuster-celery.conf" ]
then
  echo "NO CHANGE - blockbuster-celery.conf file already present"
else
	cp /opt/blockbuster/blockbuster-server/provision/init/blockbuster-celery.conf /etc/init/blockbuster-celery.conf
  	echo "Seeding project using blockbuster-celery.conf upstart file"
fi