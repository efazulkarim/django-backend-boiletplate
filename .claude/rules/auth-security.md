---
paths:
  - "apps/users/**"
  - "apps/*/views.py"
  - "apps/core/middleware.py"
  - "config/settings/**"
---

# Auth & security rules

## Secrets

- All secrets come from env via `config/settings/`. Never `os.environ` outside settings files.
- `SECRET_KEY` must be set from env. Validate it's not the dev placeholder in production.
- Never log secrets: no `print(secret)`, no `logger.info("token: %s", token)`, no echo in tracebacks.
- Never return a secret in an HTTP response, even a partial one.
- Never commit `.env`. The `.gitignore` covers it; the `pre-tool-use-secret-guard` hook blocks it.

## Auth

- `AUTH_USER_MODEL = "users.User"` — email-based, no username.
- DRF Token auth: `rest_framework.authtoken.models.Token` — one token per user.
- Session auth: via `django.contrib.auth` and allauth.
- `permission_classes = [IsAuthenticated]` on every mutating endpoint.
- `request.user` is populated by DRF's authentication classes.
- Return 401 for missing/invalid auth, 403 for insufficient permissions.
- Soft-deleted users cannot authenticate: check `is_active` (Django's built-in flag).

## OAuth (django-allauth)

- Allauth handles registration, login, logout, password reset, email verification, and social auth.
- Verify `id_token` against `SOCIALACCOUNT_PROVIDERS` config.
- `state` and `nonce` must be verified (allauth handles this).

## CORS

- `CORS_ALLOW_ALL_ORIGINS` is `True` only in dev. Never in production.
- `CORS_ALLOW_CREDENTIALS = True` is fine, but only with explicit origins.
- `CORS_ALLOWED_ORIGINS` is an explicit list in production.

## Rate limits / throttling

- Use DRF's `DEFAULT_THROTTLE_CLASSES` and `DEFAULT_THROTTLE_RATES`.
- Default: `60/minute` per user.
- Auth routes: `10/minute`.
- Webhooks: exempt (they hit our IP, not the user's).

## Webhook signature verification

- Every webhook handler verifies the signature. Always.
  - Polar: `webhook-signature` header, `HMAC-SHA256(body, POLAR_WEBHOOK_SECRET)`.
  - Stripe: `stripe-signature` header, `stripe.Webhook.construct_event(body, sig, secret)`.
- Webhook returns 200 quickly; heavy work goes in a Celery task.

## Logging

- Use `logging.getLogger(__name__)`. Never `print()`.
- Never log: Authorization headers, tokens, passwords (plain or hashed), API keys, webhook signatures, full request body on auth routes.
- Structured logging: include request context when available.

## Input validation

- Free-text fields MUST have `max_length`:
  - `name`: 200
  - `description`: 5000
  - answer text: 10000
- Email: `EmailField`.
- Path IDs: typed as `int` (DRF returns 400 on non-int).
- Enums: use `ChoiceField` or `CharField(choices=...)`.

## Debug mode

- `DEBUG=True` only in development. Production sets `DEBUG=False`.
- Never return stack traces in production responses.
