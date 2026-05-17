from loguru import logger
from schemas import ParseResultSchema, FetchCardsResultSchema, TrackPositionsResultSchema, TaskStatus
from db import set_task_status, save_fetch_cards_batch, save_track_positions_batch, get_db
from sqlalchemy.ext.asyncio import AsyncSession
from itertools import islice
from typing import Iterable


class Saver:
    def __init__(self):
        self.session_maker = get_db


    @staticmethod
    def chunked_iterable(iterable: Iterable, size: int):
        it = iter(iterable)
        while True:
            chunk = list(islice(it, size))
            if not chunk:
                break
            yield chunk

    async def fetch_cards_save(self, session: AsyncSession, parse_result: ParseResultSchema):
        batch_size = 500
        processed_count = 0
        payload: FetchCardsResultSchema | TrackPositionsResultSchema = parse_result.payload

        try:
            for batch in self.chunked_iterable(payload.items, batch_size):
                    await save_fetch_cards_batch(session, batch, parse_result.task_id)
                    processed_count += len(batch)
                    logger.success(f"Сохранено {processed_count} из {len(payload.items)}")
        except Exception as e:
            logger.exception(e)
            logger.error(f'Ошибка в батче {e}')
            parse_result.status = TaskStatus.failed
            parse_result.error_message = str(e)


    async def track_positions_save(self, session: AsyncSession, parse_result: ParseResultSchema):
        batch_size = 500
        processed_count = 0
        payload: TrackPositionsResultSchema = parse_result.payload

        try:
            for batch in self.chunked_iterable(payload.positions, batch_size):
                await save_track_positions_batch(session, batch, parse_result.task_id)
                processed_count += len(batch)
                logger.success(f"Сохранено {processed_count} из {len(payload.positions)}")

        except (Exception, BaseException) as e:
            logger.exception(e)
            logger.error(f'Ошибка в батче {e}')
            parse_result.status = TaskStatus.failed
            parse_result.error_message = str(e)



    async def save(self, parse_result: ParseResultSchema):
        total_found = 0

        async with self.session_maker() as session:
            payload = parse_result.payload

            if isinstance(payload, FetchCardsResultSchema):
                total_found = len(payload.items)
                await self.fetch_cards_save(session, parse_result)

            if isinstance(payload, TrackPositionsResultSchema):
                total_found = len(payload.items)
                await self.fetch_cards_save(session, parse_result)
                await self.track_positions_save(session, parse_result)

            await set_task_status(session, parse_result.task_id, parse_result.status, total_found, parse_result.error_message)





