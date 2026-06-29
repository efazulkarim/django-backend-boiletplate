---
name: django-settings
description: Django settings patterns for my-api-project. Use when extending config/settings/ — environment-specific overrides, env var handling, and the rule to never read os.environ outside settings files.
---

# Django settings — `my-api-project`

## Files in scope

- `config/settings/base.py` — shared settings across all environments
- `config/settings/dev.py` — development overrides
- `config/settings/prod.py` — production overrides
- `config/settings/test.py` — test overrides (SQLite in-memory, eager Celery)
- `.env.example` — template (tracked)
- `.env` — local dev (gitignored)

## Settings inheritance

```text
base.py          → shared across all environments
  ├── dev.py     → DEBUG=True, CORS_ALLOW_ALL_ORIGINS=True, console email
  ├── prod.py    → DEBUG=False, SMTP email, S3 storage, strict security
  └── test.py    → SQLite in-memory, MD5 password hasher, eager Celery
```

`config/settings/__init__.py` auto-selects based on environment.

## Template: adding a new env var

```python
# config/settings/base.py
import os

# At the top of base.py, after imports:
MY_NEW_SERVICE_API_KEY = os.environ.get("MY_NEW_SERVICE_API_KEY", "")
MY_NEW_SERVICE_TIMEOUT = int(os.environ.get("MY_NEW_SERVICE_TIMEOUT", "30"))
```

## Template: adding a new Django app

```python
# config/settings/base.py — INSTALLED_APPS
INSTALLED_APPS = [
    # Django core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "rest_framework",
    "rest_framework.authtoken",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "corsheaders",
    "channels",
    "drf_spectacular",
    # Local apps
    "apps.core",
    "apps.users",
    "apps.api",
    # New app here:
    "apps.<new_app>",
]
```

## Template: adding a new REST_FRAMEWORK setting

```python
# config/settings/base.py — REST_FRAMEWORK
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    # Add new settings here:
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}
```

## Conventions

- **All env access goes through `config/settings/`**. Never `os.environ` outside settings files.
- **Required vs optional**: `os.environ["KEY"]` for required (raises at startup), `os.environ.get("KEY", default)` for optional.
- **Type conversion**: `int()`, `bool()`, etc. at the call site. Django settings are plain Python.
- **Backwards compat**: when adding a new env key, give it a default. When renaming, keep the old key reading.
- **Immutability**: settings are loaded once at startup. Don't mutate them at runtime.
- **Secrets**: `SECRET_KEY`, `DB_PASSWORD`, API keys — from env only, never hardcoded, never logged.
- **Production security**: `DEBUG=False`, `SECURE_SSL_REDIRECT=True`, `SESSION_COOKIE_SECURE=True`, `CSRF_COOKIE_SECURE=True`.

## Adding a new service key

1. Add to `base.py` with `os.environ.get("KEY", "")` (optional) or `os.environ["KEY"]` (required).
2. Add to `.env.example` with a comment.
3. Consume in the service file: `from django.conf import settings; settings.MY_KEY`.
4. If the key is a secret, never log it, never return it in a response, never include in error messages.

## Don't do

- Don't read `os.environ["..."]` in a view, service, or model file.
- Don't mutate settings at runtime; treat them as immutable.
- Don't import `dev` settings in production code.
- Don't put computed values in settings; compute at the call site.
- Don't commit `.env` — it's gitignored. Use `.env.example` for templates.
