from typing import Optional, Union

from loguru import logger
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher


class PasswordHelper:
    def __init__(self, password_hash: Optional[PasswordHash] = None) -> None:
        if password_hash is None:
            self.password_hash = PasswordHash((Argon2Hasher(),))
        else:
            self.password_hash = password_hash

    def verify(
        self, plain_password: str, hashed_password: str
    ) -> tuple[bool, Union[str, None]]:
        result = self.password_hash.verify(plain_password, hashed_password)
        logger.debug("Password verification: {}", result[0])
        return result

    def hash(self, password: str) -> str:
        hashed = self.password_hash.hash(password)
        logger.debug("Password hashed")
        return hashed

    # def generate(self) -> str:
    #     return secrets.token_urlsafe()
