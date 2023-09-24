from typing import Any

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine, async_sessionmaker
from sqlalchemy.orm import as_declarative, declared_attr

from app.core.security import settings


@as_declarative()
class Base(object):
    id: Any
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


def create_engine(testing_flag=settings.TESTING) -> AsyncEngine:
    if testing_flag:
        result_engine = create_async_engine(settings.DATABASE_URL_FOR_TEST, echo=True)
    else:
        result_engine = create_async_engine(settings.DATABASE_URL, echo=False)
    return result_engine


engine = create_engine()
async_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
