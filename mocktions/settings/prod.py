import os
import sentry_sdk
import dj_database_url
from sentry_sdk.integrations.django import DjangoIntegration
from .base import BASE_DIR


SECRET_KEY = os.environ['SECRET_KEY']
DEBUG = False
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

# Static files (CSS, JavaScript, Images)
# S3 settings
AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
AWS_STORAGE_BUCKET_NAME = os.environ['AWS_BUCKET_NAME']
AWS_REGION = os.environ['AWS_REGION']
AWS_S3_CUSTOM_DOMAIN = '{bucket}.s3.{region}.amazonaws.com'.format(
    bucket=AWS_STORAGE_BUCKET_NAME, region=AWS_REGION)
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age:86400',
}
AWS_LOCATION = 'static'

# Django settings
STATIC_URL = '{domain}/{location}/'.format(
    domain=AWS_S3_CUSTOM_DOMAIN,
    location=AWS_LOCATION
)
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
