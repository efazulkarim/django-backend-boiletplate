---
name: security-and-hardening
description: Security middleware, headers, rate limits, request sanitization, and input validation for my-api-project. Use when modifying middleware or hardening a route.
---

# Security & hardening — `my-api-project`

## Middleware (in `config/settings/base.py`, order matters)

```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",       # outermost — HTTPS, HSTS
    "corsheaders.middleware.CorsMiddleware",               # CORS headers
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",       # allauth
    # Custom middleware:
    "apps.core.middleware.JSONRequestMiddleware",          # request logging
]
```

## Security headers (Django built-in)

```python
# config/settings/prod.py — when DEBUG=False
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
```

## Rate limiting

Use `django-ratelimit` or DRF throttling:

```python
# config/settings/base.py — REST_FRAMEWORK
REST_FRAMEWORK = {
    # ...
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "60/minute",
        "user": "60/minute",
    },
}
```

Auth routes should have tighter limits: `10/minute`.

## Request sanitization (custom middleware)

```python
# apps/core/middleware.py
import json
import logging

logger = logging.getLogger(__name__)


class JSONRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.body:
            try:
                request.json_body = json.loads(request.body)
            except (json.JSONDecodeError, UnicodeDecodeError):
                request.json_body = None
        response = self.get_response(request)
        return response
```

## Input validation (DRF serializers)

- Free-text fields MUST have `max_length`:
  - `name`: 200
  - `description`: 5000
  - `answer text`: 10000
- Email: `EmailField`.
- IDs from path: typed as `int` (DRF returns 400 on non-int).
- Enums: use `ChoiceField` or `CharField(choices=...)`.

```python
from rest_framework import serializers


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ["id", "name", "description"]
        extra_kwargs = {
            "name": {"max_length": 200},
            "description": {"max_length": 5000},
        }
```

## CORS

```python
# config/settings/base.py
CORS_ALLOW_ALL_ORIGINS = False  # True only in dev
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",    # frontend dev
    "https://yourdomain.com",   # production
]
CORS_ALLOW_CREDENTIALS = True
```

Production `CORS_ALLOWED_ORIGINS` is the deployed frontend URL only. Never `*` with credentials.

## Logging

Use Python's `logging` module. Never log:
- Authorization headers
- Tokens
- Passwords (plain or hashed)
- API keys
- Webhook signatures
- Full request body on auth routes

```python
import logging
logger = logging.getLogger(__name__)
logger.info("User %s created resource %s", user.pk, resource.pk)
```

## Don't do

- Don't roll your own auth. Use DRF's built-in auth or allauth.
- Don't disable HTTPS in production.
- Don't add `CORS_ALLOW_ALL_ORIGINS = True` in production.
- Don't return stack traces in prod responses (`DEBUG=False`).
- Don't use `@csrf_exempt` on API views without a reason.
