from travel_map.db import async_session
from travel_map.infrastructure.uow import SqlAlchemyUoW


def get_uow() -> SqlAlchemyUoW:
    return SqlAlchemyUoW(async_session)
