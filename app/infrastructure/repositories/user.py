from uuid import UUID

from loguru import logger
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import UserModel


class SqlUserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, uid: UUID | str) -> UserModel | None:
        logger.debug("UserRepository.get: {}", uid)
        result = await self.session.get(UserModel, uid)
        logger.debug("UserRepository.get: {} -> {}", uid, result is not None)
        return result

    async def get_by_email(self, email: str) -> UserModel | None:
        logger.debug("UserRepository.get_by_email: {}", email)
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self.session.exec(stmt)
        user = result.first()
        logger.debug("UserRepository.get_by_email: {} -> {}", email, user is not None)
        return user

    def add(self, user: UserModel) -> UserModel:
        logger.debug("UserRepository.add: {} ({})", user.email, user.uuid)
        self.session.add(user)
        return user
