import io

from fastapi import APIRouter, Body
from fastapi.responses import StreamingResponse
from loguru import logger

from app.services.gpx import GPXService

router = APIRouter(tags=["GPX"])


@router.post("/route-to-gpx")
def route_to_pgx(
    points: list[tuple[float, float]] = Body(...),
    title: str = Body(...),
) -> StreamingResponse:
    logger.info("POST /route-to-gpx: title={}, points={}", title, len(points))
    gpx = GPXService.points_to_gpx(points, title)

    return StreamingResponse(
        io.BytesIO(gpx.to_xml().encode("utf-8")),
        media_type="application/gpx+xml",
        headers={"Content-Disposition": f"attachment; filename={title}.gpx"},
    )
