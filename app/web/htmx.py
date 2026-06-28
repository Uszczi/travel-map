from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse

from app.api import route_generation as rg
from app.api.common import DEFAULT_START_X, DEFAULT_START_Y
from app.serializers.geocode import GeocodeItem
from app.services.elevation import ElevationService
from app.services.nominatim import (
    BadRequest,
    FetchFailed,
    NominatimService,
    UpstreamError,
)

router = APIRouter(prefix="/htmx", tags=["Web"], include_in_schema=False)


def get_nominatim_service() -> NominatimService:
    return NominatimService()


@router.get("/route", response_class=HTMLResponse)
def htmx_route(
    request: Request,
    algorithm: str = "random",
    start_x: float = DEFAULT_START_X,
    start_y: float = DEFAULT_START_Y,
    end_x: float | None = None,
    end_y: float | None = None,
    distance: int = 6000,
    prefer_new: bool = False,
) -> HTMLResponse:
    """Generate a route and return an HTML fragment that draws it on the map."""
    from app.web.templates import templates

    route = rg.route(
        algorithm_type=algorithm,
        start_x=start_x,
        start_y=start_y,
        end_x=end_x,
        end_y=end_y,
        distance=distance,
        prefer_new=prefer_new,
        skip_elevation=True,
        elevation_service=ElevationService(),
    )

    coords = [[lat, lng] for lat, lng in zip(route.y, route.x)]

    return templates.TemplateResponse(
        request,
        "partials/route_result.html",
        {"route": route, "coords": coords},
    )


@router.get("/visited-routes", response_class=HTMLResponse)
def htmx_visited_routes(request: Request) -> HTMLResponse:
    """Return an HTML fragment that draws all visited edges on the map."""
    from app.web.templates import templates

    segments = rg.get_visited_edges()

    return templates.TemplateResponse(
        request,
        "partials/visited_routes.html",
        {"segments": segments, "count": len(segments)},
    )


@router.get("/geocode", response_class=HTMLResponse)
async def htmx_geocode(
    request: Request,
    q: str = Query("", description="Search query"),
    nominatim: NominatimService = Depends(get_nominatim_service),
) -> HTMLResponse:
    """Return an HTML fragment listing geocoding matches for the search box."""
    from app.web.templates import templates

    items: list[GeocodeItem] = []
    error: str | None = None

    query = q.strip()
    if query:
        try:
            items = await nominatim.search(q=query, limit=5)
        except BadRequest:
            error = "Query cannot be empty."
        except (FetchFailed, UpstreamError):
            error = "Geocoding service unavailable."

    return templates.TemplateResponse(
        request,
        "partials/geocode_results.html",
        {"items": items, "error": error, "query": query},
    )
