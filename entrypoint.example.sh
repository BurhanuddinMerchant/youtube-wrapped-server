#!/bin/bash

export AWS_ACCESS_KEY_ID=
export AWS_SECRET_ACCESS_KEY=
export AWS_STORAGE_BUCKET_NAME=
export YOUTUBE_API_KEY=
export DJANGO_SECRET_KEY=
export DEBUG=
export EMAIL_HOST_USER=
export EMAIL_HOST_PASSWORD=
export BASE_HOST_URL=
export RECAPTCHA_SECRET_KEY=
export RECAPTCHA_SITE_KEY=

python manage.py makemigrations
python manage.py migrate
python manage.py runserver 0.0.0.0:8000