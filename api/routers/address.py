from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.address import Address
from api.database import get_async_session
from api.schemas import AddressListResponse, ClassroomListResponse
from app.models.classroom import Classroom

router = APIRouter()


@router.get("/", response_model=AddressListResponse)
async def all_addresses(session: AsyncSession = Depends(get_async_session)):
    stmt = select(Address)
    result = await session.execute(stmt)
    addresses = result.scalars().all()

    return AddressListResponse(addresses=addresses)


@router.get("/{address_id}/classrooms", response_model=ClassroomListResponse)
async def classrooms_at_address(address_id: int, session: AsyncSession = Depends(get_async_session)):
    stmt = select(Classroom).where(Classroom.address_id == address_id)
    result = await session.execute(stmt)
    classrooms = result.scalars().all()

    return ClassroomListResponse(classrooms=classrooms)
