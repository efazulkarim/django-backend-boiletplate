# Getting Started with My API Project

Congratulations! Your Django API boilerplate is ready. This guide will walk you through setup and initial development.

## Prerequisites Check

Ensure you have these tools installed:

- Python 3.12+ ✓ (verified: 3.12.9)
- Docker & Docker Compose ✓ (verified: 29.2.1)
- Node.js 20+ ✓ (verified: v24.3.0) - not required for API-only setup

## Step 1: Install Python Dependencies

### Option A: Using pip (Recommended - Works with MSYS2 Python)

```bash
cd d:\Backend\my-api-project
pip install -r requirements-dev.txt
```

### Option B: Using uv (Faster - Requires proper Python installation)

If you have a non-MSYS2 Python installation:

```bash
# Install uv
pip install uv

# Install dependencies
uv sync
```

## Step 2: Start Docker Services

This starts PostgreSQL, Redis, Mailpit (email testing), and Temporal (workflows):

```bash
cd d:\Backend\my-api-project
docker compose up -d
```

Expected services to start:

- postgres: Database on port 5432
- redis: Cache & message broker on port 6379
- mailpit: Email testing UI on http://localhost:8025
- temporal: Workflow engine UI on http://localhost:8088
- flower: Celery monitoring on http://localhost:5555

Verify all services are running:

```bash
docker compose ps
```

## Step 3: Configure Environment

Copy the example environment file and customize it:

```bash
cp .env.example .env
```

Edit `.env` with your settings. For local development, the defaults work fine:

```env
# Django
SECRET_KEY=your-secret-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_SETTINGS_MODULE=config.settings.dev

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/my_api_project

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Temporal
TEMPORAL_HOST=localhost:7233
TEMPORAL_NAMESPACE=default
```

## Step 4: Run Migrations

Create the database schema:

```bash
python manage.py migrate
```

## Step 5: Create Superuser

Create an admin user:

```bash
python manage.py createsuperuser
```

Follow the prompts to enter:

- Email: admin@example.com
- Password: (choose a strong password)

## Step 6: Start Development Server

```bash
python manage.py runserver
```

Or use the `just` task runner:

```bash
just dev
```

## Step 7: Verify Everything Works

### Health Check

Open in browser or use curl:

```bash
curl http://localhost:8000/health/
```

Expected response:

```json
{
  "status": "healthy",
  "service": "my-api-project",
  "database": "connected"
}
```

### API Root

```bash
curl http://localhost:8000/api/
```

### Admin Interface

Open http://localhost:8000/admin/

- Login with the superuser you created
- Manage users, view application logs

### Email Testing

Open http://localhost:8025

- View all emails sent during development
- Test email templates and delivery

### Temporal Workflows

Open http://localhost:8088

- View workflow executions
- Monitor workflow history
- Debug workflow issues

### Celery Monitoring

Open http://localhost:5555

- View Celery workers
- Monitor task execution
- View task statistics

## Testing Your Setup

Run the test suite:

```bash
pytest
```

Run with coverage:

```bash
just test-coverage
```

Run specific test files:

```bash
pytest tests/test_core.py
pytest tests/test_users.py
pytest tests/test_api.py
```

## Project Structure

```
my-api-project/
├── apps/
│   ├── core/              # Health checks, middleware
│   ├── users/             # Custom user model, auth
│   └── api/               # REST API endpoints
├── config/
│   ├── settings/
│   │   ├── base.py       # Common settings
│   │   ├── dev.py        # Development settings
│   │   ├── test.py       # Test settings
│   │   └── prod.py       # Production settings
│   ├── urls.py            # Root URL configuration
│   ├── asgi.py            # ASGI config (WebSockets)
│   └── wsgi.py            # WSGI config
├── temporal_app/           # Temporal workflows & activities
│   ├── workflows.py       # Workflow definitions
│   ├── activities.py      # Activity implementations
│   └── run_temporal_worker.py  # Worker process
├── tests/                 # Test suite
│   ├── test_core.py      # Health check tests
│   ├── test_users.py     # User model tests
│   └── test_api.py       # API endpoint tests
├── docker-compose.yml       # Development services
├── Dockerfile              # Production image
├── requirements.txt         # Production dependencies
├── requirements-dev.txt     # Development dependencies
├── manage.py              # Django CLI
├── Justfile               # Task runner commands
├── pytest.ini             # pytest configuration
└── GETTING_STARTED.md     # This file
```

## Common Development Tasks

### Create a new Django app

```bash
python manage.py startapp my_new_app
```

### Create a Celery task

Edit `apps/core/tasks.py`:

```python
from celery import shared_task

@shared_task
def my_background_task(param):
    # Your task logic here
    return result
```

### Create a Temporal workflow

Edit `temporal_app/workflows.py`:

```python
from temporalio import workflow, activity

@activity.defn
def my_activity(param: str) -> str:
    # Your activity logic
    return f"Processed: {param}"

@workflow.defn
def my_workflow(param: str) -> str:
    result = yield activity.execute(my_activity, args=[param])
    return result
```

### Run code quality checks

```bash
# Lint
just lint

# Format
just format

# Type check
just type-check
```

### Start background workers

In separate terminal windows:

```bash
# Terminal 1: Django dev server
just dev

# Terminal 2: Celery worker
just celery-worker

# Terminal 3: Temporal worker
just temporal-worker

# Terminal 4: Celery beat scheduler (optional)
just celery-beat
```

## Next Steps

1. **Explore the code**: Look at `apps/core/`, `apps/users/`, and `apps/api/`
2. **Add your business logic**: Create new apps or extend existing ones
3. **Write tests**: Add test files in `tests/` for new features
4. **Build API endpoints**: Add views in `apps/api/views.py`
5. **Configure Celery tasks**: Add background jobs in `apps/core/tasks.py`
6. **Design workflows**: Use Temporal for complex multi-step processes
7. **Set up WebSockets**: Implement Channels consumers in `apps/api/consumers.py`
8. **Configure production**: Update `.env` for production settings

## Troubleshooting

### Database Connection Error

If you see "could not connect to server":

```bash
# Check if PostgreSQL is running
docker compose ps postgres

# View logs
docker compose logs postgres
```

### Redis Connection Error

```bash
# Check Redis
docker compose ps redis

# View logs
docker compose logs redis
```

### Import Errors

If you see module not found errors:

```bash
# Reinstall dependencies
pip install -r requirements-dev.txt

# Check Python version
python --version  # Should be 3.12+
```

## Resources

- Django Documentation: https://docs.djangoproject.com/
- Django REST Framework: https://www.django-rest-framework.org/
- Celery: https://docs.celeryproject.org/
- Temporal: https://docs.temporal.io/
- Channels (WebSockets): https://channels.readthedocs.io/
