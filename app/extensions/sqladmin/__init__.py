from fastapi import FastAPI
from sqladmin import Admin

from app.db import engine
from app.extensions.sqladmin.user import UserAdmin


def include_sqladmin(app: FastAPI) -> None:
    admin = Admin(app, engine, base_url="/backoffice")

    admin.add_view(UserAdmin)
