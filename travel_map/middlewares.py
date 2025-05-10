from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import time

from loguru import logger


async def measure_execution_time(request: Request, call_next):
    start_time = time.time()

    logger.info(f"{request.url} start.")
    response = await call_next(request)

    process_time = time.time() - start_time
    logger.info(f"{request.url} took {process_time:.4f} sec.")

    return response


def setup_middlewares(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.middleware("http")(measure_execution_time)
