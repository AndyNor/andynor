#!/bin/sh
cd ~/webapps/django225/myproject/

git fetch
git reset --hard origin/master

python3.7 -m pip install -r requirements.txt
python3.7 manage.py makemigrations
python3.7 manage.py migrate
python3.7 manage.py collectstatic --noinput

~/webapps/django225/apache2/bin/restart
