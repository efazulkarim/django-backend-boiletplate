"""Example Celery tasks for the core app.

Celery is for fire-and-forget and scheduled tasks.
For durable/stateful workflows, use Temporal (see temporal_app/).
"""
import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_notification_email(self, user_id: int, subject: str, body: str):
    """Send a notification email to a user.

    Uses Celery retry with exponential backoff on failure.
    In production, replace the print with actual email sending.
    """
    logger.info('send_notification_started', extra={'task_id': self.request.id, 'user_id': user_id})

    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.get(pk=user_id)

        # TODO: Replace with actual email sending (e.g. django.core.mail.send_mail)
        logger.info(
            'send_notification_completed',
            extra={'task_id': self.request.id, 'user_id': user_id, 'email': user.email},
        )
        return {'status': 'sent', 'user_id': user_id, 'email': user.email}

    except Exception as exc:
        logger.warning(
            'send_notification_retry',
            extra={'task_id': self.request.id, 'user_id': user_id, 'error': str(exc)},
        )
        raise self.retry(exc=exc)


@shared_task
def cleanup_expired_tokens():
    """Remove expired auth tokens. Schedule via Celery Beat.

    Add to CELERY_BEAT_SCHEDULE in settings:
        'cleanup-expired-tokens': {
            'task': 'apps.core.tasks.cleanup_expired_tokens',
            'schedule': crontab(hour=3, minute=0),  # daily at 3am
        }
    """
    from django.utils import timezone
    from rest_framework.authtoken.models import Token

    threshold = timezone.now() - timezone.timedelta(days=30)
    expired = Token.objects.filter(created__lt=threshold)
    count = expired.count()
    expired.delete()
    logger.info('cleanup_expired_tokens', extra={'deleted': count})
    return {'deleted': count}
