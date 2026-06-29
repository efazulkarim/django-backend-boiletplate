"""WebSocket consumers for Django Channels.

Example: a simple notification channel that pushes messages to connected clients.

Wire in config/asgi.py's URLRouter:
    from apps.core.consumers import NotificationConsumer
    websocket_urlpatterns = [
        path('ws/notifications/', NotificationConsumer.as_asgi()),
    ]
"""
import json
import logging

from channels.generic.websocket import AsyncJsonWebsocketConsumer

logger = logging.getLogger(__name__)


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    """WebSocket consumer for real-time notifications.

    Clients connect to ws/notifications/ and receive JSON messages.
    Messages are broadcast to the 'notifications' group.
    """

    async def connect(self):
        self.group_name = 'notifications'

        # Join notification group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        logger.info('websocket_connected', extra={'channel': self.channel_name})

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        logger.info('websocket_disconnected', extra={'channel': self.channel_name, 'code': close_code})

    async def receive_json(self, content, **kwargs):
        """Handle incoming messages from the client.

        Echo the message back and broadcast to the group.
        """
        message = content.get('message', '')
        logger.info('websocket_message_received', extra={'channel': self.channel_name, 'message': message})

        # Broadcast to notification group
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'notification.message',
                'message': message,
            },
        )

    async def notification_message(self, event):
        """Handle messages broadcast to the notification group."""
        await self.send_json({
            'type': 'notification',
            'message': event['message'],
        })
