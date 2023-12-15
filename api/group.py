from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.models.group import Group
from .database import get_async_session
from .schemas import EventListResponse

router = APIRouter()


@router.get("/find",  response_model=int)
async def group_id_by_name(name: str, session: AsyncSession = Depends(get_async_session)):
    stmt = select(Group.id).where(Group.name == name)
    result = await session.execute(stmt)
    group_id = result.scalar_one_or_none()

    if not group_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No group with name {name} found')
    return group_id


@router.get("/{group_id}/events", response_model=EventListResponse)
async def get_group_events(group_id: int):
    ...
