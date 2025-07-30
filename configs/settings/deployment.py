import os
from datetime import timedelta
from configs.settings.base import *

# Do not enable debug mode in production
DEBUG = False

# Get allowed hosts from .env and split them by comma
ALLOWED_HOSTS = os.environ.get('PRODUCTION_ALLOWED_HOSTS', '').split(',')

# Database configuration using environment variables
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('PRODUCTION_DB_NAME'),
        'USER': os.environ.get('PRODUCTION_DB_USER'),
        'PASSWORD': os.environ.get('PRODUCTION_DB_PASSWORD'),
        'HOST': os.environ.get('PRODUCTION_DB_HOST'),
        'PORT': os.environ.get('PRODUCTION_DB_PORT'),
    }
}

# CORS Configuration
CORS_ALLOW_ALL_ORIGINS = os.environ.get('PRODUCTION_CORS_ALLOW_ALL_ORIGINS', 'False') == 'True'

CORS_ALLOWED_ORIGINS = os.environ.get('PRODUCTION_CORS_ALLOWED_ORIGINS', '').split(',')

CORS_ALLOW_HEADERS = [
    "accept",
    "authorization",
    "content-type",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

CORS_ALLOW_METHODS = [
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "OPTIONS",
]

# JWT token settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=5),
}
