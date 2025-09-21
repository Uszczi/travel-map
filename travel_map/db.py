from typing import AsyncIterator

from pymongo import MongoClient
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import create_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from travel_map.settings import settings

client = MongoClient(settings.MONGO_URL)
strava_db = client["strava_db"]

engine = create_engine(settings.DB_CONNECTION_STR, echo=True)
async_engine = create_async_engine(
    settings.DB_ASYNC_CONNECTION_STR, echo=True, future=True
)


async def get_async_session() -> AsyncIterator[AsyncSession]:
    async_session = sessionmaker(
        bind=async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
