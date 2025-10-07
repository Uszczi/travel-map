from pydantic import EmailStr

from app.domain.locale import Locale
from app.domain.ports import UnitOfWork
from app.jwt import issue_password_reset_token
from app.services.email import EmailService, send_password_reset_email
from app.settings import settings


class RequestPasswordResetUseCase:
    def __init__(self, uow: UnitOfWork, email_service: EmailService):
        self.uow = uow
        self.email_service = email_service

    async def __call__(self, email: EmailStr) -> None:
        async with self.uow as uow:
            user = await uow.users.get_by_email(email)
        if not user:
            return

        token = issue_password_reset_token(user)
        # TODO this url is wrong, there should be to frontend
        reset_url = f"{settings.APP_BASE_URL}/password-reset?token={token}"

        await send_password_reset_email(
            email_service=self.email_service,
            recipient_email=user.email,
            # TODO use user locale
            locale=Locale.PL,
            reset_url=reset_url,
        )
