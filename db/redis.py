import redis.asyncio as aioredis
from loguru import logger
from uuid import UUID
from schemas import ParseResultSchema

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

    async def get_new_task(self, key: str, timeout: float = 0) -> UUID:
        result = await self.client.blpop(key, timeout=timeout)
        _, task_id_bytes = result
        task_id = task_id_bytes.decode('utf8')
        logger.info(f"[Воркер] Поймал новую задачу {task_id} из Redis!")
        return task_id

    async def send_task_update(self, task_result: ParseResultSchema):

        channel_name = f'task_updates:{task_result.task_id}'
        message_json = task_result.model_dump_json(exclude={'payload'})
        receivers_count = await self.client.publish(channel_name, message_json)
        logger.info(f"[Парсер] Отправлен JSON-ивент в канал {channel_name}. Получателей: {receivers_count}")

