#!/usr/bin/env bash
set -e

echo "==> Running database migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "==> Collecting static files..."
python manage.py collectstatic --noinput

echo "==> Starting Gunicorn production server on port ${PORT:-8000}..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers ${WEB_CONCURRENCY:-3} \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -

