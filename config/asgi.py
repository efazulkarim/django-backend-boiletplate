"""ASGI config for My API Project with Channels."""
import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import path

from apps.core.consumers import NotificationConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django_asgi_app = get_asgi_application()

websocket_urlpatterns = [
    path('ws/notifications/', NotificationConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    'http': AuthMiddlewareStack(django_asgi_app),
    'websocket': AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
})
