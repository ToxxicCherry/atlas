from db.models import TaskModel
from schemas.db_schemas import MarketPlace, TaskType
from .wb import WBCardsFetcher, PositionsFetcher
from .base import BaseParser

class ParserMaker:
    def __init__(self):
        self.parsers = {

            MarketPlace.wildberries: {
                TaskType.fetch_cards: WBCardsFetcher,
                TaskType.track_positions: PositionsFetcher
            },
            MarketPlace.ozon: {

            }

        }

    def choose(self, task: TaskModel) -> BaseParser:
        parser = self.parsers.get(task.source, {}).get(task.type)


        if not parser:
            raise ValueError(f"Нет реализации парсера для {task.source}, {task.type}")
        return parser(task)