from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol
from uuid import UUID

from app.models import UserModel


class UserRepository(Protocol):
    async def get_by_email(self, email: str) -> UserModel | None: ...

    async def get(self, uid: UUID | str) -> UserModel | None: ...

    def add(self, user: UserModel) -> UserModel: ...


class UnitOfWork(ABC):
    users: UserRepository

    # events: list[Any]
    # outbox: list[dict]

    @abstractmethod
    async def __aenter__(self) -> "UnitOfWork": ...

    @abstractmethod
    async def __aexit__(self, exc_type, exc, tb) -> None: ...

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...

    # def collect_event(self, evt: Any) -> None:
    #     self.events.append(evt)
    #
    # def add_outbox(self, type_: str, payload: dict) -> None:
    #     self.outbox.append({"type": type_, "payload": payload})
