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

class TrackPositionInterval(enum.IntEnum):
    TEST = 10
    EVERY_HOUR = 3600
    EVERY_3_HOURS = 10800
    EVERY_6_HOURS = 21600
    EVERY_12_HOURS = 43200
    EVERY_DAY = 86400