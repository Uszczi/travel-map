from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.utils import ROOT_PATH

from .htmx import router as htmx_router
from .pages import router as pages_router

__all__ = ["include_web"]


def include_web(app: FastAPI) -> None:
    """Mount static files and register the server-rendered web UI routers."""
    app.mount(
        "/static",
        StaticFiles(directory=ROOT_PATH / "static"),
        name="static",
    )
    app.include_router(pages_router)
    app.include_router(htmx_router)
