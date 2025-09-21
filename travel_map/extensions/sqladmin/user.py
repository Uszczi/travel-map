from sqladmin import ModelView

from travel_map.models import UserModel


class UserAdmin(ModelView, model=UserModel):
    pass
