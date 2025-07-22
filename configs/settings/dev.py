from datetime import timedelta

from configs.settings.base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',  # استفاده از PostgreSQL
        'NAME': 'SeoTools',  # نام دیتابیس PostgreSQL
        'USER': 'postgres',  # نام کاربری دیتابیس
        'PASSWORD': 'rezabhm:1290',  # رمز عبور دیتابیس
        'HOST': 'localhost',  # آدرس سرور دیتابیس (localhost برای دیتابیس محلی)
        'PORT': '5432',  # پورت دیتابیس (پورت پیش‌فرض PostgreSQL)
    }
}


# Cors headers Config
CORS_ALLOW_ALL_ORIGINS = True

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

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Example: React frontend
    # "https://your-production-domain.com",
]

# JWT Authentication Configs
SIMPLE_JWT = {

    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),  # Set token expiration time
    'REFRESH_TOKEN_LIFETIME': timedelta(days=5),     # Refresh token expiration time

}

# # Redis Configs
# CACHES = {
#     "default": {
#         "BACKEND": "django_redis.cache.RedisCache",
#         "LOCATION": "redis://127.0.0.1:6379/1",
#         "OPTIONS": {
#             "CLIENT_CLASS": "django_redis.client.DefaultClient",
#         }
#     }
# }