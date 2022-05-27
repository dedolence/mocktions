import os
from .base import *
if not os.environ['PRODUCTION']:
    from .dev import *
else:
    from .prod import *