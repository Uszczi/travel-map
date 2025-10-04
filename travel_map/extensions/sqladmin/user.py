from datetime import timezone

from sqladmin import ModelView

from travel_map.models import UserModel


def fmt_dt(dt):
    if not dt:
        return "—"

    return dt.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


class UserAdmin(ModelView, model=UserModel):
    column_details_exclude_list = [
        UserModel.hashed_password,
    ]
    column_list = [
        UserModel.uuid,
        UserModel.email,
        UserModel.created_at,
        UserModel.updated_at,
    ]

    column_formatters = {
        UserModel.created_at: lambda m, a: fmt_dt(m.created_at),
        UserModel.updated_at: lambda m, a: fmt_dt(m.updated_at),
    }
