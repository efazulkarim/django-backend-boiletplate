# Celery Tasks Skill

## When to use Celery

- **Fire-and-forget**: sending emails, push notifications, webhook delivery
- **Scheduled tasks**: daily cleanup, report generation, data sync
- **Heavy computation**: PDF generation, data export, image processing
- **Rate-limited operations**: third-party API calls with quotas

Do NOT use Celery for things that need a response in the same request cycle.

## Task template

```python
# apps/<app>/tasks.py
import logging
from celery import shared_task
from django.apps import apps as django_apps

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    acks_late=True,
    reject_on_worker_lost=True,
)
def send_notification_email(self, user_id: int, message: str) -> dict[str, str]:
    """Send a notification email to a user.

    Uses apps.get_model() to avoid import-time model access.
    Retries on transient failures with exponential backoff.
    """
    try:
        User = django_apps.get_model("users", "User")
        user = User.objects.get(id=user_id)

        # ... send email logic ...

        logger.info("Email sent to user %d", user_id)
        return {"status": "sent", "user_id": str(user_id)}

    except User.DoesNotExist:
        logger.error("User %d not found, skipping email", user_id)
        return {"status": "skipped", "reason": "user_not_found"}

    except Exception as exc:
        logger.warning("Email send failed for user %d: %s", user_id, exc)
        raise self.retry(exc=exc, countdown=2 ** self.request.retries * 60)
```

## Scheduled tasks (Celery Beat)

```python
# config/settings/base.py
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    "cleanup-expired-sessions": {
        "task": "apps.core.tasks.cleanup_expired_sessions",
        "schedule": crontab(hour=3, minute=0),  # 3 AM daily
        "args": (),
        "options": {"queue": "maintenance"},
    },
    "generate-daily-report": {
        "task": "apps.api.tasks.generate_daily_report",
        "schedule": crontab(hour=6, minute=0, day_of_week="1-5"),
        "kwargs": {"report_type": "summary"},
    },
}
```

## Testing tasks

```python
import pytest
from unittest.mock import patch, MagicMock
from apps.core.tasks import send_notification_email


@pytest.mark.django_db
def test_send_notification_email_success(user):
    """Task should send email and return success status."""
    with patch("apps.core.tasks.send_mail") as mock_send:
        mock_send.return_value = 1
        result = send_notification_email.delay(user.id, "Hello")

    assert result.get(timeout=10) == {"status": "sent", "user_id": str(user.id)}


@pytest.mark.django_db
def test_send_notification_email_missing_user():
    """Task should handle missing user gracefully."""
    result = send_notification_email.delay(99999, "Hello")
    assert result.get(timeout=10) == {"status": "skipped", "reason": "user_not_found"}


def test_send_notification_email_retries():
    """Task should retry on transient failures."""
    task = send_notification_email
    task.max_retries = 3

    with patch("apps.core.tasks.User.objects.get") as mock_get:
        mock_get.side_effect = ConnectionError("SMTP down")

        with pytest.raises(task.retry):
            task(1, "Hello")
```

## Testing Celery Beat schedule

```python
@pytest.mark.django_db
def test_beat_schedule_has_required_fields(settings):
    """Every beat schedule entry must have task, schedule, and either args or kwargs."""
    for name, entry in settings.CELERY_BEAT_SCHEDULE.items():
        assert "task" in entry, f"{name} missing 'task'"
        assert "schedule" in entry, f"{name} missing 'schedule'"
        assert "args" in entry or "kwargs" in entry, f"{name} missing 'args' or 'kwargs'"
```

## Queue routing

```python
# config/settings/base.py
CELERY_TASK_ROUTES = {
    "apps.core.tasks.send_*": {"queue": "emails"},
    "apps.api.tasks.generate_*": {"queue": "reports"},
    "apps.core.tasks.cleanup_*": {"queue": "maintenance"},
}

CELERY_TASK_DEFAULT_QUEUE = "default"
```

## Task naming convention

```
apps.<app>.tasks.<verb>_<noun>
```

Examples:
- `apps.core.tasks.send_notification_email`
- `apps.api.tasks.generate_daily_report`
- `apps.users.tasks.cleanup_expired_tokens`

## Error handling patterns

```python
from celery.exceptions import SoftTimeLimitExceeded


@shared_task(
    soft_time_limit=300,  # 5 minutes
    time_limit=360,  # 6 minutes hard limit
)
def long_running_task(data_id: int) -> dict:
    try:
        # ... work ...
        return {"status": "done"}
    except SoftTimeLimitExceeded:
        logger.error("Task timed out processing data %d", data_id)
        return {"status": "timeout"}
```

## Monitoring

```bash
# Check worker status
celery -A config inspect active
celery -A config inspect reserved
celery -A config inspect stats

# Purge a queue
celery -A config purge -Q emails

# Flower (web UI)
celery -A config flower --port=5555
```
