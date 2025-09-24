from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from travel_map.models import UserModel


class SqlUserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, uid: UUID | str) -> UserModel | None:
        result = await self.session.get(UserModel, uid)
        return result

    async def get_by_email(self, email: str) -> UserModel | None:
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self.session.exec(stmt)
        return result.first()

    def add(self, user: UserModel) -> UserModel:
        self.session.add(user)
        return user
