---
paths:
  - "apps/*/views.py"
  - "apps/*/services.py"
  - "apps/*/models.py"
  - "apps/*/serializers.py"
  - "apps/*/urls.py"
  - "config/**"
---

# Layered architecture rules

The target architecture for `my-api-project`:

```text
Views (HTTP layer)         →  apps/*/views.py
Services (business logic)  →  apps/*/services.py
Models (data access)       →  apps/*/models.py
Serializers (validation)   →  apps/*/serializers.py
URLs (routing)             →  apps/*/urls.py
Settings (config)          →  config/settings/
```

These rules keep each layer honest.

## Views (`apps/*/views.py`)

- **Thin**: parse request, call service/ORM, return DRF Response.
- **No complex business logic** in views. Validation rules, orchestration, external calls — all live in the service.
- **No raw SQL** in views. Use Django ORM or delegate to services.
- **Auth**: `permission_classes = [IsAuthenticated]` on every mutating view. Pull the user from `request.user`.
- **Idempotency-Key**: every non-idempotent POST reads the header and forwards it to the service.
- **Serializer**: every endpoint declares `serializer_class`. Override `get_serializer_class()` for different actions.

## Services (`apps/*/services.py`)

- **Plain classes or functions** (project pattern: `<Resource>Service`). No instance state needed.
- **Own business logic**: validation rules, orchestration, external calls, transaction boundaries.
- **ORM access**: services use Django ORM directly for simple queries, or call managers for complex ones.
- **External SDKs**: one service per external system (`PolarService`, `StripeService`, `LLMService`). No SDK imports in views.
- **Return querysets or dicts**, not serialized data. Serializers handle serialization in the view.
- **Logging**: `logging.getLogger(__name__)`. Never `print()`.

## Models (`apps/*/models.py`)

- **Django ORM** with `models.Model`. Use `TimestampedModel` and `SoftDeleteModel` base classes.
- **`auto_now_add=True`** for `created_at`, `auto_now=True` for `updated_at`.
- **Soft delete** via `is_deleted` boolean, never `QuerySet.delete()`.
- **`db_index=True`** on every FK. Composite indexes in `Meta.indexes`.
- **`related_name`** on every FK for reverse access.
- **`settings.AUTH_USER_MODEL`** for user FKs, never `auth.User` directly.

## Serializers (`apps/*/serializers.py`)

- **DRF serializers**, separate request/response when needed: `ResourceCreateSerializer`, `ResourceSerializer`.
- Free-text fields: `max_length=...` for DoS protection.
- Closed enums: `ChoiceField` or `CharField(choices=...)`.

## Anti-patterns to flag

- Complex business logic in a view body.
- `stripe.` / `polar_sdk.` / `httpx` import in a view or model.
- `print()` in production code path.
- A service that takes `request` as a parameter — services don't know about HTTP (pass `request.user` instead).
- A model that mutates a serializer's nested data — that's an N+1 / hidden coupling smell.

## Don't

- Don't import from `apps.*.views` in a service.
- Don't put `os.environ` calls outside `config/settings/`.
- Don't put `try/except` around the entire view body to "make it work" — exceptions should be specific.
- Don't bypass the app structure ("I'll just put logic in the view for now").
