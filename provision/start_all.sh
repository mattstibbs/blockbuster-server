#!/bin/bash

/usr/bin/tmux new-session -s blockbuster-server -d 'cd /opt/blockbuster/blockbuster-server &&
/opt/blockbuster/env/bin/gunicorn
blockbuster:app -b
localhost:8000 --reload' \; split-window -d 'cd /opt/blockbuster/blockbuster-server && export C_FORCE_ROOT="true" &&
/opt/blockbuster/env/bin/celery -A
blockbuster_celery.bb_celery worker -c 1 -l info -n worker1' \; attach
