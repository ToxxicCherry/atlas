from db import get_fresh_task_and_set_status, RedisService
from loguru import logger
from scheduler import TaskScheduler
from schemas import TaskStatus
import asyncio

class Atlas:
    def __init__(self):
        self.max_workers = 1
        self.redis = RedisService()
        self.scheduler = TaskScheduler(self.redis)



    async def worker(self):

        while True:
            task_id = await self.redis.get_new_task('tasks_queue', timeout=0)
            task = await get_fresh_task_and_set_status(task_id, TaskStatus.processing)
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

