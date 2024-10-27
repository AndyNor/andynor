#!/bin/sh
cd /home/django/django_project/andynor

git fetch
git reset --hard origin/master

python3 -m pip install --upgrade pip
pip install -r requirements.txt
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py collectstatic --noinput

systemctl restart gunicorn
systemctl restart nginx

chmod +x synch.sh
chmod +x restart.sh
chmod +x backup.sh
