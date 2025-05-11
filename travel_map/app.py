from fastapi import FastAPI
from travel_map.api.routes import router
from travel_map.middlewares import setup_middlewares

app = FastAPI()
setup_middlewares(app)

app.include_router(router)
