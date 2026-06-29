# Logging Rules

## Logging configuration

```python
# config/settings/base.py
import os

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        },
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
    },
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json" if os.environ.get("LOG_FORMAT") == "json" else "verbose",
        },
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": os.environ.get("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
        "apps": {
            "handlers": ["console"],
            "level": "DEBUG" if os.environ.get("DEBUG") else "INFO",
            "propagate": False,
        },
    },
}
```

## Logger usage

```python
# In every module that logs
import logging

logger = logging.getLogger(__name__)


def my_function():
    logger.info("Processing request", extra={"user_id": user.id, "action": "share"})
    try:
        result = do_work()
        logger.info("Request completed", extra={"result_id": result.id})
        return result
    except Exception as e:
        logger.exception("Request failed: %s", e)
        raise
```

## What to log

| Level | When | Example |
|---|---|---|
| `DEBUG` | Internal state, variable values | Cache hit/miss, query parameters |
| `INFO` | Normal operations, business events | User logged in, idea created, email sent |
| `WARNING` | Recoverable issues, deprecated usage | Retry triggered, fallback used, rate limit approaching |
| `ERROR` | Failures that need attention | External API failed, payment webhook rejected |
| `CRITICAL` | System-level failures | Database unreachable, Celery worker down |

## What NOT to log

- **Never log secrets**: JWTs, API keys, passwords, tokens, `SECRET_KEY`
- **Never log PII in plaintext**: emails, phone numbers, addresses (mask or hash)
- **Never log full request/response bodies in production** (too large, may contain secrets)
- **Never use `print()` for logging** — use `logger.info()` or `logger.debug()`
- **Never log inside tight loops** — aggregate first, log once

## Structured logging with context

```python
# apps/<app>/middleware.py
import logging
import uuid

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:
    """Attach request ID and log request/response."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        logger.info(
            "Request started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.path,
                "user_id": getattr(request.user, "id", None),
            },
        )

        response = self.get_response(request)

        logger.info(
            "Request completed",
            extra={
                "request_id": request_id,
                "status_code": response.status_code,
            },
        )

        response["X-Request-ID"] = request_id
        return response
```

## Logging in Celery tasks

```python
@shared_task(bind=True)
def my_task(self, data_id: int):
    logger.info(
        "Task started",
        extra={
            "task_id": self.request.id,
            "data_id": data_id,
        },
    )
    # ... work ...
    logger.info("Task completed", extra={"task_id": self.request.id})
```

## Sentry integration

```python
# config/settings/prod.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration

sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    integrations=[
        DjangoIntegration(),
        CeleryIntegration(),
    ],
    traces_sample_rate=0.1,
    send_default_pii=False,
    environment=os.environ.get("ENVIRONMENT", "production"),
)
```
