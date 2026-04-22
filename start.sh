#!/bin/bash
# Move to the project directory
cd /home/django/django_project/andynor

# Activate the virtual environment
source /home/django/django_project/python3.13-env/bin/activate

# Print the versions so you know it worked
echo "Environment Activated!"
python --version
pip --version