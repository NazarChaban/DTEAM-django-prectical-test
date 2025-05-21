#!/bin/bash
set -e

# Add PYTHONPATH
export PYTHONPATH="/app/CVProject"

# Set DJANGO_SETTINGS_MODULE
export DJANGO_SETTINGS_MODULE="CVProject.settings"

# Migrations
echo "Running migrations"
python manage.py migrate --noinput

# Create superuser if it doesn't exist and CREATE_SUPERUSER is True
echo "Checking for existing superuser"
python ../scripts/create_superuser.py

# Load initial data if LOAD_INITIAL_DATA is True
if [ "$LOAD_INITIAL_DATA" = "True" ] || [ "$LOAD_INITIAL_DATA" = "true" ]; then
    echo "Loading initial data"
    python manage.py loaddata sample_data.json
fi

# Start debug server if DJANGO_DEBUG is True, otherwise start gunicorn
if [ "$DJANGO_DEBUG" = "True" ] || [ "$DJANGO_DEBUG" = "true" ]; then
    echo "Running development server"
    exec python manage.py runserver 0.0.0.0:8000
else
    echo "Starting server"
    exec gunicorn CVProject.wsgi:application --bind 0.0.0.0:8000
fi
