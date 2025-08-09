from fastapi import FastAPI

from .main import router as main_router
from .middlewares import setup_middlewares
from .route_generation import router as route_router
from .strava_routes import router as strava_router
from .gpx import router as gpx_router

__all__ = ["setup_middlewares", "include_routers"]


def include_routers(app: FastAPI):
    # TODO automatic imports and includes
    app.include_router(main_router)
    app.include_router(route_router)
    app.include_router(strava_router)
    app.include_router(gpx_router)
