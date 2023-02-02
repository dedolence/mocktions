"""
    Production settings!

    Any development settings should be in local_settings, where they will 
    overwrite anything set here.
"""

import dj_database_url, environ, os, sentry_sdk
from pathlib import Path
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk import set_level
from django.contrib.messages import constants as messages

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# set up django-environ to read environment variables
env = environ.Env(
    DEBUG=(bool, False)
)

environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')

ALLOWED_HOSTS = ['mocktions.fly.dev', '0.0.0.0']

CSRF_TRUSTED_ORIGINS = ['https://mocktions.fly.dev']

# Sentry initialization to log errors/security issues
set_level("info")
sentry_sdk.init(
    dsn="https://36e84563aec64d1a96f99b86840f4984@o4503955967377408.ingest.sentry.io/4503955970260992",
    integrations=[
        DjangoIntegration(),
    ],

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0,

    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True
)

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'base',
    'accounts',
    'images',
    'storages',
    'whitenoise.runserver_nostatic',
    'django_cleanup.apps.CleanupConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.common.BrokenLinkEmailsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mocktions.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR,],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # this was for my custom context processor, not yet in use
                #'global_context_processors.global_variables',
            ],
        },
    },
]


# Used to match message tags to their corresponding Bootstrap alert classes
MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'error',
}

WSGI_APPLICATION = 'mocktions.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(conn_max_age=600)
}


# Default user model

AUTH_USER_MODEL = 'accounts.User'


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

# USE_LOCAL:
# A flag for where static files are stored, either locally or by CDN,
# True/False respectively.
#
# Note to self:
# .env variables are always strings. VARIABLE=True evaluates as the 
# string, "True", not a boolean.
USE_LOCAL: bool = env('USE_LOCAL') == 'True'  

if USE_LOCAL:
    STATIC_URL = '/staticfiles/'
    # STATIC_ROOT defines where staticfiles will be copied and then served from.
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
    DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
    MEDIA_URL = '/mediafiles/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles/tests')
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        },
        "django-backblaze-b2": {
            'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
            'LOCATION': 'django_backblaze_b2_cache_table',
        }
    }

    BACKBLAZE_CONFIG = {
        "application_key_id": os.getenv("B2_KEY_ID"),
        "application_key": os.getenv("B2_APPLICATION_KEY"),
        "bucket": "mocktions-pub"
    }
    STATICFILES_STORAGE = 'django_backblaze_b2.BackblazeB2Storage'
    STATIC_URL = "https://s3.us-west-004.backblazeb2.com/static/"

    DEFAULT_FILE_STORAGE = 'django_backblaze_b2.PublicStorage'
    MEDIA_URL = "https://s3.us-west-004.backblazeb2.com/media/"


# In the presence of the local_settings module, they will override
# anything here. So, these are all production settings by default.
# Obviously, local_settings should be omitted from version control.
try:
    from .local_settings import *
    print("-------------\nLocal development settings loading!\n-------------")
except ImportError:
    pass