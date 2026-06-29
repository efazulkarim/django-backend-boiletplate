# Error Handling Rules

## API error response shape

Every error response must be JSON with the correct status code. Never return `200 OK` for an error.

### DRF default (preferred for most cases)

```json
HTTP 400
{ "field_name": ["This field is required."] }
```

### Structured error (for cross-field or service-level errors)

```json
HTTP 400
{
  "error": "Validation failed",
  "detail": {
    "email": ["This field is required."],
    "password": ["Must be at least 8 characters."]
  }
}
```

### Simple error (for auth, permission, not found)

```json
HTTP 401
{ "detail": "Invalid token." }
```

## Status code rules

| Situation | Code | Body |
|---|---|---|
| Missing/invalid auth | 401 | `{ "detail": "Authentication credentials were not provided." }` |
| Insufficient permissions | 403 | `{ "detail": "You do not have permission." }` |
| Resource not found | 404 | `{ "detail": "Not found." }` |
| Validation error | 400 | Field-keyed dict |
| Rate limited | 429 | `{ "detail": "Request was throttled." }` |
| Server error | 500 | `{ "detail": "Internal server error." }` |

## Exception handling pattern

```python
# apps/<app>/exceptions.py
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """DRF exception handler that ensures consistent error shape."""
    response = exception_handler(exc, context)

    if response is None:
        # Unhandled exception — log it, return 500
        logger.exception("Unhandled exception in %s", context.get("view", "unknown"))
        return Response(
            {"detail": "Internal server error."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return response
```

```python
# config/settings/base.py
REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "apps.api.exceptions.custom_exception_handler",
}
```

## Service-layer exceptions

```python
# apps/<app>/exceptions.py
class AppError(Exception):
    """Base exception for service-layer errors."""
    def __init__(self, message: str, code: str = "app_error", status_code: int = 400):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppError):
    def __init__(self, resource: str, identifier: str | int):
        super().__init__(
            message=f"{resource} with id '{identifier}' not found",
            code="not_found",
            status_code=404,
        )


class PermissionDeniedError(AppError):
    def __init__(self, message: str = "You do not have permission."):
        super().__init__(message=message, code="permission_denied", status_code=403)


class ConflictError(AppError):
    def __init__(self, message: str):
        super().__init__(message=message, code="conflict", status_code=409)
```

## View-level error handling

```python
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from apps.api.exceptions import AppError


class IdeaViewSet(ModelViewSet):
    @action(detail=True, methods=["post"])
    def share(self, request, pk=None):
        idea = self.get_object()
        try:
            result = IdeaService.share_idea(idea, request.user)
            return Response(result, status=status.HTTP_200_OK)
        except PermissionDeniedError as e:
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ConflictError as e:
            return Response({"detail": str(e)}, status=status.HTTP_409_CONFLICT)
```

## What NOT to do

- Never return `Response({"error": ...}, status=200)` — errors must have error status codes
- Never catch bare `Exception` and return a generic message without logging
- Never expose internal error details (stack traces, SQL errors) to the client
- Never use `assert` for input validation — use serializer validation or explicit checks
