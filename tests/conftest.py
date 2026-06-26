import pytest
from typing import AsyncIterator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession


from unittest.mock import patch
from pydantic import SecretStr
from app.settings import Settings


@pytest.fixture
def test_settings():
    return Settings(
        ENV="test",
        MONGO_URL="mongodb://test:27017",
        DB_CONNECTION_STR="sqlite+aiosqlite:///test.db",
        DB_ASYNC_CONNECTION_STR="sqlite+aiosqlite:///test.db",
        REDIS_URL="redis://localhost:6379/0",
        REDIS_HOST="localhost",
        ALLOWED_ORIGINS=["*"],
        URL_PREFIX="",
        SENTRY_SDK="",
        NOMINATIM_URL="",
        NOMINATIM_REVERSE_URL="",
        NOMINATIM_USER_AGENT="test",
        NOMINATIM_ACCESS_TOKEN="",
        PROMETHEUS_MULTIPROC_DIR="/tmp/prometheus_multiproc",
        APP_BASE_URL="http://test",
        JWT_ACCESS_SECRET=SecretStr("test-access"),
        JWT_REFRESH_SECRET=SecretStr("test-refresh"),
        JWT_EMAIL_SECRET=SecretStr("test-email"),
        MAIL_SERVER="mailhog",
        MAIL_PORT=1025,
        MAIL_STARTTLS=False,
        MAIL_SSL_TLS=False,
        MAIL_VALIDATE_CERTS=False,
    )


@pytest.fixture(autouse=True)
def mock_settings(test_settings):
    with patch("app.settings.settings", test_settings):
        yield


from app.app import app
from app.db import async_engine


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest_asyncio.fixture(scope="function")
async def async_session() -> AsyncIterator[AsyncSession]:
    session = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

    async with session() as s:
        async with async_engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

        yield s

    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await async_engine.dispose()
