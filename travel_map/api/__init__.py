from fastapi import FastAPI

from .middlewares import setup_middlewares
from .route_generation import router as route_router
from .strava_routes import router as strava_router

setup_middlewares = setup_middlewares


def include_routers(app: FastAPI):
    app.include_router(route_router)
    app.include_router(strava_router)
