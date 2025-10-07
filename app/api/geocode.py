from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache

from app.limiter import NOMINATIM_LIMITER
from app.serializers.geocode import GeocodeItem, GeocodeResponse
from app.services.nominatim import (
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


CACHE_TIME = 60 * 60 * 24 * 7


def request_key_builder(
    func,
    namespace: str,
    request: Request,
    response: Response | None = None,
    *args,
    **kwargs,
):
    prefix = FastAPICache.get_prefix()
    return ":".join(
        [
            prefix,
            namespace or "geocode",
            request.method.lower(),
            request.url.path,
            repr(sorted(request.query_params.items())),
        ]
    )


@router.get("/geocode")
@cache(CACHE_TIME, key_builder=request_key_builder)
async def geocode(
    q: Optional[str] = Query(None, description="Search query (search)"),
    lat_param: Optional[str] = Query(
        None, alias="lat", description="Latitude (reverse)"
    ),
    lng_param: Optional[str] = Query(
        None, alias="lng", description="Longitude (reverse)"
    ),
    tag: Optional[str] = Query(None, alias="tag", description="Tag of places"),
    nominatim: NominatimService = Depends(get_nominatim_service),
) -> GeocodeResponse | GeocodeItem:
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
            async with NOMINATIM_LIMITER.slot():
                items = await nominatim.search(q=q, limit=5, tag=tag)
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
        async with NOMINATIM_LIMITER.slot():
            reverse = await nominatim.reverse(lat=lat, lng=lng)
    except NotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except FetchFailed:
        raise HTTPException(status_code=500, detail="Fetch failed")
    except UpstreamError:
        raise HTTPException(status_code=502, detail="Upstream error")

    return reverse
