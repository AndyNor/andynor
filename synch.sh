#!/bin/sh
cd /home/django/django_project/andynor

git fetch
git reset --hard origin/master

pip install -r requirements.txt
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py collectstatic --noinput

systemctl restart gunicorn
systemctl restart nginx

chmod +x synch.sh
chmod +x restart.sh
chmod +x sbanken_api.sh
