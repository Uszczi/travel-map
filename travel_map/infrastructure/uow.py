from __future__ import annotations

from typing import Callable

# TODO import from sqlmodel
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from travel_map.domain.ports import UnitOfWork

from .repositories.user import SqlUserRepository


class SqlAlchemyUoW(UnitOfWork):
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession] | Callable[[], AsyncSession],
    ):
        self._session_factory = session_factory
        self.session: AsyncSession | None = None

        # # publiczne „koszyki”
        # self.events: list[object] = []
        # self.outbox: list[dict] = []

        self.users = None

    async def __aenter__(self):
        self.session = self._session_factory()
        await self.session.__aenter__()
        self._tx = await self.session.begin()

        self.users = SqlUserRepository(self.session)
        # self.events.clear()
        # self.outbox.clear()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        try:
            if exc_type:
                await self.rollback()
            else:
                if self._tx.is_active:
                    await self.commit()
        finally:
            await self.session.__aexit__(exc_type, exc, tb)  # type: ignore[attr-defined]
            self.session = None

    async def commit(self):
        await self.session.flush()
        await self._tx.commit()

    async def rollback(self):
        if self._tx.is_active:
            await self._tx.rollback()
