#!/usr/bin/env bash
# Render har deploy par yeh script run karta hai
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
