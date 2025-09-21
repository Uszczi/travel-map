from fastapi import FastAPI
from sqladmin import Admin

from travel_map.db import engine
from travel_map.extensions.sqladmin.user import UserAdmin


def include_sqladmin(app: FastAPI) -> None:
    # if settings.URL_PREFIX:
    #     base_url = f"/{settings.URL_PREFIX}/backoffice"
    # else:
    base_url = "/backoffice"

    admin = Admin(app, engine, base_url=base_url)

    admin.add_view(UserAdmin)
