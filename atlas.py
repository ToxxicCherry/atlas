from db import get_oldest_task
from loguru import logger
from scheduler import TaskScheduler
import asyncio

class Atlas:
    def __init__(self):
        self.max_workers = 1
        self.scheduler = TaskScheduler()


    async def worker(self):

        while True:
            task = await get_oldest_task()

            if not task:
                logger.info('Не нашел таску')
                await asyncio.sleep(5)
                continue

            await self.scheduler.handle_new_task(task)




    async def run_workers(self):
        tasks = []
        for _ in range(self.max_workers):
            tasks.append(asyncio.create_task(self.worker()))

        await asyncio.gather(*tasks)

