import os
from .base import *

# evaluate as strings to avoid eval()
if os.environ['PRODUCTION'] == "False":
    from .dev import *
else:
    from .prod import *