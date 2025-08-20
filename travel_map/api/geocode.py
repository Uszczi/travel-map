from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from travel_map.serializers.geocode import (
    GeocodeResponse,
    ReverseResponse,
)
from travel_map.services.nominatim import (
    BadRequest,
    FetchFailed,
    NominatimService,
    NotFound,
    UpstreamError,
)

router = APIRouter()


# TODO
def get_nominatim_service() -> NominatimService:
    return NominatimService()


@router.get("/geocode")
async def geocode(
    q: Optional[str] = Query(None, description="Search query (search)"),
    lat_param: Optional[str] = Query(
        None, alias="lat", description="Latitude (reverse)"
    ),
    lng_param: Optional[str] = Query(
        None, alias="lng", description="Longitude (reverse)"
    ),
    nominatim: NominatimService = Depends(get_nominatim_service),
) -> GeocodeResponse | ReverseResponse:
    if q and (lat_param or lng_param):
        raise HTTPException(
            status_code=400,
            detail="Use either q (search) or lat+lng (reverse), not both at once.",
        )
    if not q and (not lat_param or not lng_param):
        raise HTTPException(
            status_code=400,
            detail="Provide q (search) or both lat and lng (reverse).",
        )

    if q:
        try:
            items = await nominatim.search(q=q, limit=5)
        except BadRequest:
            raise HTTPException(status_code=400, detail="Query cannot be empty.")
        except FetchFailed:
            raise HTTPException(status_code=500, detail="Fetch failed")
        except UpstreamError:
            raise HTTPException(status_code=502, detail="Upstream error")

        return GeocodeResponse(items=items)

    try:
        lat = float(lat_param)  # type: ignore[arg-type]
        lng = float(lng_param)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=400, detail="The lat and lng parameters must be numbers."
        )

    try:
        reverse = await nominatim.reverse(lat=lat, lng=lng)
    except NotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except FetchFailed:
        raise HTTPException(status_code=500, detail="Fetch failed")
    except UpstreamError:
        raise HTTPException(status_code=502, detail="Upstream error")

    return reverse
