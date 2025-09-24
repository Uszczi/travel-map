from fastapi import FastAPI

from travel_map.api import include_routers, init_sentry, setup_middlewares
from travel_map.extensions.lifespan import lifespan
from travel_map.extensions.prometheus import include_prometheus
from travel_map.extensions.sqladmin import include_sqladmin

init_sentry()

app = FastAPI(lifespan=lifespan)

setup_middlewares(app)

include_routers(app)

include_prometheus(app)

# include_alloy(app)

include_sqladmin(app)
