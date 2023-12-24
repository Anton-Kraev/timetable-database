from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, join
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.models.event import Event
from app.models.group import Group
from app.models.group_to_event import GroupToEvent
from api.database import get_async_session
from api.schemas import EventListResponse, GroupListResponse

router = APIRouter()


@router.get("/all", response_model=GroupListResponse)
async def all_groups(session: AsyncSession = Depends(get_async_session)):
    stmt = select(Group)
    result = await session.execute(stmt)
    groups = result.scalars().all()

    return GroupListResponse(groups=groups)


@router.get("/find",  response_model=int)
async def group_id_by_name(name: str,
                           session: AsyncSession = Depends(get_async_session)):
    stmt = select(Group.id).where(Group.name == name)
    result = await session.execute(stmt)
    group_id = result.scalar_one_or_none()

    if not group_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No group with name {name} found'
        )
    return group_id


@router.get("/{group_id}/events", response_model=EventListResponse)
async def get_group_events(group_id: int,
                           session: AsyncSession = Depends(get_async_session)):
    stmt = select(Event).select_from(
        join(Event, GroupToEvent, Event.id == GroupToEvent.event_id)
    ).where(GroupToEvent.group_id == group_id)
    result = await session.execute(stmt)
    events = result.scalars().all()

    return EventListResponse(events=events)
