import jwt
from fastapi import HTTPException, status
from pydantic import BaseModel

from app.domain.ports import UnitOfWork
from app.jwt import (
    JWT_ALGORITHM,
    decode_jwt,
    issue_access_token,
    issue_refresh_token,
)
from app.settings import settings
from app.use_case.login_user import TokenPair


class RefreshTokenCommand(BaseModel):
    refresh_token: str


class RefreshTokenUseCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def __call__(self, cmd: RefreshTokenCommand) -> TokenPair:
        async with self.uow as uow:
            try:
                payload = decode_jwt(
                    encoded_jwt=cmd.refresh_token,
                    secret=settings.JWT_REFRESH_SECRET,
                    audience=["refresh"],
                    algorithms=[JWT_ALGORITHM],
                )
            except jwt.ExpiredSignatureError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Refresh token expired",
                )
            except jwt.InvalidTokenError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token",
                )

            sub = payload.get("sub")
            if not sub:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token (no sub)",
                )

            user = await uow.users.get(sub)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token",
                )

            new_access = issue_access_token(user)
            new_refresh = issue_refresh_token(user)

            return TokenPair(
                access_token=new_access,
                refresh_token=new_refresh,
            )
