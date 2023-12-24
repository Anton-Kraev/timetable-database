from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.address import Address
from api.database import get_async_session
from api.schemas import AddressListResponse

router = APIRouter()


@router.get("/all", response_model=AddressListResponse)
async def all_addresses(session: AsyncSession = Depends(get_async_session)):
    stmt = select(Address)
    result = await session.execute(stmt)
    addresses = result.scalars().all()

    return AddressListResponse(addresses=addresses)
