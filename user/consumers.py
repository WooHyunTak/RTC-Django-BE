import logging

from channels.generic.websocket import AsyncJsonWebsocketConsumer

from common.redis_client import redis_client

logger = logging.getLogger(__name__)


class UserSocketConsumer(AsyncJsonWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.redis_client = redis_client.get_client()
        self.user = None

    def redis_hset_key(self, key, field, value):
        self.redis_client.hset(key, field, value)

    def redis_hdel_key(self, key, field):
        self.redis_client.hdel(key, field)

    async def connect(self):
        try:
            user = self.scope.get("token_user")
            if not user:
                raise Exception("User not found")
            self.user = user

            if not self.channel_layer:
                logger.error("Channel layer not found")
                await self.close(code=4403)
                return

            channel_group_name = "django_chat_user"
            active_channel_key = "django_chat_active_channel"
            await self.channel_layer.group_add(channel_group_name, self.channel_name)

            self.redis_hset_key(active_channel_key, self.user.id, self.channel_name)

            await self.accept()

            await self.send_json(
                {"type": "websocket.accept", "message": "Connected to the server"}
            )
        except Exception:
            await self.close(code=4401)
            return

    async def disconnect(self, close_code):
        try:
            if self.channel_layer:
                channel_group_name = "django_chat_user"
                await self.channel_layer.group_discard(
                    channel_group_name, self.channel_name
                )
                active_channel_key = "django_chat_active_channel"
                self.redis_hdel_key(active_channel_key, self.user.id)
        except Exception:
            logger.error("Error discarding channel group: django_chat_user")

    async def receive_json(self, content):
        try:
            message_type = content.get("type")
            message = content.get("message")
            await self.send_message(message_type, message)
        except Exception:
            await self.close(code=4401)
            logger.error(f"Error receiving message: {content}")

    async def send_message(self, message_type, message):
        try:
            message_data = {
                "type": message_type,
                "message": message,
            }

            await self.send_json(message_data)
        except Exception:
            logger.error(f"Error sending message: {message}")
