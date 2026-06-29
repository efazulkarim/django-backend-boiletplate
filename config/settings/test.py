"""Test settings."""
from .dev import *  # noqa: F401,F403

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

# Disable password validators in tests
AUTH_PASSWORD_VALIDATORS = []

# Disable email during tests
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Disable SSL redirect and security features in tests
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Celery broker for tests (use in-memory)
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
