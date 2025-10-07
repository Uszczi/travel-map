import pytest
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.jwt import issue_refresh_token
from app.models import UserModel
from app.password import PasswordHelper
from tests.factories import acreate_user


@pytest.mark.asyncio
async def test_register(client, async_session: AsyncSession):
    data = {"email": "someemail@example.com", "password": "SomeStrong123!@#"}

    res = await client.post("/register", json=data)

    assert res.status_code == 200, res.json()

    # TODO use user repo
    users = list(await async_session.exec(select(UserModel)))
    assert len(users) == 1
    user = users[0]

    assert user.email == "someemail@example.com"
    assert user.hashed_password


@pytest.mark.asyncio
async def test_login(client, async_session):
    user = await acreate_user(
        async_session, hashed_password=PasswordHelper().hash("Supersecret")
    )

    data = {"username": user.email, "password": "Supersecret"}
    res = await client.post("/login", data=data)

    res_json = res.json()
    assert res.status_code == 200, res_json

    for key in ("access_token", "refresh_token"):
        res_json.pop(key)
    assert res_json == {}


@pytest.mark.asyncio
async def test_refresh(client, async_session):
    user = await acreate_user(
        async_session, hashed_password=PasswordHelper().hash("Supersecret")
    )
    refresh_token = issue_refresh_token(user)

    data = {"refresh_token": refresh_token}
    res = await client.post("/refresh", json=data)

    res_json = res.json()
    assert res.status_code == 200, res_json

    for key in ("access_token", "refresh_token"):
        res_json.pop(key)
    assert res_json == {}


@pytest.mark.asyncio
async def test_register_login_refresh(client, async_session):
    email = "someemail@example.com"
    password = "SomeStrong123!@#"
    register_data = {"email": email, "password": password}

    register_res = await client.post("/register", json=register_data)

    assert register_res.status_code == 200, register_res.json()

    login_data = {"username": email, "password": password}
    login_res = await client.post("/login", data=login_data)

    login_json = login_res.json()
    assert login_res.status_code == 200, login_json

    refresh_data = {"refresh_token": login_json["refresh_token"]}
    refresh_res = await client.post("/refresh", json=refresh_data)

    refresh_json = refresh_res.json()
    assert refresh_res.status_code == 200, refresh_json
