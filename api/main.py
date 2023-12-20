from fastapi import FastAPI

from .group import router as group_router
from .educator import router as educator_router
from .address import router as address_router
from .classroom import router as classroom_router


app = FastAPI(title='Timetable API')

app.include_router(group_router, tags=['Group'], prefix='/api/group')
app.include_router(educator_router, tags=['Educator'], prefix='/api/educator')
app.include_router(address_router, tags=['Address'], prefix='/api/address')
app.include_router(classroom_router, tags=['Classroom'], prefix='/api/classroom')
