from fastapi import FastAPI
from sqladmin import Admin

from travel_map.db import engine
from travel_map.extensions.sqladmin.user import UserAdmin
from travel_map.settings import settings


def include_sqladmin(app: FastAPI) -> None:
    admin = Admin(app, engine, base_url=settings.URL_PREFIX + "/backoffice")

    admin.add_view(UserAdmin)
