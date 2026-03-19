"""Test settings."""
from .dev import *

# Override for testing
DEBUG = False
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Speed up password hashing in tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable email during tests
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Celery broker for tests (use in-memory)
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
