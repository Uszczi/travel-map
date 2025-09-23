from sqlalchemy import select
from sqlmodel.ext.asyncio.session import AsyncSession

from travel_map.models import UserModel


class SqlUserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str) -> UserModel | None:
        stmt = select(UserModel).where(UserModel.email == email)
        return (await self.session.exec(stmt)).first()

    def add(self, user: UserModel) -> UserModel:
        self.session.add(user)
        return user
