import jwt as pyjwt
from fastapi import HTTPException
from loguru import logger
from pydantic import SecretStr
from sqlmodel import SQLModel

from app.domain.ports import UnitOfWork
from app.jwt import PASSWORD_RESET_AUD, decode_jwt
from app.settings import settings


class ConfirmPasswordResetCommand(SQLModel):
    token: str
    new_password: SecretStr


class ConfirmPasswordResetUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def __call__(self, cmd: ConfirmPasswordResetCommand) -> None:
        logger.debug("Confirming password reset")
        try:
            payload = decode_jwt(
                cmd.token,
                secret=settings.JWT_EMAIL_SECRET,
                audience=[PASSWORD_RESET_AUD],
            )
        except pyjwt.ExpiredSignatureError:
            logger.warning("Password reset token expired")
            raise HTTPException(status_code=400, detail="Reset link expired.")
        except pyjwt.InvalidTokenError:
            logger.warning("Invalid password reset token")
            raise HTTPException(status_code=400, detail="Invalid reset token.")

        if payload.get("typ") != "password_reset":
            logger.warning("Password reset token wrong typ")
            raise HTTPException(status_code=400, detail="Invalid reset token.")

        user_id = payload.get("sub")
        if not user_id:
            logger.warning("Password reset token missing sub")
            raise HTTPException(status_code=400, detail="Invalid reset token.")

        async with self.uow as uow:
            user = await uow.users.get(user_id)
            if not user:
                logger.warning("Password reset user not found: {}", user_id)
                raise HTTPException(status_code=404, detail="User not found.")

            user.hashed_password = cmd.new_password.get_secret_value()

            await uow.commit()
            logger.info("Password reset confirmed for user {}", user_id)
