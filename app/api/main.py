import datetime
from pathlib import Path

from fastapi import APIRouter
from loguru import logger

router = APIRouter(tags=["General"])
start_time = datetime.datetime.now(datetime.timezone.utc)


@router.get("/")
def read_root():
    logger.info("Hello World.")
    return {"Hello": "World"}


def get_version():
    head = Path("./.git/HEAD").read_text().strip()
    if head.startswith("ref: "):
        ref_path = f"./.git/{head[5:]}"
        return Path(ref_path).read_text().strip()
    return head


@router.get("/version")
def version():
    return {
        "version": get_version()[:7],
    }


@router.get("/info")
def info():
    return {
        "version": get_version()[:7],
        "start_time": start_time,
        "uptime_seconds": (
            datetime.datetime.now(datetime.timezone.utc) - start_time
        ).total_seconds(),
    }
