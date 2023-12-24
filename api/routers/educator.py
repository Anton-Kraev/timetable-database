from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, join
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.models.educator import Educator
from app.models.educator_to_event import EducatorToEvent
from app.models.event import Event
from api.database import get_async_session
from api.schemas import EventListResponse, EducatorListResponse

router = APIRouter()


@router.get("/all", response_model=EducatorListResponse)
async def all_educators(session: AsyncSession = Depends(get_async_session)):
    stmt = select(Educator)
    result = await session.execute(stmt)
    educators = result.scalars().all()

    return EducatorListResponse(educators=educators)


@router.get("/find", response_model=int)
async def educator_id_by_name(first_name: str, last_name: str, middle_name: str,
                              session: AsyncSession = Depends(get_async_session)):
    stmt = select(Educator.id).where((Educator.first_name == first_name)
                                          & (Educator.last_name == last_name)
                                          & (Educator.middle_name == middle_name))
    result = await session.execute(stmt)
    educator_id = result.scalar_one_or_none()

    if not educator_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No educator with name {first_name} {last_name} {middle_name} found'
        )
    return educator_id


@router.get("/{educator_id}/events", response_model=EventListResponse)
async def get_educator_events(educator_id: int,
                              session: AsyncSession = Depends(get_async_session)):
    stmt = select(Event).select_from(
        join(Event, EducatorToEvent, Event.id == EducatorToEvent.event_id)
    ).where(EducatorToEvent.educator_id == educator_id)
    result = await session.execute(stmt)
    events = result.scalars().all()

    return EventListResponse(events=events)
