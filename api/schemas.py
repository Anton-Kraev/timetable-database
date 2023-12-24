from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict

config = ConfigDict(
    from_attributes=True, populate_by_name=True, arbitrary_types_allowed=True
)


class GroupBaseSchema(BaseModel):
    id: int
    name: str
    type: str | None = None
    program_id: int | None = None

    model_config = config


class EducatorBaseSchema(BaseModel):
    id: int
    first_name: str
    last_name: str
    middle_name: str

    model_config = config


class EventBaseSchema(BaseModel):
    id: int
    start_time: datetime
    end_time: datetime
    description: str | None = None
    location: str | None = None

    model_config = config


class AddressBaseSchema(BaseModel):
    id: int
    oid: str | None = None
    name: str
    matches: int | None = None

    model_config = config


class ClassroomBaseSchema(BaseModel):
    id: int
    oid: str | None = None
    name: str
    capacity: int | None = None
    seating_type: int | None = None
    additional_info: str | None = None
    address_id: int

    model_config = config


class GroupListResponse(BaseModel):
    groups: List[GroupBaseSchema]


class EducatorListResponse(BaseModel):
    educators: List[EducatorBaseSchema]


class EventListResponse(BaseModel):
    events: List[EventBaseSchema]


class AddressListResponse(BaseModel):
    addresses: List[AddressBaseSchema]


class ClassroomListResponse(BaseModel):
    classrooms: List[ClassroomBaseSchema]