#!/bin/bash

/usr/bin/tmux new-session -s bb-server -d 'cd /vagrant && /home/vagrant/env/bin/python run.py -v' \; attach