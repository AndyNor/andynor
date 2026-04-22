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

# 4. Restart services with status feedback
echo "--- Restarting Gunicorn ---"
sudo systemctl restart gunicorn
if [ $? -eq 0 ]; then
    echo "SUCCESS: Gunicorn restarted."
    # Show the active status line specifically
    sudo systemctl status gunicorn | grep "Active:"
else
    echo "ERROR: Gunicorn failed to restart!"
fi

echo "--- Restarting Nginx ---"
sudo systemctl restart nginx
if [ $? -eq 0 ]; then
    echo "SUCCESS: Nginx restarted."
    sudo systemctl status nginx | grep "Active:"
else
    echo "ERROR: Nginx failed to restart!"
fi

# 5. Ensure scripts remain executable
chmod +x synch.sh
chmod +x restart.sh
chmod +x backup.sh
chmod +x start.sh

echo "--- DEPLOYMENT COMPLETE ---"