---
name: django-models
description: Django ORM model patterns for my-api-project. Use when defining or modifying apps/*/models.py — Django model style, timestamps, soft delete via is_deleted, relationships, and index hints.
---

# Django model patterns — `my-api-project`

## Files in scope

- `apps/<app>/models.py` — domain models
- `apps/users/models.py` — custom User model (email-based)

## Base model (abstract)

```python
# apps/core/models.py
from django.db import models
from django.utils import timezone


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False, db_index=True)

    class Meta:
        abstract = True

    def soft_delete(self):
        self.is_deleted = True
        self.save(update_fields=["is_deleted", "updated_at"])
```

## Model template

```python
# apps/<app>/models.py
from django.db import models
from django.conf import settings
from apps.core.models import TimestampedModel, SoftDeleteModel


class Resource(TimestampedModel, SoftDeleteModel):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="resources",
        db_index=True,
    )

    class Meta:
        db_table = "resources"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["created_by", "is_deleted"], name="ix_resources_user_active"),
        ]

    def __str__(self):
        return f"Resource(id={self.pk})"
```

## Conventions

- Inherit from `TimestampedModel` and/or `SoftDeleteModel` for domain models.
- `auto_now_add=True` for `created_at`, `auto_now=True` for `updated_at`.
- Soft delete: `is_deleted` boolean, never `QuerySet.delete()`. Use `soft_delete()` method.
- Foreign keys: explicit `on_delete` (`CASCADE` for owned children, `SET_NULL` for optional links).
- `related_name` on every FK for reverse access.
- `db_index=True` on every FK. Composite indexes in `Meta.indexes`.
- `db_table` explicitly set for non-auth models.
- `__str__`: f"{ClassName}(id={self.pk})" only. No dumping of long fields.
- Use `settings.AUTH_USER_MODEL` for user FKs, never `auth.User` directly.

## Custom User model

```python
# apps/users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "users"

    def __str__(self):
        return self.email
```

## Schema→serializer sync

- Field name alignment: `is_deleted` in DB maps to `is_deleted` in serializer.
- Enum-like fields: prefer `CharField(max_length=32)` with choices over Postgres enum; easier migrations.
- Don't expose `password` or `secret_*` fields via serializers.

## Don't do

- Don't add indexes that duplicate an existing FK index.
- Don't use `select_related` on large tables without considering the join cost.
- Don't expose `password` or sensitive columns via serializer.
- Don't use `on_delete=CASCADE` on a child whose parent is soft-deleted (it'd be unreachable).
- Don't import `User` directly — use `settings.AUTH_USER_MODEL`.
