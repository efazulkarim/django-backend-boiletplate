"""ASGI config for My API Project with Channels."""
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django_asgi_app = get_asgi_application()

# Import your routing here
application = ProtocolTypeRouter({
    'http': AuthMiddlewareStack(django_asgi_app),
    'websocket': AuthMiddlewareStack(django_asgi_app),
})
