# Justfile for My API Project

default:
    @just list

# Development
dev:
    python manage.py runserver

# Database
migrate:
    python manage.py migrate

makemigrations:
    python manage.py makemigrations

createsuperuser:
    python manage.py createsuperuser

# Testing
test:
    pytest

test-coverage:
    pytest --cov=apps --cov-report=html

# Code quality
lint:
    ruff check .

format:
    ruff format .

type-check:
    mypy .

fix:
    ruff check --fix .

# Background tasks
celery-worker:
    celery -A config.celery worker -l INFO

celery-beat:
    celery -A config.celery beat -l INFO

flower:
    celery flower --broker=redis://localhost:6379/0

# Temporal
temporal-worker:
    python temporal_app/run_temporal_worker.py

# Docker
docker-up:
    docker compose up -d

docker-down:
    docker compose down

docker-logs:
    docker compose logs -f

# Setup
setup:
    uv sync

# Help
list:
    @just --list
