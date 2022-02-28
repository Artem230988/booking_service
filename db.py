from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/hotel"
engine = create_async_engine(DATABASE_URL, echo=True, future=True)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
