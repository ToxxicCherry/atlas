from pydantic import BaseModel


class PositionSchema(BaseModel):
    product_id: int
    position: int
