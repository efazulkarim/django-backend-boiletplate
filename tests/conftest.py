"""Pytest configuration."""
import os
import sys
import django
from django.test.utils import get_runner


def pytest_configure():
    """Configure Django settings for pytest."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.test')
    sys.path.insert(0, os.path.dirname(__file__))
    django.setup()


@pytest.fixture(scope='session')
def django_db_setup():
    """Set up Django test database."""
    TestRunner = get_runner(config.settings.test)
    old_config = TestRunner.setup_test_environment()
    yield TestRunner.teardown_test_environment(old_config)
