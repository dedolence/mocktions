import os
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

DEBUG = False
ALLOWED_HOSTS = ['mocktions.herokuapp.com']

# Sentry setup
SENTRY_DSN = os.environ['SENTRY_DSN']
sentry_sdk.init(
    # remove this for production
    #dsn='https://323a1597f3134297b9051cfc882dae88:bb813f44456e4e4a811d9442abdd1f1b@o1239642.ingest.sentry.io/6391230',
    dsn=SENTRY_DSN,
    integrations=[DjangoIntegration()]
)