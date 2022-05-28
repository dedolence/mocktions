import os
from .base import *
"""
    To facilitate easy development, the settings are broken down into three files:
    base.py: common settings belonging to both production and development environments.
    dev.py: settings for development; can be used via "heroku local" or "manage.py runserver"
    prod.py: settings specifically for deployment.

    If the environment variable "ENVIRONMENT" is immediately accessible, then it must
    be a production environment. Although the default case is to load development settings,
    for security's sake dev.py still checks to see if the variable is declared as "DEPLOYMENT."
    That being said, later I would like to switch it around so it defaults to production.
"""
try:
    os.environ.get('ENVIRONMENT')
    from .prod import *
except KeyError:
    from .dev import *