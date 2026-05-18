from db import get_fresh_task_and_set_status, RedisService
from loguru import logger
from scheduler import TaskScheduler
import asyncio

class Atlas:
    def __init__(self):
        self.max_workers = 1
        self.scheduler = TaskScheduler()
        self.redis = RedisService()


    async def worker(self):

        while True:
            result = await self.redis.client.blpop('tasks_queue', timeout=0)
            _, task_id_bytes = result
            task_id = task_id_bytes.decode('utf8')
            logger.info(f"[Воркер] Поймал новую задачу {task_id} из Redis!")
            task = await get_fresh_task_and_set_status(task_id)

            if not task:
                logger.info('Не нашел таску')
                await asyncio.sleep(5)
                continue

            await self.scheduler.handle_new_task(task)




    async def run_workers(self):
        tasks = []
        await self.redis.connect()
        try:
            for _ in range(self.max_workers):
                tasks.append(asyncio.create_task(self.worker()))

            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            await self.redis.close()

