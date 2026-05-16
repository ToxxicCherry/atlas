from pydantic import BaseModel, ConfigDict
from typing import List, Literal
from .enums import *


class FetchCardsPayloadSchema(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    type: Literal[TaskType.fetch_cards] = TaskType.fetch_cards
    query: str

class TrackPositionPayloadSchema(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    type: Literal[TaskType.track_positions] = TaskType.track_positions
    query: str
    articles: List[int]



