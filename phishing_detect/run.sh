#!/bin/bash
set -e

# Run passed commands directly
if [ $# -gt 0 ]; then
    exec "$@"
fi

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn..."

exec gunicorn phishing_detect.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3