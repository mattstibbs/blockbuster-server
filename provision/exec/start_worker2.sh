#!/bin/bash
export C_FORCE_ROOT="true"
/usr/local/bin/celery -A blockbuster_celery.bb_celery worker -l info -n worker2 -c 1
