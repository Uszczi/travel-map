from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import SecretStr

from app.cookies import delete_refresh_cookie, set_refresh_cookie
from app.dependencies import get_current_user
from app.models import UserModel
from app.password import PasswordHelper
from app.serializers.input.user import (
    UserConfimPasswordReset,
    UserDetails,
    UserEmail,
    UserRegister,
    RefreshToken,
)
from app.use_case import (
    get_confirm_password_reset_uc,
    get_login_user_uc,
    get_refresh_token_uc,
    get_register_user_uc,
    get_request_password_reset_uc,
    get_verify_user_email_uc,
)
from app.use_case.confirm_password_reset import (
    ConfirmPasswordResetCommand,
    ConfirmPasswordResetUseCase,
)
from app.use_case.login_user import (
    InvalidCredentials,
    LoginUserCommand,
    LoginUserUserCase,
)
from app.use_case.refresh_user_token import (
    RefreshTokenCommand,
    RefreshTokenUseCase,
)
from app.use_case.register_user import (
    RegisterUserCommand,
    RegisterUserUseCase,
    UserAlreadyRegistered,
)
from app.use_case.request_password_reset import (
    RequestPasswordResetUseCase,
)
from app.use_case.verify_user_email import (
    VerifyUserEmailUseCase,
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
    set_refresh_cookie(resp, tokens.refresh_token)
    return resp


@router.post("/logout")
async def logout():
    resp = JSONResponse({"ok": True})
    delete_refresh_cookie(resp)
    return resp


@router.post("/refresh")
async def refresh(
    data: RefreshToken,
    refresh_cookie: Annotated[str | None, Cookie(alias=REFRESH_COOKIE_NAME)] = None,
    uc: RefreshTokenUseCase = Depends(
        get_refresh_token_uc,
    ),
):
    token = refresh_cookie or (data.refresh_token if data else None)
    if not token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    tokens = await uc(RefreshTokenCommand(refresh_token=token))

    resp = JSONResponse(content=tokens.model_dump())
    set_refresh_cookie(resp, tokens.refresh_token)
    return resp


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
    token: str,
    uc: VerifyUserEmailUseCase = Depends(get_verify_user_email_uc),
):
    msg = await uc(token)
    return msg


@router.post("/password-reset")
async def request_password_reset(
    data: UserEmail,
    uc: RequestPasswordResetUseCase = Depends(get_request_password_reset_uc),
):
    await uc(email=data.email)
    return {"message": "If the email exists, a reset link has been sent."}


@router.post("/password-reset/confirm")
async def confirm_password_reset(
    data: UserConfimPasswordReset,
    uc: ConfirmPasswordResetUseCase = Depends(get_confirm_password_reset_uc),
):
    await uc(
        ConfirmPasswordResetCommand(
            token=data.token,
            new_password=SecretStr(
                PasswordHelper().hash(data.password)  # type: ignore
            ),
        )
    )
    return {"message": "Password changed."}


@router.get("/me")
async def me(user: UserModel = Depends(get_current_user)) -> UserDetails:
    return user  # type: ignore
