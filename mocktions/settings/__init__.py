import os
from .base import *

try:
    os.environ.get('ENVIRONMENT')
    from .prod import *
except KeyError:
    from .dev import *