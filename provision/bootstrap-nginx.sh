#!/bin/sh
# Configure the Nginx server

echo "Removing default site configuration for Nginx"
rm /etc/nginx/sites-enabled/default

echo "Seeding Nginx site configuration for blockbuster-server"
cd /etc/nginx/sites-enabled

if [ -e "blockbuster-server" ]
then
  echo "NO CHANGE - blockbuster-server site file already present"
else
	cp /opt/blockbuster/blockbuster-server/provision/nginx/blockbuster-server /etc/nginx/sites-available/
  	echo "Copying blockbuster-server site config into sites-available"
  	ln -s /etc/nginx/sites-available/blockbuster-server /etc/nginx/sites-enabled/blockbuster-server
fi

echo "Restarting Nginx"
service nginx reload