"""Tests for core app."""
import pytest
from django.test import Client
from django.urls import reverse


@pytest.mark.django_db
class TestHealthChecks:
    """Test health check endpoints."""

    def test_health_check(self):
        """Test health check endpoint."""
        client = Client()
        response = client.get('/health/')
        assert response.status_code == 200
        assert 'status' in response.json()
        assert response.json()['status'] == 'healthy'

    def test_readiness_check(self):
        """Test readiness check endpoint."""
        client = Client()
        response = client.get('/health/ready/')
        assert response.status_code == 200
        assert 'status' in response.json()
        assert response.json()['status'] == 'ready'
