import os
import sentry_sdk
import dj_database_url
from sentry_sdk.integrations.django import DjangoIntegration
from .base import BASE_DIR


ALLOWED_HOSTS = ['mocktions.herokuapp.com']

# Sentry setup
try:
    SENTRY_DSN = os.environ['SENTRY_DSN']
    sentry_sdk.init(
        # remove this for production
        #dsn='https://323a1597f3134297b9051cfc882dae88:bb813f44456e4e4a811d9442abdd1f1b@o1239642.ingest.sentry.io/6391230',
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()]
    )
except KeyError:
    pass

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases
try:
    DATABASE_URL = os.environ['DATABASE_URL']
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
        }
    }
    db_from_env = dj_database_url.config(conn_max_age=500)
    DATABASES['default'].update(db_from_env)
except KeyError:
    pass

# Static storage
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'