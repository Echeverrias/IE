#!/bin/sh

set -e

/wait
python manage.py makemigrations
python manage.py migrate
python manage.py initadmin root root@ie.com root
python manage.py initdb


exec "$@"