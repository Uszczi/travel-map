from pydantic import BaseModel, SecretStr

from app.domain.ports import UnitOfWork
from app.jwt import issue_access_token, issue_refresh_token
from app.password import PasswordHelper


class LoginUserCommand(BaseModel):
    username: str
    password: SecretStr


class InvalidCredentials(Exception): ...


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str


class RefreshInput(BaseModel):
    refresh_token: str


class LoginUserUserCase:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def __call__(self, cmd: LoginUserCommand) -> TokenPair:
        async with self.uow as uow:
            user = await uow.users.get_by_email(cmd.username)
            if not user:
                raise InvalidCredentials()

            if not PasswordHelper().verify(
                cmd.password.get_secret_value(), user.hashed_password
            ):
                raise InvalidCredentials()

        access = issue_access_token(user)
        refresh = issue_refresh_token(user)

        return TokenPair(
            access_token=access,
            refresh_token=refresh,
        )
