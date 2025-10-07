from fastapi import FastAPI

from app.api import include_routers, init_sentry, setup_middlewares
from app.extensions.lifespan import lifespan
from app.extensions.prometheus import include_prometheus
from app.extensions.sqladmin import include_sqladmin

init_sentry()

app = FastAPI(lifespan=lifespan)

setup_middlewares(app)

include_routers(app)

include_prometheus(app)

# include_alloy(app)

include_sqladmin(app)
