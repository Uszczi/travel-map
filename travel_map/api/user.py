from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from travel_map.db import get_async_session
from travel_map.models import UserModel
from travel_map.serializers.input.user import UserRegister

router = APIRouter()


@router.post("/register")
async def register(
    data: UserRegister, session: AsyncSession = Depends(get_async_session)
):
    user_db = await session.exec(select(UserModel).where(UserModel.email == data.email))
    user_db = user_db.first()

    if user_db:
        raise HTTPException(
            status_code=400,
            detail="User already registered.",
        )

    user = UserModel(**data.model_dump())

    session.add(user)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=400,
            detail="User already registered.",
        )

    await session.refresh(user)
    return user
