
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '0.0.0.0']
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
    "django-backblaze-b2": {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'django_backblaze_b2_cache_table',
    }
}
# Logging in production is handled by Sentry
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'Simple_Format': {
            'format': '{levelname}: {message}',
            'style': '{'
        },
        'verbose': {
            'format': '({levelname}) Raised at {asctime} from {module}:\n"{message}"\nFull path: {pathname}\n',
            'style': '{',
        }
    },

    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },

    'filters': {},

    'loggers': {
        'fly_stream': {
            'handlers': ['console'],
            'level': 'INFO',
        }
    },
}
