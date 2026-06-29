import jwt
from fastapi import HTTPException
from loguru import logger

from app.domain.ports import UnitOfWork
from app.jwt import decode_jwt
from app.settings import settings

ACTIVATION_AUD = "activation"


class VerifyUserEmailUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def __call__(self, token: str) -> str:
        logger.debug("Verifying email activation token")
        try:
            payload = decode_jwt(
                token,
                secret=settings.JWT_EMAIL_SECRET,
                audience=[ACTIVATION_AUD],
            )
        except jwt.ExpiredSignatureError:
            logger.warning("Activation token expired")
            raise HTTPException(status_code=400, detail="Activation link expired.")
        except jwt.InvalidTokenError:
            logger.warning("Invalid activation token")
            raise HTTPException(status_code=400, detail="Invalid activation token.")

        user_id = payload.get("sub")
        token_typ = payload.get("typ")

        if token_typ != "activation" or not user_id:
            logger.warning("Activation token invalid typ or missing sub")
            raise HTTPException(status_code=400, detail="Invalid activation token.")

        async with self.uow as tx:
            user = await tx.users.get(user_id)
            if not user:
                logger.warning("Activation user not found: {}", user_id)
                raise HTTPException(status_code=404, detail="User not found.")

            if user.is_email_verified:
                logger.info("User {} already active", user_id)
                return "already_active"

            user.is_email_verified = True
            await tx.commit()

        logger.info("User {} activated", user_id)
        return "activated"
