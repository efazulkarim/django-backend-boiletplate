"""User models with email-based authentication."""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model using email as username."""

    # Remove username field, use email instead
    username = None
    email = models.EmailField(unique=True, verbose_name='email address')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.email
