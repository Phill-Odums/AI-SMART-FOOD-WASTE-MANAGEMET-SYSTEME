"""
Django settings for the Smart Food-Waste Reduction Framework.

Built for: South-East Nigeria QSR Operations
Stack: Django REST Framework + Swagger UI (drf-spectacular)
"""

import os
from pathlib import Path
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-fw-dev-key-change-in-production-9x$2m!k&3'
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = [host.strip() for host in os.environ.get('DJANGO_ALLOWED_HOSTS', '*').split(',') if host.strip()]

# Automatic hostname configuration on Render
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME and RENDER_EXTERNAL_HOSTNAME not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# HTTPS / Reverse Proxy Header (Render terminates SSL at its proxy)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Trusted origins for CSRF protection
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get(
        'CSRF_TRUSTED_ORIGINS',
        'https://*.onrender.com,http://localhost:8000,http://127.0.0.1:8000'
    ).split(',')
    if origin.strip()
]


# ---------------------------------------------------------------------------
# Application definition
# ---------------------------------------------------------------------------

INSTALLED_APPS = [
    # Django core
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'rest_framework',
    'rest_framework.authtoken',
    'drf_spectacular',
    'django_filters',
    'corsheaders',

    # Project apps
    'apps.organization',
    'apps.accounts',
    'apps.menu',
    'apps.inventory',
    'apps.waste',
    'apps.calendar_context',
    'apps.sales',
    'apps.forecasting',
    'apps.analytics',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
        conn_max_age=600,
        conn_health_checks=True,
    )
}


# ---------------------------------------------------------------------------
# Password validation
# ---------------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ---------------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------------

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Lagos'   # WAT (West Africa Time) for South-East Nigeria
USE_I18N = True
USE_TZ = True


# ---------------------------------------------------------------------------
# Static files (CSS, JavaScript, Images) & WhiteNoise Production Storage
# ---------------------------------------------------------------------------

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

# Don't crash collectstatic if third-party packages have missing file references
WHITENOISE_MANIFEST_STRICT = False


# ---------------------------------------------------------------------------
# Default primary key field type
# ---------------------------------------------------------------------------

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ---------------------------------------------------------------------------
# Django REST Framework
# ---------------------------------------------------------------------------

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',

    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],

    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],

    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],

    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 25,

    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
}


# ---------------------------------------------------------------------------
# drf-spectacular (Swagger UI / OpenAPI 3.0)
# ---------------------------------------------------------------------------

SPECTACULAR_SETTINGS = {
    'TITLE': 'Smart Food-Waste Reduction Framework API',
    'DESCRIPTION': (
        'Integrated AI-powered food waste management platform for Quick Service '
        'Restaurants (QSRs) in South-East Nigeria. Combines Amazon Chronos-Bolt '
        'and Google TimesFM ensemble forecasting with local contextual features '
        '(Igbo market days, civil service paydays, weather patterns) to optimize '
        'kitchen preparation and minimize edible food waste.'
    ),
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,

    # Organize endpoints by Django app
    'TAGS': [
        {'name': 'Auth & Accounts', 'description': 'User authentication, registration, and profile management.'},
        {'name': 'Organization', 'description': 'Restaurant chains and branch outlet management.'},
        {'name': 'Menu & Recipes', 'description': 'Menu items, ingredients, and Recipe Bill of Materials (BOM).'},
        {'name': 'Inventory', 'description': 'Raw ingredient stock tracking with FEFO expiry management.'},
        {'name': 'Waste Tracking', 'description': 'Edible food waste logging across operational stages.'},
        {'name': 'Local Calendar', 'description': 'South-East Nigeria contextual calendar (market days, paydays, weather).'},
        {'name': 'Sales Records', 'description': 'Historical POS sales data feeding the forecasting engine.'},
        {'name': 'AI Forecasting', 'description': 'Chronos-Bolt + TimesFM ensemble demand prediction and kitchen prep targets.'},
        {'name': 'Analytics', 'description': 'Menu engineering matrix, pilot KPIs, and branch benchmarking.'},
    ],

    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': '/api/v1/',
}


# ---------------------------------------------------------------------------
# CORS (Cross-Origin Resource Sharing) — for PWA tablet clients
# ---------------------------------------------------------------------------

CORS_ALLOW_ALL_ORIGINS = DEBUG  # Only in development
CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',') if not DEBUG else []

