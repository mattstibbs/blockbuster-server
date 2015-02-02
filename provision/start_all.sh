#!/bin/bash

/usr/bin/tmux new-session -s bb-all -d 'cd /vagrant && /home/vagrant/env/bin/gunicorn blockbuster:app -b localhost:8000
--reload' \; split-window -d 'cd /vagrant && export C_FORCE_ROOT="true" && /home/vagrant/env/bin/celery -A
blockbuster_celery.bb_celery worker -l info -n worker1 -c 1' \; attach
