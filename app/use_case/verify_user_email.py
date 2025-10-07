import jwt
from fastapi import HTTPException

from app.domain.ports import UnitOfWork
from app.jwt import decode_jwt
from app.settings import settings

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
