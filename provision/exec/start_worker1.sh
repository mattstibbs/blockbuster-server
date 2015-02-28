#!/bin/bash
export C_FORCE_ROOT="true"
/usr/local/bin/celery -A blockbuster_celery.bb_celery worker -l info -n worker1 -c 1