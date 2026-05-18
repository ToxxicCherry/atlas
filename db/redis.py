import redis.asyncio as aioredis
from loguru import logger

class RedisService:
    def __init__(self):
        self.client: aioredis.Redis | None = None

    async def connect(self, url: str = "redis://atlas-redis:6379/0"):
        logger.info('Connecting to Redis')
        self.client = aioredis.from_url(url, encoding="utf-8")

    async def close(self):
        if self.client:
            logger.info('Disconnecting from Redis')
            await self.client.close()