"""Settings package."""
import os
import sys

# Determine which settings to use
env = os.environ.get('DJANGO_SETTINGS_MODULE', 'config.settings.dev')

if 'test' in sys.argv:
    from .test import *
elif 'prod' in env:
    from .prod import *
else:
    from .dev import *
