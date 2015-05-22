# Application Server Setup

###
* nginx
* gunicorn
* python
* rabbitmq


## Configure the Blockbuster processes to automatically start
The rc.local script is executed at the end of each multiuser runlevel.
Open the script:
    
    sudo nano /etc/rc.local
    
Add lines to start new tmux sessions for the main app and 2 celery async worker processes.
Example (you will need to alter paths to suit etc.):

    /usr/bin/tmux new-session -s app -d 'cd ~/production/blockbuster-server && bash start_app.sh'
    sleep 5
    /usr/bin/tmux new-session -s wrk1 -d 'cd ~/production/blockbuster-server && bash start_worker1.sh'
    sleep 5
    /usr/bin/tmux new-session -s wrk2 -d 'cd ~/production/blockbuster-server && bash start_worker2.sh'
    

