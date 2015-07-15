#!/bin/bash
cd /opt/blockbuster/blockbuster-server/
/opt/blockbuster/env/bin/gunicorn blockbuster:app -w 2 -b localhost:8000 --reload
