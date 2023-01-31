import dj_database_url

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '0.0.0.0']

DATABASES = {
    'default': dj_database_url.config(conn_max_age=600)
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
