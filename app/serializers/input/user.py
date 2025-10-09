import re
from typing import Annotated

from pydantic import EmailStr, SecretStr, StringConstraints, field_validator
from sqlmodel import SQLModel


class PasswordSchema(SQLModel):
    password: Annotated[SecretStr, StringConstraints(min_length=8, max_length=72)]

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: SecretStr) -> str:
        vv = v.get_secret_value()
        if not re.search(r"[a-z]", vv):
            raise ValueError("Hasło musi zawierać przynajmniej jedną małą literę.")
        if not re.search(r"[A-Z]", vv):
            raise ValueError("Hasło musi zawierać przynajmniej jedną wielką literę.")
        if not re.search(r"\d", vv):
            raise ValueError("Hasło musi zawierać przynajmniej jedną cyfrę.")
        if not re.search(r"[^\w\s]", vv):
            raise ValueError("Hasło musi zawierać przynajmniej jeden znak specjalny.")
        return vv


class UserRegister(PasswordSchema):
    email: EmailStr


class UserEmail(SQLModel):
    email: EmailStr


class UserConfimPasswordReset(PasswordSchema):
    token: str


class RefreshToken(SQLModel):
    refresh_token: str | None = None


# TODO remove it from there
class UserDetails(SQLModel):
    email: EmailStr
