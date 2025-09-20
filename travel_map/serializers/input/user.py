import re
from typing import Annotated

from pydantic import EmailStr, StringConstraints, field_validator
from sqlmodel import SQLModel


class UserRegister(SQLModel):
    email: EmailStr
    password: Annotated[str, StringConstraints(min_length=8, max_length=72)]

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if not re.search(r"[a-z]", v):
            raise ValueError("Hasło musi zawierać przynajmniej jedną małą literę.")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Hasło musi zawierać przynajmniej jedną wielką literę.")
        if not re.search(r"\d", v):
            raise ValueError("Hasło musi zawierać przynajmniej jedną cyfrę.")
        if not re.search(r"[^\w\s]", v):
            raise ValueError("Hasło musi zawierać przynajmniej jeden znak specjalny.")
        return v
