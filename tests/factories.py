"""Test factories using factory_boy.

Usage in tests:
    user = UserFactory()
    admin = UserFactory(is_staff=True)
    users = UserFactory.create_batch(10)
"""
import factory
from django.contrib.auth import get_user_model

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    """Factory for the custom User model."""

    class Meta:
        model = User
        skip_postgeneration_save = True

    email = factory.Sequence(lambda n: f'user{n}@example.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_active = True
    is_staff = False

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        """Set password after user creation."""
        password = extracted or 'testpass123'
        self.set_password(password)
        if create:
            self.save()
