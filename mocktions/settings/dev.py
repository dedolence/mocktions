from dotenv import load_dotenv
load_dotenv()

DEBUG = True
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
import os
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'mocktions',
        'USER': 'django',
        'PASSWORD': 'R6ZL4gPW',
        'HOST': 'localhost',
        'PORT': '5432'
    }
}