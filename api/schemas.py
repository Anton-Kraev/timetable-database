from datetime import datetime
from typing import List

from pydantic import BaseModel


class EventBaseSchema(BaseModel):
    id: int
    start_time: datetime
    end_time: datetime
    description: str | None
    location: str | None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class EventListResponse(BaseModel):
    status: str
    results: int
    events: List[EventBaseSchema]
