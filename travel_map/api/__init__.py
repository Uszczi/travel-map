from fastapi import FastAPI

from .middlewares import setup_middlewares
from .route_generation import router as route_router
from .main import router as main_router
from .strava_routes import router as strava_router

__all__ = ["setup_middlewares", "include_routers"]


def include_routers(app: FastAPI):
    app.include_router(main_router)
    app.include_router(route_router)
    app.include_router(strava_router)
