#!/bin/sh

uwsgi --chdir=/home/launy/code/launmon-django/launmon \
    --plugins python3\
    --module=launmon.wsgi:application \
    --env DJANGO_SETTINGS_MODULE=launmon.settings_prod \
    --master --pidfile=/tmp/launmon-master.pid \
    --socket=/tmp/launmon-django.sock \
    --chmod-socket=666 \
    --uid=www-data \
    --gid=www-data \
    --processes=2 \
    --harakiri=20 \
    --max-requests=5000 \
    --vacuum \
    --home=/home/launy/code/launmon-django/env \
#    --daemonize=/var/log/uwsgi/launmon.log
#    --uid=1000 --gid=2000 \
