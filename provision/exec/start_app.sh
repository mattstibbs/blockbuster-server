#!/bin/bash
cd ~/production/blockbuster-server/
/root/production/blockbuster-server/env/bin/gunicorn blockbuster:app -w 2 -b localhost:8000 --reload