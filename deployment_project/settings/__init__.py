from .base import *

import os
from decouple import config

if config('DJANGO_SETTINGS_MODULE', default='development') == 'production':
    from .production import *
else:
    from .development import *