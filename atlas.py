from parsers import ParserMaker
from db import db_actions
from schemas.db_schemas import TaskStatus
from schemas.parsers_schemas import ParseResult
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
            task = await db_actions.get_oldest_task()

            if not task:
                logger.info('Не нашел таску')
                await asyncio.sleep(5)
                continue

            result = ParseResult(
                task_id=task.id,
                error_message='Ошибка воркера в try except. ParseResult не был получен',
                status=TaskStatus.failed
            )
            try:
                parser = self.manager.choose(task)
                result: ParseResult = await parser.parse()

            except (Exception, BaseException) as e:
                logger.error(e)
                result = ParseResult(
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

