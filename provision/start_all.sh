#!/bin/bash

/usr/bin/tmux new-session -s bb-all -d 'cd /vagrant && /home/vagrant/env/bin/gunicorn blockbuster:app -b localhost:8000
--reload' \; split-window -d 'cd /vagrant && export C_FORCE_ROOT="true" && /home/vagrant/env/bin/celery -A blockbuster_celery.bb_celery worker -c 1 -l info -n worker1' \; attach


/usr/bin/tmux new-session -s app -d 'cd /opt/blockbuster/blockbuster-server/provision/exec && bash start_app.sh'
sleep 5
/usr/bin/tmux new-session -s wrk1 -d 'cd /opt/blockbuster/blockbuster-server && bash start_worker1.sh'
sleep 5
/usr/bin/tmux new-session -s wrk2 -d 'cd /opt/blockbuster/blockbuster-server && bash start_worker2.sh'
