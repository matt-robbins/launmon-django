from launmon.settings.base import *
from launmon.settings.secrets import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'tfamt$5c@(_efm_v9#7-5uwwx7e&*d=h52+*s8+*l22kyzbi&z'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["localhost",
                 "launmon.ddns.net",
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
EMAIL_HOST = "smtp.porkbun.com"
EMAIL_HOST_USER = "admin@375lincoln.nyc"
EMAIL_FROM_USER = "admin@375lincoln.nyc"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

DEFAULT_FROM_EMAIL = "admin@375lincoln.nyc"
# Cookies
ACCOUNT_SESSION_REMEMBER = True
SESSION_COOKIE_AGE = 4000000000

STATIC_ROOT = "/var/www/launmon-django"