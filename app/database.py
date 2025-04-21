from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from config import settings


async_engine = create_async_engine(url=settings.DATABASE_URL_asyncpg, echo=True)
local_session = async_sessionmaker(bind=async_engine, expire_on_commit=False)


async def get_db():
    async with local_session() as session:
        yield session