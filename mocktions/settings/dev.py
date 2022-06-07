import os
from .base import BASE_DIR
from dotenv import load_dotenv
load_dotenv()


ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases
"""
    Postgres settings
    User: postgres
    Password: kPgHqw2g

    Django (user) settings:
    Username: django
    Password: R6ZL4gPW
"""

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ['DB_NAME'],
        'USER': os.environ['DB_USER'],
        'PASSWORD': os.environ['DB_PASSWORD'],
        'HOST': 'localhost',
        'PORT': '5432'
    }
}

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