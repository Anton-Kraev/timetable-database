from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.operators import or_
from starlette import status
from starlette.exceptions import HTTPException

from app.models.classroom import Classroom
from app.models.event import Event
from api.database import get_async_session
from api.schemas import ClassroomListResponse, EventListResponse

router = APIRouter()


@router.get("/at_address", response_model=ClassroomListResponse)
async def classrooms_at_address(address_id: int, session: AsyncSession = Depends(get_async_session)):
    stmt = select(Classroom).where(Classroom.address_id == address_id)
    result = await session.execute(stmt)
    classrooms = result.scalars().all()

    return ClassroomListResponse(classrooms=classrooms)


@router.get("/{classroom}/events", response_model=EventListResponse)
async def get_classroom_events(classroom: str,
                               session: AsyncSession = Depends(get_async_session)):
    stmt = select(Event).where(Event.location.like(f'%{classroom}%'))
    result = await session.execute(stmt)
    events = result.scalars().all()

    return EventListResponse(events=events)


@router.post("/events", response_model=EventListResponse)
async def get_events_in_classrooms(classrooms: List[str],
                                   session: AsyncSession = Depends(get_async_session)):
    if not classrooms:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'Expected non-empty classrooms list')

    conditions = [Event.location.like(f'%{c}%') for c in classrooms]
    stmt = select(Event).where(
        conditions[0] if len(conditions) == 1 else or_(*conditions)
    )
    result = await session.execute(stmt)
    events = result.scalars().all()

    return EventListResponse(events=events)
