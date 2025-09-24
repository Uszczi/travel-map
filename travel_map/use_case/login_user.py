from pydantic import BaseModel, SecretStr

from travel_map.domain.ports import UnitOfWork
from travel_map.jwt import issue_access_token, issue_refresh_token
from travel_map.password import PasswordHelper


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
