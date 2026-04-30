@echo off
cd /d C:\Users\andre\envs\andynor_py313_django512\Scripts
call activate.bat
cd /d C:\Users\andre\Documents\GitHub\andynor

pip install -r requirements.txt && ^
python manage.py makemigrations && ^
python manage.py migrate

cmd /k
