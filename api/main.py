from fastapi import FastAPI

from api.routers import group_router, educator_router, address_router, classroom_router

app = FastAPI(title='Timetable API')

app.include_router(group_router, tags=['Group'], prefix='/api/groups')
app.include_router(educator_router, tags=['Educator'], prefix='/api/educators')
app.include_router(address_router, tags=['Address'], prefix='/api/addresses')
app.include_router(classroom_router, tags=['Classroom'], prefix='/api/classrooms')
