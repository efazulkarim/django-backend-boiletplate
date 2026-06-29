# Django Backend Boilerplate — Claude Project Rules

## What this is

`my-api-project` is a **production-ready Django API backend** (Python 3.12+). It powers a data-driven web application with REST APIs, WebSocket support, background tasks (Celery + Temporal), and django-allauth authentication.

## Stack

- **Framework**: Django 6.0, Django REST Framework 3.15
- **ORM**: Django ORM, PostgreSQL (Neon in prod, SQLite in-memory for tests)
- **Auth**: django-allauth (email-based), DRF Token auth, session auth
- **WebSockets**: Django Channels + channels-redis
- **Background tasks**: Celery (fire-and-forget/scheduled) + Temporal (durable workflows)
- **API docs**: drf-spectacular (OpenAPI)
- **Observability**: Sentry, python-json-logger
- **Testing**: pytest + pytest-django
- **Lint/format**: ruff (`line-length = 100`, target py312)
- **Type checking**: mypy (strict, django-stubs)
- **Dependency management**: uv

## Architecture

```text
config/                      → Settings, root URLs, WSGI/ASGI, Celery config
  settings/                  → base.py, dev.py, prod.py, test.py
apps/                        → Django apps (domain boundary)
  core/                      → Health checks, foundational utilities
  users/                     → Custom User model (email-based), admin
  api/                       → REST API endpoints, views
temporal_app/                → Temporal workflows and activities
tests/                       → Project-wide test suite
```

- **Views handle HTTP**: parse request, call service/ORM, return DRF Response.
- **Services own business logic**: create `services.py` inside apps as the app grows.
- **Models define schema**: Django ORM with `created_at`/`updated_at`, soft-delete via `is_deleted`.
- **Serializers validate input/output**: DRF serializers in `serializers.py` per app.

## Conventions

- **Endpoints**: plural nouns, no verbs, flat where possible (`/ideas/`, `/ideas/{id}/`).
- **Response format**: `Content-Type: application/json` only. Errors use DRF's default `{ "detail": "..." }` or structured `{ "error": "...", "detail": {...} }`.
- **HTTP semantics**: POST → 201, PUT/PATCH → 200, DELETE → 204, async → 202, auth fail → 401, forbidden → 403.
- **Idempotency**: every non-idempotent POST takes an `Idempotency-Key` header; persist it on the worker side too.
- **Serializers**: DRF serializers per app (`apps/<app>/serializers.py`); separate request/response when needed.
- **Models**: Django ORM in `apps/<app>/models.py`; timestamps via `created_at`/`updated_at`; soft-delete via `is_deleted` flag, not row removal.
- **Migrations**: Django migrations (`makemigrations`/`migrate`), never destructive, always reversible, always add indexes for new FKs and new query columns.
- **Tests**: in `tests/` directory, pytest with `@pytest.mark.django_db`. Mark slow/external tests.
- **Settings**: typed in `config/settings/` with environment-specific overrides. Never read `os.environ` outside settings files. Never log a secret.

## Domain invariants (do not break)

1. **`AUTH_USER_MODEL`** is `users.User` (email-based, no username). Never revert to default Django user.
2. **API response shapes** are a public contract; never change a field name, type, or nullability without a deprecation path.
3. **`SECRET_KEY`**, `SENTRY_DSN`, `DB_PASSWORD`, and all external service keys come from env only. Never commit values.
4. **Settings inheritance**: `base.py` → `dev.py` / `prod.py` / `test.py`. Never import `dev` settings in production.
5. **Background tasks**: Celery for fire-and-forget, Temporal for durable/stateful workflows. Don't mix responsibilities.

## Common commands

```bash
# Lint
ruff check .                     # check
ruff check --fix .               # autofix
ruff format .                    # format

# Type check
mypy .                           # strict type checking

# Tests
pytest -q                        # all
pytest -q -m unit                # unit only
pytest -q tests/test_foo.py      # one file
pytest -q -k "name_pattern"      # by name

# Django management
python manage.py makemigrations  # generate migrations
python manage.py migrate         # apply migrations
python manage.py migrate --check # check for pending migrations
python manage.py shell           # Django shell
python manage.py createsuperuser # create admin user

# Dev server
python manage.py runserver       # localhost:8000

# Background workers
celery -A config worker -l info  # Celery worker
celery -A config beat -l info    # Celery beat (scheduled tasks)
python temporal_app/run_temporal_worker.py  # Temporal worker

# Health
curl http://localhost:8000/health/
```

## What NOT to do

- Don't write plain-text responses from any API endpoint.
- Don't `git push --force` or `git reset --hard`.
- Don't edit `.env` (local dev file, ignored). Use `.env.example` for new keys.
- Don't refactor unrelated code in a feature PR — keep diffs minimal and focused.
- Don't introduce `Any` types; prefer explicit types with django-stubs.
- Don't log JWTs, API keys, passwords, or session secrets.
- Don't skip writing reverse operations for data migrations.
- Don't bypass the app structure ("I'll just put logic in the view for now").
- Don't use `os.environ` outside `config/settings/` files.
- Don't run `pip install` against prod; use `uv sync` with the pinned `pyproject.toml`.

## What to defer to globals

- **Caveman mode**, env vars, base permissions, plugins → `~/.claude/settings.json` (already wired).
- **General engineering rules** (REST standards, error shape, secrets policy) → `~/.claude/CLAUDE.md`.

This file is the **project-specific** layer. The global layer is the default. Where they conflict, project rules win.
