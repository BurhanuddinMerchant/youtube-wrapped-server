#!/bin/bash

python manage.py makemigrations
python manage.py migrate
./create_superuser.sh
python manage.py runserver 0.0.0.0:8000