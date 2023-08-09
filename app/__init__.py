from sqlalchemy.ext.asyncio import create_async_engine
from config import DATABASE_URI

engine = create_async_engine(DATABASE_URI)