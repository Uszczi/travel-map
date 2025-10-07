from pydantic import BaseModel, EmailStr

from app.domain.locale import Locale
from app.domain.ports import UnitOfWork
from app.jwt import issue_activation_token
from app.models import UserModel
from app.services.email import EmailService, send_activation_email
from app.settings import settings


class RegisterUserCommand(BaseModel):
    email: EmailStr
    hashed_password: str
    locale: Locale = Locale.PL


class UserAlreadyRegistered(Exception):
    pass


class RegisterUserUseCase:
    def __init__(self, uow: UnitOfWork, email_service: EmailService):
        self.uow = uow
        self.email_service = email_service

    async def __call__(self, cmd: RegisterUserCommand) -> UserModel:
        async with self.uow as uow:
            existing = await uow.users.get_by_email(cmd.email)
            if existing:
                raise UserAlreadyRegistered()

            user = UserModel(**cmd.model_dump())

            uow.users.add(user)
            await uow.commit()

        token = issue_activation_token(user)
        activation_url = f"{settings.APP_BASE_URL}/activate?token={token}"

        await send_activation_email(
            email_service=self.email_service,
            recipient_email=cmd.email,
            locale=cmd.locale,
            activation_url=activation_url,
        )
        return user
