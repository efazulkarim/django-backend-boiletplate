"""Tests for API endpoints."""
import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model


User = get_user_model()


@pytest.mark.django_db
class TestAPIRoot:
    """Test API root endpoint."""

    def test_api_root(self):
        """Test API root returns welcome message."""
        client = APIClient()
        response = client.get('/api/')
        assert response.status_code == status.HTTP_200_OK
        assert 'message' in response.json()
        assert 'version' in response.json()
        assert 'endpoints' in response.json()


@pytest.mark.django_db
class TestUserAPI:
    """Test user API endpoints."""

    def test_user_profile_requires_auth(self):
        """Test user profile requires authentication."""
        client = APIClient()
        response = client.get('/api/profile/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_user_profile_authenticated(self):
        """Test user profile with authentication."""
        # Create user
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        
        # Authenticate
        client = APIClient()
        client.force_authenticate(user=user)
        
        response = client.get('/api/profile/')
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['email'] == 'test@example.com'
