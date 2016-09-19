#!/bin/bash

python manage.py migrate
python manage.py initadmin
#python manage.py collectstatic --noinput  # need to set STATIC_ROOT first
python manage.py runserver 0.0.0.0:8000
