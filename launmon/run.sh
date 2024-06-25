#!/bin/bash

settings="launmon.settings"
echo $#

if [ $# -ge 1 ]; then
    settings=$1
fi

echo $settings

trap 'pkill -P $$; exit' SIGINT SIGTERM

./manage.py rundaemon --settings=$settings &
./manage.py runpusher --settings=$settings &
./manage.py runserver --settings=$settings &
python ./ws_server.py &

wait