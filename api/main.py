from fastapi import FastAPI

from .group import router as group_router
from .educator import router as educator_router

app = FastAPI(title='Timetable API')

app.include_router(group_router, tags=['Group'], prefix='/api/group')
app.include_router(educator_router, tags=['Educator'], prefix='/api/educator')
