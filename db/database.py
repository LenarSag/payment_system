import os

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from models.user import Base


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@db:5432/postgres"
)
async_engine = create_async_engine(DATABASE_URL, echo=True)

# DATABASE_URL = "db.sqlite3"
# async_engine = create_async_engine(
#     f"sqlite+aiosqlite:///{DATABASE_URL}", echo=True
# )

async_session = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)


async def init_models():
    async with async_engine.begin() as conn:
        existing_tables = await conn.run_sync(Base.metadata.reflect)
        if not existing_tables:
            await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
