#!/bin/bash

/usr/bin/tmux new-session -s bb-workers -d 'cd /vagrant && export C_FORCE_ROOT="true" && /home/vagrant/env/bin/celery -A
blockbuster_celery.bb_celery worker -c 1 -l info -n worker10' \; split-window -h -d 'cd /vagrant && export
C_FORCE_ROOT="true" && sleep 5 && /home/vagrant/env/bin/celery -A blockbuster_celery.bb_celery worker -c 1 -l info -n
worker11' \; attach