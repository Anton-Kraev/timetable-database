from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from config import DATABASE_URI

engine = create_async_engine(DATABASE_URI, echo=True)
LocalSession = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)


async def get_async_session():
    session = LocalSession()
    try:
        yield session
    except Exception as e:
        print(e)
        await session.rollback()
    finally:
        await session.close()
