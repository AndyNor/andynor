!/bin/bash

# local backup of database. no need to backup site or config

tar -zcvf /home/django/django_project/andynor/backup/sqlite_`date +%F_%H:%M:%S`.tar.gz /home/django/django_project/andynor/db.sqlite3

# remove files older than 3 days

#find /home/django/django_project/andynor/backup/ -type d -mtime +3 -exec ls {}\;


