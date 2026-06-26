from fastapi import FastAPI

from app.api import include_routers, init_sentry, setup_middlewares
from app.extensions.lifespan import lifespan
from app.extensions.prometheus import include_prometheus
from app.extensions.sqladmin import include_sqladmin

init_sentry()

app = FastAPI(
    lifespan=lifespan,
    openapi_tags=[
        {"name": "General", "description": "Health check, version, and info endpoints"},
        {"name": "Routes", "description": "Route generation and visited edges"},
        {"name": "Strava", "description": "Strava route import and management"},
        {"name": "GPX", "description": "GPX file export"},
        {"name": "Geocoding", "description": "Forward and reverse geocoding"},
        {"name": "Auth", "description": "User authentication and account management"},
    ],
)

setup_middlewares(app)

include_routers(app)
include_prometheus(app)
# include_alloy(app)
include_sqladmin(app)
