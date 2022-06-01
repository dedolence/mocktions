import os
from dotenv import load_dotenv
load_dotenv()

# double check that this is a deployment environment by checking the local .env
try:
    environment = os.environ['ENVIRONMENT']
except KeyError:
    environment = None

if environment == 'DEVELOPMENT':
    DEBUG = True
else:
    DEBUG = False

SECRET_KEY = os.environ['SECRET_KEY']
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