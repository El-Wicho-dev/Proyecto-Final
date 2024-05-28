# home/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("notifications_group", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("notifications_group", self.channel_name)

    async def notification_message(self, event):
        # Asegúrate de que 'notification_message' en "type": "notification.message"
        message = event['message']
        await self.send(text_data=json.dumps({
            'total_notificaciones': message['total_notificaciones']  # Asegúrate de que la clave coincide con lo que envías
        }))
