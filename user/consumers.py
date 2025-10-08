import logging

from channels.generic.websocket import AsyncJsonWebsocketConsumer

from common.redis_client import redis_client
from user.helper import save_message_by_channel, save_message_to_user

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

    def get_user_channel_name(self, field):
        channel_name_key = "django_chat_active_channel"
        return self.redis_client.hget(channel_name_key, field)

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

    async def receive_json(self, data):
        try:
            send_channel_type = data.get("sendChannelType")
            if send_channel_type == "channel":
                group_name, message_content = await save_message_by_channel(data)
                await self.send_message_by_channel(
                    group_name, message_content, is_group=True
                )

            elif send_channel_type == "direct":
                # 보낸사람 정보
                from_user = self.scope.get("token_user")
                from_user_id = from_user.id
                data["from_user_id"] = from_user_id
                message = await save_message_to_user(data)
                to_user_id = data.get("toUserId")
                channel_name = self.get_user_channel_name(to_user_id)
                if not channel_name:
                    logger.warning(
                        f"Skip direct send: not found channel for user {to_user_id}"
                    )
                    return
                await self.send_message_by_channel(
                    channel_name, message, is_group=False
                )

        except Exception as e:
            await self.close(code=4401)
            logger.error(f"Error receiving message: {e}")

    async def send_message_by_channel(self, channel_name, message, is_group=False):
        """
        채널 그룹에 소켓 전송
        :param channel_name: 채널 그룹 이름
        :param message: 메시지
        """
        if is_group:
            await self.channel_layer.group_send(
                channel_name,
                {
                    "type": "chat.message",
                    "message": message,
                },
            )
        else:
            await self.channel_layer.send(
                channel_name,
                {
                    "type": "chat.message",
                    "message": message,
                },
            )

    async def chat_message(self, event):
        await self.send_json(
            {
                "type": "message",
                "message": event.get("message"),
            }
        )

    async def send_message(self, message_type, message):
        try:
            message_data = {
                "type": message_type,
                "message": message,
            }

            await self.send_json(message_data)
        except Exception:
            logger.error(f"Error sending message: {message}")
