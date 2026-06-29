"""DRF serializers for the API app."""
from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model — read-only profile fields."""

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'is_staff',
            'date_joined',
        ]
        read_only_fields = fields


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile — only editable fields."""

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
        ]
