"""Custom exceptions and DRF exception handler."""
import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Service-layer exceptions
# ---------------------------------------------------------------------------


class AppError(Exception):
    """Base exception for service-layer errors."""

    def __init__(
        self,
        message: str,
        code: str = 'app_error',
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppError):
    """Resource not found."""

    def __init__(self, resource: str, identifier: str | int):
        super().__init__(
            message=f'{resource} with id "{identifier}" not found',
            code='not_found',
            status_code=status.HTTP_404_NOT_FOUND,
        )


class PermissionDeniedError(AppError):
    """Insufficient permissions."""

    def __init__(self, message: str = 'You do not have permission.'):
        super().__init__(
            message=message,
            code='permission_denied',
            status_code=status.HTTP_403_FORBIDDEN,
        )


class ConflictError(AppError):
    """Resource conflict (e.g. duplicate)."""

    def __init__(self, message: str):
        super().__init__(
            message=message,
            code='conflict',
            status_code=status.HTTP_409_CONFLICT,
        )


class ValidationError(AppError):
    """Service-layer validation error."""

    def __init__(self, message: str, detail: dict | None = None):
        self.detail = detail or {}
        super().__init__(
            message=message,
            code='validation_error',
            status_code=status.HTTP_400_BAD_REQUEST,
        )


# ---------------------------------------------------------------------------
# DRF exception handler
# ---------------------------------------------------------------------------


def custom_exception_handler(exc, context):
    """DRF exception handler that ensures consistent error shape.

    - Handles AppError subclasses with structured JSON.
    - Falls back to DRF default for standard exceptions.
    - Returns 500 for unhandled exceptions.
    """
    # Handle our custom exceptions
    if isinstance(exc, AppError):
        data = {
            'error': exc.message,
            'code': exc.code,
        }
        if isinstance(exc, ValidationError) and exc.detail:
            data['detail'] = exc.detail
        return Response(data, status=exc.status_code)

    # Let DRF handle its own exceptions (400, 401, 403, 404, etc.)
    response = exception_handler(exc, context)

    if response is not None:
        return response

    # Unhandled exception — log and return 500
    view = context.get('view', None)
    view_name = view.__class__.__name__ if view else 'unknown'
    logger.exception('Unhandled exception in %s', view_name)

    return Response(
        {'detail': 'Internal server error.'},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
