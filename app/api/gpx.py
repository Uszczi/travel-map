import io

from fastapi import APIRouter, Body
from fastapi.responses import StreamingResponse

from app.services.gpx import GPXService

router = APIRouter()


@router.post("/route-to-gpx")
def route_to_pgx(
    points: list[tuple[float, float]] = Body(...),
    title: str = Body(...),
) -> StreamingResponse:
    gpx = GPXService.points_to_gpx(points, title)

    return StreamingResponse(
        io.BytesIO(gpx.to_xml().encode("utf-8")),
        media_type="application/gpx+xml",
        headers={"Content-Disposition": f"attachment; filename={title}.gpx"},
    )
