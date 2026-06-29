import httpx
from loguru import logger

from app.serializers.geocode import GeocodeItem
from app.settings import settings


class NominatimError(Exception):
    """Base class for Nominatim-related exceptions."""


class FetchFailed(NominatimError):
    pass


class UpstreamError(NominatimError):
    pass


class NotFound(NominatimError):
    pass


class BadRequest(NominatimError):
    pass


class NominatimService:
    def __init__(self) -> None:
        self.search_url = settings.NOMINATIM_URL
        self.reverse_url = settings.NOMINATIM_REVERSE_URL
        self.timeout = 10
        self.headers = {
            "User-Agent": settings.NOMINATIM_USER_AGENT,
            "Accept": "application/json",
            "Accept-Language": "pl,en;q=0.8",
        }

    async def search(
        self, q: str, limit: int = 5, tag: str | None = None
    ) -> list[GeocodeItem]:
        if not q or not q.strip():
            raise BadRequest("Empty query.")

        logger.info("Nominatim search: q={}, tag={}, limit={}", q, tag, limit)

        params = {
            "key": settings.NOMINATIM_ACCESS_TOKEN,
            "q": q.strip(),
            "accept-language": "pl",  # TODO
            "format": "json",
            "limit": str(limit),
            "dedupe": 1,
        }

        if tag:
            params["tag"] = tag

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout, headers=self.headers
            ) as client:
                res = await client.get(self.search_url, params=params)
        except httpx.HTTPError as e:
            logger.error("Nominatim search fetch failed: {}", e)
            raise FetchFailed("Fetch failed") from e

        if not res.is_success:
            logger.warning("Nominatim search upstream error: {}", res.status_code)
            raise UpstreamError(f"Upstream error ({res.status_code})")

        raw = res.json()
        logger.debug("Nominatim search returned {} results", len(raw))

        items: list[GeocodeItem] = [
            GeocodeItem(
                id=r["place_id"],
                label=r["display_name"],
                lat=r["lat"],
                lng=r["lon"],
                type=r["type"],
                boundingbox=r["boundingbox"],
            )
            for r in raw
        ]
        return items

    async def reverse(self, lat: float, lng: float) -> GeocodeItem:
        logger.info("Nominatim reverse: lat={}, lng={}", lat, lng)

        params = {
            "key": settings.NOMINATIM_ACCESS_TOKEN,
            "format": "json",
            "lat": str(lat),
            "lon": str(lng),
        }

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout, headers=self.headers
            ) as client:
                res = await client.get(self.reverse_url, params=params)
        except httpx.HTTPError as e:
            logger.error("Nominatim reverse fetch failed: {}", e)
            raise FetchFailed("Fetch failed") from e

        if not res.is_success:
            logger.warning("Nominatim reverse upstream error: {}", res.status_code)
            raise UpstreamError(f"Upstream error ({res.status_code})")

        raw = res.json()

        if not raw or (isinstance(raw, dict) and raw.get("error")):
            msg = (
                raw.get("error")
                if isinstance(raw, dict)
                else "No address found for these coordinates."
            )
            logger.warning("Nominatim reverse not found: {}", msg)
            raise NotFound(msg)

        logger.debug("Nominatim reverse got: {}", raw.get("display_name"))
        return GeocodeItem(
            id=raw["place_id"],
            label=raw["display_name"],
            lat=raw["lat"],
            lng=raw["lon"],
            type=raw["osm_type"],
            boundingbox=raw["boundingbox"],
        )
