from fastapi import FastAPI

from api.group import router as group_router
from api.educator import router as educator_router

app = FastAPI(title='Timetable API')

app.include_router(group_router, tags=['Group'], prefix='/api/group')
app.include_router(educator_router, tags=['Educator'], prefix='/api/educator')
