from fastapi import FastAPI

from travel_map.api import include_routers, setup_middlewares

app = FastAPI()
setup_middlewares(app)
include_routers(app)
