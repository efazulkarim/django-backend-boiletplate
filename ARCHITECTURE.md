# Architectural Review: Django Backend Boilerplate

## 1. System Overview
- **Type of System**: This is a production-ready Web API and background processing backend. It is designed to serve as a robust foundation for a data-driven web application or mobile app.
- **Architectural Style**: It follows a **Modular Monolith** architecture. While all code runs within the same application process (the Django app), it is logically structured into self-contained "apps" (`core`, `users`, `api`) and separate worker processes for asynchronous tasks.
- **Core Technologies**:
  - **Framework**: Django 6.0 (Python 3.12+) serving as the core HTTP framework.
  - **API Layer**: Django REST Framework (DRF) for RESTful endpoints.
  - **WebSockets**: Django Channels for real-time, bi-directional communication.
  - **Asynchronous Processing**: Dual-engine approach using **Celery** (for fire-and-forget/scheduled tasks) and **Temporal** (for stateful, durable, long-running workflows).
  - **Data Layer**: PostgreSQL (relational DB) and Redis (in-memory cache, message broker, channel layer).

## 2. Codebase Structure
The project is strictly organized to separate configuration, domain logic, and background processing:
- `apps/`: The domain boundary. Contains internal Django applications.
  - `core/`: Health checks and foundational utilities.
  - `users/`: Custom user authentication logic (email-based, replacing default username).
  - `api/`: REST API endpoints and views (acting as the presentation/controller layer).
- `config/`: System-wide settings and root URL routing.
  - `settings/`: Split environments (`base.py`, `dev.py`, `prod.py`, `test.py`) for clean configuration management.
- `temporal_app/`: Dedicated module for Temporal workflows and activities, completely decoupled from the HTTP request-response cycle.
- `tests/`: Project-wide test suite using `pytest`.

*Evaluation*: The structure adheres to Django best practices but elevates it by isolating business domains into an `apps` directory, which prevents root-folder clutter and enforces module boundaries.

## 3. Execution Flow
**Typical API Request (e.g., Get User Profile):**
1. **Entry**: Request hits `config.urls` → routed via `apps.api.urls` → `apps.api.views.user_profile`.
2. **Middleware**: Passes through `JSONRequestMiddleware` (logging), `CorsMiddleware`, and authentication.
3. **Controller**: The DRF `@api_view` handles the request, interacts directly with the `request.user` object (populated by `rest_framework.authentication`).
4. **Data Access**: User data is fetched implicitly via Django ORM when accessing the authenticated user instance.
5. **Output**: Serialization into JSON and returned as an HTTP 200 via DRF `Response`.

**Background Workflow (e.g., Temporal Onboarding):**
1. **Trigger**: An API view or Celery task calls the Temporal Client to start `onboarding_workflow`.
2. **Execution**: The Temporal Worker (`run_temporal_worker.py`) picks up the workflow.
3. **Activities**: It sequentially executes `send_email` and `process_report` activities. If the worker crashes mid-step, Temporal resumes state automatically from the cluster.

## 4. State & Data Management
- **Primary Data Store**: PostgreSQL via Django ORM. Standard relational modeling. The `User` model is customized to use email as the primary identifier.
- **Caching & State**: Redis serves multiple roles:
  1. Django Cache backend (implied for typical setups, used for sessions/rate limiting).
  2. Celery Message Broker (`redis://localhost:6379/0`).
  3. Django Channels Layer (`channels_redis.core.RedisChannelLayer`).

## 5. Configuration & Environment
- **Environment Variables**: Heavy reliance on `.env` injected via `os.environ` in `config/settings/base.py`. Secrets (`SECRET_KEY`, `SENTRY_DSN`, `DB_PASSWORD`) are properly abstracted.
- **Environment Separation**: Uses base inheritance (`base.py` imported by `dev.py` and `prod.py`). Production settings (`prod.py`) enforces security flags (`SECURE_SSL_REDIRECT`, `X_FRAME_OPTIONS`, strict CORS).

## 6. Async & Background Processing
The system employs an unusual but powerful **dual-engine** approach:
- **Celery**: Configured with `django-celery-beat` (implied for scheduling). Best for crons, straightforward async tasks (e.g., resizing an image), and high-throughput/low-latency queueing.
- **Temporal**: Integrated for complex sagas and orchestrations (e.g., the nested `payment_workflow` and `onboarding_workflow` in `temporal_app/workflows.py`). Provides durable executions and automatic retries out of the box.

*Critique*: Maintaining both Celery and Temporal workers is operational overhead. Unless there's a strict boundary (Celery for fast background HTTP responses, Temporal for distributed sagas), consider consolidating on Temporal.

## 7. External Integrations
- **Sentry**: Integrated natively (`sentry-sdk`) with performance tracing.
- **Mailpit**: Included in `docker-compose.yml` for local SMTP trapping and testing without external API limits.
- **Authentication**: Integrates `django-allauth` for robust standard and social auth flows.

## 8. DevOps & Deployment
- **Local Dev**: Handled beautifully via `docker-compose.yml` (spins up Postgres, Redis, Mailpit, Temporal Cluster, Flower).
- **Tooling**: Uses `uv` for hyper-fast dependency resolution (via `pyproject.toml`), `Justfile` as a modern `Make` alternative for task running.
- **Code Quality**: Enforced via `ruff` (linter/formatter) and `mypy` (strict static typing).
- **Deployment Build**: Includes a production `Dockerfile`.

## 9. Extensibility
The modular architecture is highly extensible:
- **New Features**: Create a new app (e.g., `python manage.py startapp billing apps/billing`), wire URLs, and add it to `INSTALLED_APPS`.
- **New Workflows**: Simply define them in `temporal_app/workflows.py` without touching Django core logic.
Maintainability is high due to strict typing (`mypy --strict`), structured JSON logging (`django-json-logger`), and test coverage configurations (`pytest-cov`).

## 10. Code Quality & Architecture Evaluation
**What is well-designed:**
- Replaces Django's username with Email immediately (saves massive refactoring headaches later).
- Uses `pyproject.toml` and modern tooling (`uv`, `ruff`) instead of legacy pip/flake8.
- Structured JSON logging instead of raw text logs—critical for Datadog/ELK integration.
- Includes OpenAPI spec generation (`drf-spectacular`).

**Risks & Bottlenecks:**
- **System Complexity**: Running Django, Celery, Temporal Cluster, Redis, and Postgres locally requires significant RAM and context-switching for new developers.
- **DRF Views vs Services**: The boilerplate currently puts logic directly in `views.py`. As the app grows, business logic will leak into controllers.

**Immediate Refactoring Recommendations:**
1. **Service Layer**: Introduce a `services.py` inside apps to decouple business logic from DRF serializers/views. Views should only handle HTTP concerns.
2. **Consolidate Async**: Evaluate if Celery is strictly necessary. Temporal can handle cron jobs and simple tasks, reducing the infrastructure footprint by dropping the Celery worker and Flower.

## 11. Scaling Considerations
- **High Load**: The Django HTTP layer is stateless and can be scaled horizontally behind a load balancer. The DB will be the first bottleneck; Django’s DB connection pooling or PgBouncer should be added to the production stack.
- **WebSockets**: Django Channels with Redis layer scales well, but under massive WebSocket concurrency (100k+ connections), Redis pub/sub can become a bottleneck.
- **Workers**: Temporal and Celery workers can be scaled out independently depending on which queues are lagging.
- **Improvements**: Implement Read Replicas (via Django DB routers) if read-heavy, and ensure caching strategies (via Redis) are wrapped around expensive API queries.
