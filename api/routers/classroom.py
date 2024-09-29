from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import Event
from api.database import get_async_session
from api.schemas import ClassroomNameListResponse, EventListResponse

router = APIRouter()


@router.get("/", response_model=ClassroomNameListResponse)
async def all_classrooms(session: AsyncSession = Depends(get_async_session)):
    stmt = select(Event.location).group_by(Event.location)
    result = await session.execute(stmt)
    classrooms = result.scalars().all()

    return ClassroomNameListResponse(classrooms=classrooms)


@router.get("/{classroom}/events", response_model=EventListResponse)
async def get_classroom_events(classroom: str,
                               session: AsyncSession = Depends(get_async_session)):
    stmt = select(Event).where(Event.location == classroom)
    result = await session.execute(stmt)
    events = result.scalars().all()

    return EventListResponse(events=events)
