import enum

class TaskType(enum.Enum):
    fetch_cards = "fetch_cards"
    track_positions = "track_positions"

class MarketPlace(enum.Enum):
    wildberries = 'wildberries'
    ozon = 'ozon'

class TaskStatus(enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"