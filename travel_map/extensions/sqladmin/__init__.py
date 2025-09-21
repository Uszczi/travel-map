from fastapi import FastAPI
from sqladmin import Admin

from travel_map.db import engine
from travel_map.extensions.sqladmin.user import UserAdmin


def include_sqladmin(app: FastAPI) -> None:
    admin = Admin(app, engine, base_url="/backoffice")

    admin.add_view(UserAdmin)
