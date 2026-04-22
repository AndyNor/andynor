#!/bin/sh

#sudo visudo -->
#django ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart gunicorn, /usr/bin/systemctl restart nginx
sudo systemctl restart gunicorn
sudo systemctl restart nginx
