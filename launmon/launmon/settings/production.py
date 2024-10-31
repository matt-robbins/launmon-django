from launmon.settings.base import *
from launmon.settings.secrets import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["localhost",
                 "launmon.ddns.net",
                 "www.spintracker.app",
                 "laundry.375lincoln.nyc",
                 "laundry-dev.375lincoln.nyc"]


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'launmon',
        'USER': 'launy',
        'PASSWORD': 'monny',
        'HOST': 'localhost',
        'PORT': 5432
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379",
    }
}

# Email
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

# Cookies
ACCOUNT_SESSION_REMEMBER = True
SESSION_COOKIE_AGE = 4000000000

STATIC_ROOT = "/var/www/launmon-django/static"