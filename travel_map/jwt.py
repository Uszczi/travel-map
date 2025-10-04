from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Union
from uuid import uuid4

import jwt
from pydantic import SecretStr

from travel_map.models import UserModel
from travel_map.settings import settings

SecretType = Union[str, SecretStr]
JWT_ALGORITHM = "HS256"


def _get_secret_value(secret: SecretType) -> str:
    if isinstance(secret, SecretStr):
        return secret.get_secret_value()
    return secret


def generate_jwt(
    data: dict,
    secret: SecretType,
    lifetime_seconds: Optional[int] = None,
    algorithm: str = JWT_ALGORITHM,
) -> str:
    payload = data.copy()
    if lifetime_seconds:
        expire = datetime.now(timezone.utc) + timedelta(seconds=lifetime_seconds)
        payload["exp"] = expire
    return jwt.encode(payload, _get_secret_value(secret), algorithm=algorithm)


def decode_jwt(
    encoded_jwt: str,
    secret: SecretType,
    audience: list[str],
    algorithms: list[str] = [JWT_ALGORITHM],
) -> dict[str, Any]:
    return jwt.decode(
        encoded_jwt,
        _get_secret_value(secret),
        audience=audience,
        algorithms=algorithms,
    )


def issue_access_token(user: UserModel) -> str:
    return generate_jwt(
        data={
            "sub": str(user.uuid),
            "aud": "access",
            "typ": "access",
            "jti": str(uuid4()),
        },
        secret=settings.JWT_ACCESS_SECRET,
        lifetime_seconds=settings.JWT_ACCESS_LIFETIME_S,
        algorithm=JWT_ALGORITHM,
    )


def issue_refresh_token(user: UserModel) -> str:
    return generate_jwt(
        data={
            "sub": str(user.uuid),
            "aud": "refresh",
            "typ": "refresh",
            "jti": str(uuid4()),
        },
        secret=settings.JWT_REFRESH_SECRET,
        lifetime_seconds=settings.JWT_REFRESH_LIFETIME_S,
        algorithm=JWT_ALGORITHM,
    )


def issue_activation_token(user: UserModel) -> str:
    data = {
        "sub": str(user.uuid),
        "aud": "activation",
        "typ": "activation",
        "jti": str(uuid4()),
    }
    return generate_jwt(
        data=data,
        secret=settings.JWT_EMAIL_SECRET,
        lifetime_seconds=settings.JWT_ACTIVATION_LIFETIME_S,
        algorithm=JWT_ALGORITHM,
    )
