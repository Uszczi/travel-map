from fastapi import FastAPI

from travel_map.api import include_routers, init_sentry, setup_middlewares
from travel_map.extensions.lifespan import lifespan
from travel_map.extensions.prometheus import include_prometheus
from travel_map.settings import settings

init_sentry()

app = FastAPI(lifespan=lifespan, root_path=settings.URL_PREFIX)

setup_middlewares(app)

include_routers(app)

include_prometheus(app)
