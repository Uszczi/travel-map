from fastapi import Depends

from travel_map.dependencies import get_uow
from travel_map.domain.ports import UnitOfWork
from travel_map.services.email import EmailService, get_email_service
from travel_map.use_case.confirm_password_reset import ConfirmPasswordResetUseCase
from travel_map.use_case.login_user import LoginUserUserCase
from travel_map.use_case.refresh_user_token import RefreshTokenUseCase
from travel_map.use_case.register_user import RegisterUserUseCase
from travel_map.use_case.request_password_reset import RequestPasswordResetUseCase
from travel_map.use_case.verify_user_email import VerifyUserEmailUseCase


def get_verify_user_email_uc(
    uow: UnitOfWork = Depends(get_uow),
) -> VerifyUserEmailUseCase:
    return VerifyUserEmailUseCase(uow)


def get_register_user_uc(
    uow: UnitOfWork = Depends(get_uow),
    email_service: EmailService = Depends(get_email_service),
) -> RegisterUserUseCase:
    return RegisterUserUseCase(uow, email_service)


def get_login_user_uc(
    uow: UnitOfWork = Depends(get_uow),
) -> LoginUserUserCase:
    return LoginUserUserCase(uow)


def get_refresh_token_uc(
    uow: UnitOfWork = Depends(get_uow),
) -> RefreshTokenUseCase:
    return RefreshTokenUseCase(uow)


def get_request_password_reset_uc(
    uow: UnitOfWork = Depends(get_uow),
    email_service: EmailService = Depends(get_email_service),
) -> RequestPasswordResetUseCase:
    return RequestPasswordResetUseCase(uow, email_service)


def get_confirm_password_reset_uc(
    uow: UnitOfWork = Depends(get_uow),
) -> ConfirmPasswordResetUseCase:
    return ConfirmPasswordResetUseCase(uow)
