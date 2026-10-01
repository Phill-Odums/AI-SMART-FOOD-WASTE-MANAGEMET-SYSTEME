#!/usr/bin/env bash
set -e

echo "==> Running database migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "==> Collecting static files..."
python manage.py collectstatic --noinput

echo "==> Ensuring superuser Admin exists..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
from apps.accounts.models import UserProfile

User = get_user_model()
username = 'Admin'
password = 'Admin123'
email = 'admin@example.com'

user, created = User.objects.get_or_create(
    username=username,
    defaults={'email': email, 'is_staff': True, 'is_superuser': True}
)
if created:
    user.set_password(password)
    user.save()
    UserProfile.objects.get_or_create(user=user, defaults={'role': 'admin'})
    print(f'Superuser {username} created successfully.')
else:
    user.set_password(password)
    user.is_staff = True
    user.is_superuser = True
    user.save()
    UserProfile.objects.get_or_create(user=user, defaults={'role': 'admin'})
    print(f'Superuser {username} updated.')
"

echo "==> Starting Gunicorn production server on port ${PORT:-8000}..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers ${WEB_CONCURRENCY:-3} \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -

