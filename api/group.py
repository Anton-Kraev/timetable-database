from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.database import get_db
from api.schemas import EventListResponse

router = APIRouter()


@router.head("/find",  response_model=int)
def group_id_by_name(name: str, db: Session = Depends(get_db)):
    ...


@router.get("/{group_id}/events", response_model=EventListResponse)
async def get_group_events(group_id: int):
    ...
