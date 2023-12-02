from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.database import get_db
from api.schemas import EventListResponse

router = APIRouter()


@router.head("/find", response_model=int)
async def educator_id_by_name(first_name: str, last_name: str, middle_name: str, db: Session = Depends(get_db)):
    ...


@router.get("/{educator_id}/events", response_model=EventListResponse)
async def get_educator_events(group_id: int, db: Session = Depends(get_db)):
    ...
