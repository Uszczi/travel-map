from datetime import datetime, timezone
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer

from app.db import async_session
from app.domain.ports import UnitOfWork
from app.infrastructure.uow import SqlAlchemyUoW
from app.jwt import decode_jwt
from app.models import UserModel
from app.settings import settings

# TODO remove it from there
ACCESS_COOKIE_NAME = "access_token"
JWT_ALGORITHM = "HS256"
ACCESS_AUD = "access"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login", auto_error=False)


def get_uow() -> SqlAlchemyUoW:
    return SqlAlchemyUoW(async_session)


async def get_current_user(
    request: Request,
    bearer_token: Optional[str] = Depends(oauth2_scheme),
    uow: UnitOfWork = Depends(get_uow),
) -> UserModel:
    exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = bearer_token or request.cookies.get(ACCESS_COOKIE_NAME)

    if not token:
        raise exception

    try:
        payload = decode_jwt(
            token,
            secret=settings.JWT_ACCESS_SECRET,
            audience=[ACCESS_AUD],
            # TODO add default algorithms
            algorithms=[JWT_ALGORITHM],
        )
        # TODO catch explicit exception
    except Exception:
        raise exception

    user_id = payload.get("sub")
    if user_id is None:
        raise exception

    exp = payload.get("exp")
    if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(
        timezone.utc
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    async with uow as tx:
        user = await tx.users.get(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials.",
                headers={"WWW-Authenticate": "Bearer"},
            )

    return user
