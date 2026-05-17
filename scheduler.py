import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from db import get_db, TaskModel, update_task_iterations, get_task_by_id
from schemas import ParseResultSchema, TaskStatus
from parsers import ParserMaker
from uuid import UUID
from loguru import logger
from saver import Saver
from datetime import datetime, timezone


class TaskScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler(timezone=timezone.utc)
        self.scheduler.start()
        self.session_maker = get_db
        self.manager = ParserMaker()
        self.saver = Saver()
        self.lock = asyncio.Lock()

    async def run_interval_parsing(self, task_id: UUID):
        logger.info(f"[TaskScheduler] Проверка и запуск задачи {task_id}")
        async with self.lock:

            task = await get_task_by_id(task_id)

            if not task:
                logger.warning(f"Задача {task_id} удалена из БД. Снимаем с таймера.")
                self.scheduler.remove_job(str(task_id))
                return

            if task.status == TaskStatus.failed or task.status == TaskStatus.completed:
                logger.info(f"Задача {task_id} остановлена со статусом {task.status}. Удаляем джобу.")
                self.scheduler.remove_job(str(task_id))
                return

            result = ParseResultSchema(
                task_id=task.id,
                error_message='Ошибка воркера в try except. ParseResult не был получен',
                status=TaskStatus.failed
            )

            try:
                parser = self.manager.choose(task)
                result: ParseResultSchema = await parser.parse()

                task.iterations_left -= 1
                await update_task_iterations(task.id, task.iterations_left)
                logger.info(f"У задачи {task_id} осталось запусков: {task.iterations_left}")

                if task.iterations_left <= 0:
                    result.status = TaskStatus.completed
                    self.scheduler.remove_job(str(task_id))
                    logger.info(f"Задача {task_id} полностью завершила свой цикл мониторинга и удалена из планировщика.")


            except (Exception, BaseException) as e:
                logger.error(e)
                result = ParseResultSchema(
                    task_id=task.id,
                    error_message=str(e),
                    status=TaskStatus.failed
                )
            finally:
                await self.saver.save(result)

    async def run_single_parsing(self, task_id: UUID):
        logger.info(f"[TaskScheduler] Запуск разовой задачи {task_id}")
        async with self.lock:

            task = await get_task_by_id(task_id)
            if not task:
                return

            result = ParseResultSchema(
                task_id=task.id,
                error_message='Ошибка воркера в try except. ParseResult не был получен',
                status=TaskStatus.failed
            )

            try:
                parser = self.manager.choose(task)
                result: ParseResultSchema = await parser.parse()
                result.status = TaskStatus.completed
            except (Exception, BaseException) as e:
                logger.error(e)
                result = ParseResultSchema(
                    task_id=task_id,
                    error_message=str(e),
                    status=TaskStatus.failed
                )
            finally:
                await self.saver.save(result)


    async def handle_new_task(self, task: TaskModel):

        if task.track_interval and task.iterations_left > 1:
            self.scheduler.add_job(
                self.run_interval_parsing,
                trigger=IntervalTrigger(seconds=task.track_interval),
                args=[task.id],
                id=str(task.id),
                next_run_time=datetime.now(timezone.utc),
                replace_existing=True,
            )
            logger.info(f"Задача {task.id} встала на мониторинг. Осталось итераций: {task.iterations_left}")
        else:
            self.scheduler.add_job(
                self.run_single_parsing,
                args=[task.id],
                id=str(task.id),
                next_run_time=datetime.now(timezone.utc),
                replace_existing=True,
            )




