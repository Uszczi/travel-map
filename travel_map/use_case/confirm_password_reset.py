import jwt as pyjwt
from fastapi import HTTPException
from pydantic import SecretStr
from sqlmodel import SQLModel

from travel_map.domain.ports import UnitOfWork
from travel_map.jwt import PASSWORD_RESET_AUD, decode_jwt
from travel_map.settings import settings


class ConfirmPasswordResetCommand(SQLModel):
    token: str
    new_password: SecretStr


class ConfirmPasswordResetUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def __call__(self, cmd: ConfirmPasswordResetCommand) -> None:
        try:
            payload = decode_jwt(
                cmd.token,
                secret=settings.JWT_EMAIL_SECRET,
                audience=[PASSWORD_RESET_AUD],
            )
        except pyjwt.ExpiredSignatureError:
            raise HTTPException(status_code=400, detail="Reset link expired.")
        except pyjwt.InvalidTokenError:
            raise HTTPException(status_code=400, detail="Invalid reset token.")

        if payload.get("typ") != "password_reset":
            raise HTTPException(status_code=400, detail="Invalid reset token.")

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=400, detail="Invalid reset token.")

        async with self.uow as uow:
            user = await uow.users.get(user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found.")

            user.hashed_password = cmd.new_password.get_secret_value()

            await uow.commit()
