from fastapi import APIRouter, Depends

from travel_map.serializers.input.user import UserRegister
from travel_map.use_case import get_register_user_uc
from travel_map.use_case.register_user import RegisterUserCommand, RegisterUserUseCase

router = APIRouter()


@router.post("/register")
async def register(
    data: UserRegister, uc: RegisterUserUseCase = Depends(get_register_user_uc)
):

    user = await uc(RegisterUserCommand(**data.model_dump()))  # type: ignore
    return user
