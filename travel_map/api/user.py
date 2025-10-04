from typing import Annotated

import jwt
from fastapi import APIRouter, HTTPException
from travel_map.settings import settings
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import SecretStr

from travel_map.dependencies import get_current_user
from travel_map.models import UserModel
from travel_map.password import PasswordHelper
from travel_map.serializers.input.user import UserDetails, UserRegister
from travel_map.use_case import (
    get_verify_user_email_uc,
    get_login_user_uc,
    get_refresh_token_uc,
    get_register_user_uc,
)
from travel_map.use_case.activate_user import (
    VerifyUserEmailUseCase,
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

# TODO remove it from there
JWT_ALGORITHM = "HS256"
ACCESS_AUD = "access"
REFRESH_AUD = "refresh"

ACCESS_COOKIE_NAME = "access_token"
REFRESH_COOKIE_NAME = "refresh_token"
# W dev na http://localhost ustaw SECURE_COOKIES=False. W produkcji -> True (HTTPS)!
SECURE_COOKIES = False
# Jeżeli znasz realny czas życia tokenów, wpisz go tu (sekundy).
ACCESS_COOKIE_MAX_AGE = 15 * 60  # 15 min
REFRESH_COOKIE_MAX_AGE = 30 * 24 * 3600  # 30 dni


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
        raise HTTPException(status_code=400, detail="Invalid username or password.")

    resp = JSONResponse(content=tokens.model_dump())

    resp.set_cookie(
        key=ACCESS_COOKIE_NAME,
        value=tokens.access_token,
        httponly=True,
        secure=SECURE_COOKIES,
        samesite="lax",
        max_age=ACCESS_COOKIE_MAX_AGE,
        path="/",
    )
    resp.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=tokens.refresh_token,
        httponly=True,
        secure=SECURE_COOKIES,
        samesite="lax",
        max_age=REFRESH_COOKIE_MAX_AGE,
        path="/",
    )
    return resp


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


@router.get("/activate")
async def activate_account(
    token: str, uc: VerifyUserEmailUseCase = Depends(get_verify_user_email_uc)
):
    msg = await uc(token)
    return msg


@router.get("/me")
async def me(user: UserModel = Depends(get_current_user)) -> UserDetails:
    return user  # type: ignore
