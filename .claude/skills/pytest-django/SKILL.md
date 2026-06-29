---
name: pytest-django
description: Pytest patterns for my-api-project. Use when writing or running tests. Covers conftest fixtures, DRF APIClient, mocking external services, and the marker system.
---

# Pytest + Django — `my-api-project`

## Layout

```text
tests/
  conftest.py            # shared fixtures
  test_core.py           # health checks
  test_users.py          # user model + auth
  test_api.py            # API endpoints
```

## Markers (`pytest.ini`)

`unit`, `integration`, `slow`, `database`, `external`

## conftest.py

```python
# tests/conftest.py
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.test")

import django
django.setup()

import pytest
from django.test.utils import setup_databases, teardown_databases
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from apps.users.models import User


@pytest.fixture(scope="session")
def django_db_setup():
    """Set up the test database."""
    db_cfg = setup_databases(0, False)
    yield
    teardown_databases(*db_cfg)


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="test@example.com",
        password="testpass123",
        first_name="Test",
        last_name="User",
    )


@pytest.fixture
def auth_token(user):
    token, _ = Token.objects.get_or_create(user=user)
    return token


@pytest.fixture
def auth_client(api_client, auth_token):
    api_client.credentials(HTTP_AUTHORIZATION=f"Token {auth_token.key}")
    return api_client
```

## API test (unit)

```python
# tests/test_api.py
import pytest


@pytest.mark.django_db
def test_api_root(api_client):
    r = api_client.get("/api/")
    assert r.status_code == 200
    assert "message" in r.data


@pytest.mark.django_db
def test_user_profile_requires_auth(api_client):
    r = api_client.get("/api/profile/")
    assert r.status_code == 401


@pytest.mark.django_db
def test_user_profile_authenticated(auth_client, user):
    r = auth_client.get("/api/profile/")
    assert r.status_code == 200
    assert r.data["email"] == user.email
```

## Model test (unit)

```python
# tests/test_users.py
import pytest
from apps.users.models import User


@pytest.mark.django_db
def test_create_user():
    user = User.objects.create_user(
        email="new@example.com",
        password="securepass123",
    )
    assert user.email == "new@example.com"
    assert user.check_password("securepass123")
    assert user.is_active is True
```

## Service test (unit, no HTTP)

```python
# tests/test_resource_service.py
import pytest
from apps.<app>.services import ResourceService


@pytest.mark.django_db
def test_list_for_user(user):
    resources = ResourceService.list_for_user(user)
    assert isinstance(resources, list)
```

## Mocking external services

```python
# tests/test_external.py
import pytest
from unittest.mock import patch, MagicMock


@pytest.mark.django_db
@patch("apps.<app>.services.ExternalService.call")
def test_with_mock(mock_call, user):
    mock_call.return_value = {"status": "ok"}
    result = ResourceService.do_external_thing(user)
    assert result["status"] == "ok"
    mock_call.assert_called_once()
```

## Marking

```python
import pytest

@pytest.mark.unit
def test_foo():
    ...

@pytest.mark.django_db
def test_uses_db(db):
    ...

@pytest.mark.external
def test_hits_real_api():
    ...
```

## Run commands

```bash
pytest -q                                # all
pytest -q -m unit                        # unit only
pytest -q tests/test_foo.py              # one file
pytest -q -k "name_pattern"              # by name
pytest -q -m django_db --durations=10    # DB tests
pytest -q -m external                    # only when asked
```

## Settings for tests

```python
# config/settings/test.py
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
CELERY_TASK_ALWAYS_EAGER = True
```

## Don't do

- Don't put network calls in `unit` tests.
- Don't skip `@pytest.mark.django_db` when accessing the database — tests will fail silently.
- Don't use `django.test.TestCase` — use pytest fixtures instead.
- Don't mock `django.conf.settings` per-test; use `config/settings/test.py`.
- Don't add a test that needs `database` and `external` markers together.
- Don't use `Client()` for API tests — use DRF's `APIClient`.
