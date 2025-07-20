import redis
from django.conf import settings


class RedisClient:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True,
        )

    def get_client(self):
        return self.redis_client


redis_client = RedisClient()
