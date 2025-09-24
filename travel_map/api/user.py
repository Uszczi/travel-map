from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import SecretStr

from travel_map.password import PasswordHelper
from travel_map.serializers.input.user import UserDetails, UserRegister
from travel_map.use_case import (
    get_login_user_uc,
    get_refresh_token_uc,
    get_register_user_uc,
)
from travel_map.use_case.login_user import (
    InvalidCredentials,
    LoginUserCommand,
    LoginUserUserCase,
)
from travel_map.use_case.refresh_user_token import (
    RefreshTokenCommand,
    RefreshTokenUseCase,
)
from travel_map.use_case.register_user import (
    RegisterUserCommand,
    RegisterUserUseCase,
    UserAlreadyRegistered,
)

router = APIRouter()

JWT_ALGORITHM = "HS256"
ACCESS_AUD = "access"
REFRESH_AUD = "refresh"


@router.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    uc: LoginUserUserCase = Depends(get_login_user_uc),
):
    try:
        tokens = await uc(
            LoginUserCommand(
                username=form_data.username, password=SecretStr(form_data.password)
            )
        )
    except InvalidCredentials:
        raise HTTPException(
            status_code=400,
            detail="Invalid username or password.",
        )

    return tokens


@router.post("/refresh")
async def refresh(
    data: RefreshTokenCommand, uc: RefreshTokenUseCase = Depends(get_refresh_token_uc)
):
    tokens = await uc(data)
    return tokens


@router.post("/register")
async def register(
    data: UserRegister, uc: RegisterUserUseCase = Depends(get_register_user_uc)
) -> UserDetails:
    input = data.model_dump()
    input["hashed_password"] = PasswordHelper().hash(input.pop("password"))

    try:
        user = await uc(RegisterUserCommand(**input))  # type: ignore
    except UserAlreadyRegistered:
        raise HTTPException(
            status_code=400,
            detail="Email already used.",
        )

    return user
