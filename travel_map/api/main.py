import datetime
import subprocess

from fastapi import APIRouter

router = APIRouter()
start_time = datetime.datetime.now(datetime.timezone.utc)


@router.get("/")
def read_root():
    return {"Hello": "World"}


def get_version():
    return (
        subprocess.check_output(
            ["awk", 'BEGIN { ORS=" " }; { print $1 }', "./.git/FETCH_HEAD"]
        )
        .decode()
        .strip()
    )


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
