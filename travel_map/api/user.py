from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from travel_map.db import get_async_session
from travel_map.models import UserModel
from travel_map.serializers.input.user import UserRegister

router = APIRouter()


@router.post("/register")
async def register(
    data: UserRegister, session: AsyncSession = Depends(get_async_session)
):
    user = UserModel(**data.model_dump())

    session.add(user)
    await session.commit()

    return {"message": "Rejestracja OK", "email": data.email}
