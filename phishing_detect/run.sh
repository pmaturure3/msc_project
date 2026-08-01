#!/bin/bash
set -e

echo "Running database migrations..."
python manage.py makemigrations
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn..."
exec gunicorn your_project_name.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3