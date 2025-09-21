from fastapi import FastAPI
from sqladmin import Admin

from travel_map.db import engine
from travel_map.extensions.sqladmin.user import UserAdmin

# from travel_map.settings import settings


def include_sqladmin(app: FastAPI) -> None:
    # if settings.URL_PREFIX:
    #     if settings.URL_PREFIX.startswith("/"):
    #         base_url = f"{settings.URL_PREFIX}/backoffice"
    #     else:
    #         base_url = f"/{settings.URL_PREFIX}/backoffice"
    # else:
    base_url = "/backoffice"

    print(base_url)
    print(base_url)
    print(base_url)
    admin = Admin(app, engine, base_url=base_url)

    admin.add_view(UserAdmin)
