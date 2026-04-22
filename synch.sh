#!/bin/sh
# 1. Navigate to project root
cd /home/django/django_project/andynor

# 2. Pull latest code
git fetch
git reset --hard origin/master

# 3. Use the NEW 3.13 virtual environment path for all commands
VENV_PYTHON="/home/django/django_project/python3.13-env/bin/python"

# Upgrade pip inside the venv
$VENV_PYTHON -m pip install --upgrade pip

# Install requirements into the venv
$VENV_PYTHON -m pip install -r requirements.txt

# Run Django commands using the venv python
$VENV_PYTHON manage.py makemigrations
$VENV_PYTHON manage.py migrate
$VENV_PYTHON manage.py collectstatic --noinput

# 4. Restart services (using your NOPASSWD sudo rules)
sudo systemctl restart gunicorn
sudo systemctl restart nginx

# 5. Ensure scripts remain executable
chmod +x synch.sh
chmod +x restart.sh
chmod +x backup.sh
chmod +x start.sh