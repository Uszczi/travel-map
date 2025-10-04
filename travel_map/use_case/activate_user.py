from pydantic import BaseModel, EmailStr
import jwt

from fastapi import Depends, HTTPException, Request, status
from travel_map.settings import settings
from travel_map.domain.locale import Locale
from travel_map.domain.ports import UnitOfWork
from travel_map.jwt import decode_jwt, issue_activation_token
from travel_map.models import UserModel
from travel_map.services.email import EmailService, send_activation_email

ACTIVATION_AUD = "activation"


class VerifyUserEmailUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def __call__(self, token: str) -> str:
        try:
            payload = decode_jwt(
                token,
                secret=settings.JWT_EMAIL_SECRET,
                audience=[ACTIVATION_AUD],
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=400, detail="Activation link expired.")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=400, detail="Invalid activation token.")

        user_id = payload.get("sub")
        token_typ = payload.get("typ")

        if token_typ != "activation" or not user_id:
            raise HTTPException(status_code=400, detail="Invalid activation token.")

        async with self.uow as tx:
            user = await tx.users.get(user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found.")

            if user.is_email_verified:
                return "already_active"

            user.is_email_verified = True
            await tx.commit()

        return "activated"
