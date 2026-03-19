# My API Project

A production-ready Django API with Celery, Temporal, and WebSockets.

## Features

- Django 6.0 with Python 3.12+
- Django REST Framework (DRF) with OpenAPI 3.0 (drf-spectacular)
- Django-allauth for authentication (session-based)
- Celery for background tasks
- Temporal for durable workflows
- Django Channels for WebSockets
- PostgreSQL database
- Redis for caching
- Sentry for error tracking
- Structured JSON logging

## Prerequisites

- Python 3.12+
- Docker & Docker Compose
- Node.js 20+ (not required for API-only setup)

## Quick Start

1. **Install dependencies**:
   ```bash
   # Using uv (recommended)
   pip install uv
   uv sync

   # Or using pip
   pip install -e .
   ```

2. **Start services**:
   ```bash
   docker compose up -d
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Create superuser**:
   ```bash
   python manage.py createsuperuser
   ```

6. **Start development server**:
   ```bash
   python manage.py runserver
   ```

## Services

- Django API: http://localhost:8000
- Admin: http://localhost:8000/admin/
- API Docs (Swagger): http://localhost:8000/api/schema/swagger/
- Mailpit (email testing): http://localhost:8025
- Flower (Celery): http://localhost:5555
- Temporal UI: http://localhost:8088

## Project Structure

```
my-api-project/
├── apps/              # Django applications
│   ├── core/          # Core functionality (health checks)
│   ├── users/         # User authentication
│   └── api/           # REST API endpoints
├── config/            # Django settings
│   └── settings/      # Split settings (base/dev/test/prod)
├── temporal_app/       # Temporal workflows & activities
├── tests/             # Test suite
├── Dockerfile         # Production image
├── docker-compose.yml # Development services
├── manage.py          # Django management
└── pyproject.toml     # Dependencies
```

## Development

### Run Tests

```bash
pytest
```

### Lint & Format

```bash
ruff check .
ruff format .
mypy .
```

### Celery Worker

```bash
celery -A config.celery worker -l INFO
```

### Celery Beat (Scheduler)

```bash
celery -A config.celery beat -l INFO
```

### Temporal Worker

```bash
python temporal_app/run_temporal_worker.py
```

## Documentation

See the `docs/` directory for detailed documentation on:
- API development
- Testing
- Deployment
- Celery & Temporal
- WebSockets

## License

MIT
