"""Pytest configuration and shared fixtures."""
import os
import sys

import django
import pytest
from rest_framework.test import APIClient

from tests.factories import UserFactory


def pytest_configure():
    """Configure Django settings for pytest."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.test')
    sys.path.insert(0, os.path.dirname(__file__))
    django.setup()


@pytest.fixture
def user(db):
    """Create a standard user."""
    return UserFactory()


@pytest.fixture
def admin_user(db):
    """Create an admin/staff user."""
    return UserFactory(is_staff=True)


@pytest.fixture
def client():
    """DRF API client (unauthenticated)."""
    return APIClient()


@pytest.fixture
def auth_client(user):
    """DRF API client authenticated as a standard user."""
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def admin_client(admin_user):
    """DRF API client authenticated as an admin."""
    client = APIClient()
    client.force_authenticate(user=admin_user)
    return client
