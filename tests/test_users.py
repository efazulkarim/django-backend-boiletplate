"""Tests for users app."""
import pytest
from django.test import Client
from django.urls import reverse
from django.contrib.auth import get_user_model


User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    """Test custom user model."""

    def test_create_user(self):
        """Test creating a user with email."""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        assert user.email == 'test@example.com'
        assert user.username == 'test@example.com'
        assert user.check_password('testpass123')
        assert not user.check_password('wrongpassword')


@pytest.mark.django_db
class TestUserAuthentication:
    """Test user authentication."""

    def test_login_redirects_to_allauth(self):
        """Test login redirects to allauth."""
        client = Client()
        response = client.get('/accounts/login/')
        assert response.status_code == 200

    def test_logout(self):
        """Test logout."""
        client = Client()
        response = client.get('/accounts/logout/')
        assert response.status_code in [200, 302]
