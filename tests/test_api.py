"""Tests for API endpoints."""
import pytest
from rest_framework import status


@pytest.mark.django_db
class TestAPIRoot:
    """Test API root endpoint."""

    def test_api_root(self, client):
        """Test API root returns welcome message."""
        response = client.get('/api/')
        assert response.status_code == status.HTTP_200_OK
        assert 'message' in response.json()
        assert 'version' in response.json()
        assert 'endpoints' in response.json()


@pytest.mark.django_db
class TestUserAPI:
    """Test user API endpoints."""

    def test_profile_requires_auth(self, client):
        """Test user profile requires authentication."""
        response = client.get('/api/users/profile/')
        assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)

    def test_profile_returns_user_data(self, auth_client, user):
        """Test user profile returns correct data."""
        response = auth_client.get('/api/users/profile/')
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['email'] == user.email
        assert response.json()['first_name'] == user.first_name

    def test_profile_update(self, auth_client, user):
        """Test PATCH profile updates allowed fields."""
        response = auth_client.patch(
            '/api/users/profile/',
            {'first_name': 'Updated', 'last_name': 'Name'},
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['first_name'] == 'Updated'
        assert response.json()['last_name'] == 'Name'

    def test_profile_update_ignores_disallowed_fields(self, auth_client, user):
        """Test PATCH profile ignores fields not in serializer."""
        response = auth_client.patch(
            '/api/users/profile/',
            {'email': 'hacked@example.com', 'is_staff': True},
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['email'] == user.email
        assert response.json()['is_staff'] is False
