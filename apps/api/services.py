"""Service layer for the API app.

Services own business logic. Views call services; services call the ORM.
This keeps views thin and business logic testable.
"""
import logging

from django.contrib.auth import get_user_model

from apps.core.exceptions import NotFoundError, ValidationError

User = get_user_model()
logger = logging.getLogger(__name__)


class UserService:
    """Business logic for user operations."""

    @staticmethod
    def get_user_by_id(user_id: int) -> User:
        """Fetch a user by ID or raise NotFoundError."""
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise NotFoundError('User', user_id)

    @staticmethod
    def update_profile(user: User, data: dict) -> User:
        """Update user profile fields.

        Only allows updating first_name and last_name.
        Raises ValidationError if no valid fields provided.
        """
        allowed_fields = {'first_name', 'last_name'}
        update_data = {k: v for k, v in data.items() if k in allowed_fields}

        if not update_data:
            raise ValidationError(
                'No valid fields to update.',
                detail={'fields': f'Allowed: {", ".join(sorted(allowed_fields))}'},
            )

        for field, value in update_data.items():
            setattr(user, field, value)

        user.save(update_fields=list(update_data.keys()) + ['updated_at'])
        logger.info('user_profile_updated', extra={'user_id': user.id, 'fields': list(update_data.keys())})
        return user
