from parsers import ParserMaker
from db import get_oldest_task
from schemas import TaskStatus, ParseResultSchema
from loguru import logger
from saver import Saver
import asyncio

class Atlas:
    def __init__(self):
        self.manager = ParserMaker()
        self.max_workers = 1
        self.saver = Saver()


    async def worker(self):

        while True:
            task = await get_oldest_task()

            if not task:
                logger.info('Не нашел таску')
                await asyncio.sleep(5)
                continue

            result = ParseResultSchema(
                task_id=task.id,
                error_message='Ошибка воркера в try except. ParseResult не был получен',
                status=TaskStatus.failed
            )
            try:
                parser = self.manager.choose(task)
                result: ParseResultSchema = await parser.parse()

            except (Exception, BaseException) as e:
                logger.error(e)
                result = ParseResultSchema(
                    task_id=task.id,
                    error_message=str(e),
                    status=TaskStatus.failed
                )

            finally:
                await self.saver.save(result)



    async def run_workers(self):
        tasks = []
        for _ in range(self.max_workers):
            tasks.append(asyncio.create_task(self.worker()))

        await asyncio.gather(*tasks)

