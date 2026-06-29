"""Custom middleware for request logging and tracing."""
import logging
import uuid

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:
    """Attach a request ID and log request/response cycle.

    Adds X-Request-ID header to every response for trace correlation.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
        request.request_id = request_id

        logger.info(
            'request_started',
            extra={
                'request_id': request_id,
                'method': request.method,
                'path': request.path,
                'user_id': getattr(request.user, 'id', None) if hasattr(request, 'user') else None,
            },
        )

        response = self.get_response(request)

        logger.info(
            'request_completed',
            extra={
                'request_id': request_id,
                'status_code': response.status_code,
            },
        )

        response['X-Request-ID'] = request_id
        return response
