from fastapi import Depends

from travel_map.dependencies import get_uow
from travel_map.domain.ports import UnitOfWork
from travel_map.services.email import EmailService, get_email_service
from travel_map.use_case.register_user import RegisterUserUseCase


def get_register_user_uc(
    uow: UnitOfWork = Depends(get_uow),
    email_service: EmailService = Depends(get_email_service),
) -> RegisterUserUseCase:
    return RegisterUserUseCase(uow, email_service)
