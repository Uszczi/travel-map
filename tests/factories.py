from __future__ import annotations

import secrets
from datetime import datetime
from typing import NotRequired, TypedDict, Unpack
from uuid import UUID

import factory
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import UserModel


class UserFactory(factory.Factory):
    class Meta:
        model = UserModel

    email = factory.Faker("email")
    hashed_password = factory.LazyFunction(lambda: "hashed$" + secrets.token_hex(16))


class UserCreateKw(TypedDict, total=False):
    email: str
    hashed_password: str
    uuid: NotRequired[UUID]
    created_at: NotRequired[datetime]
    updated_at: NotRequired[datetime]


async def acreate_user(
    session: AsyncSession, commit: bool = True, **kwargs: Unpack[UserCreateKw]
) -> UserModel:
    obj = UserFactory.build(**kwargs)
    session.add(obj)
    if commit:
        await session.commit()
    else:
        await session.flush()

    await session.refresh(obj)
    return obj
