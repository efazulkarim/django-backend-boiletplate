"""Tests for users app."""
import pytest
from django.contrib.auth import get_user_model
from django.test import Client

from tests.factories import UserFactory

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    """Test custom user model."""

    def test_create_user(self):
        """Test creating a user with email."""
        user = User.objects.create_user(email='test@example.com', password='testpass123')
        assert user.email == 'test@example.com'
        assert user.check_password('testpass123')
        assert not user.check_password('wrongpassword')
        assert user.username is None

    def test_user_factory(self):
        """Test UserFactory creates valid users."""
        user = UserFactory()
        assert user.email
        assert user.check_password('testpass123')

    def test_user_factory_custom_password(self):
        """Test UserFactory with custom password."""
        user = UserFactory(password='custom456')
        assert user.check_password('custom456')

    def test_user_factory_batch(self):
        """Test UserFactory creates batches."""
        users = UserFactory.create_batch(5)
        assert len(users) == 5
        assert len({u.email for u in users}) == 5  # all unique emails

    def test_admin_factory(self):
        """Test admin factory creates staff user."""
        admin = UserFactory(is_staff=True)
        assert admin.is_staff is True

    def test_user_str(self):
        """Test __str__ returns email."""
        user = UserFactory(email='str-test@example.com')
        assert str(user) == 'str-test@example.com'

    def test_no_username_field(self):
        """Test User model has no username field."""
        user = UserFactory()
        assert not hasattr(user, 'username') or user.username is None


@pytest.mark.django_db
class TestUserAuthentication:
    """Test user authentication."""

    def test_login_endpoint_exists(self):
        """Test allauth login endpoint responds."""
        client = Client()
        response = client.get('/api/auth/login/')
        assert response.status_code in (200, 302)

    def test_signup_endpoint_exists(self):
        """Test allauth signup endpoint is wired."""
        from django.urls import reverse
        # Just verify the URL resolves — allauth's form rendering
        # requires full User model compatibility which is tested separately.
        try:
            reverse('account_signup')
        except Exception:
            pytest.fail('account_signup URL not found')
