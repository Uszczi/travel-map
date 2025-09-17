from fastapi import FastAPI

from travel_map.settings import settings

import sentry_sdk
from .geocode import router as geocode_router
from .gpx import router as gpx_router
from .main import router as main_router
from .middlewares import setup_middlewares
from .route_generation import router as route_router
from .strava_routes import router as strava_router

__all__ = ["setup_middlewares", "include_routers", "init_sentry"]


def include_routers(app: FastAPI):
    # TODO automatic imports and includes
    app.include_router(main_router)
    app.include_router(route_router)
    app.include_router(strava_router)
    app.include_router(gpx_router)
    app.include_router(geocode_router)


def init_sentry():
    if settings.SENTRY_SDK:
        sentry_sdk.init(
            dsn=settings.SENTRY_SDK,
        )
