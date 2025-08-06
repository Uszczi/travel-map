from fastapi import APIRouter
import subprocess
import datetime

router = APIRouter()
start_time = datetime.datetime.utcnow()


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
        "version": get_version()[:8],
    }


@router.get("/info")
def info():
    return {
        "version": get_version()[:8],
        "start_time": start_time,
        "uptime_seconds": (datetime.datetime.utcnow() - start_time).total_seconds(),
    }
