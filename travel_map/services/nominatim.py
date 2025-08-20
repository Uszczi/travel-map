import httpx

from travel_map.serializers.geocode import GeocodeItem
from travel_map.settings import settings


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

    async def search(self, q: str, limit: int = 5) -> list[GeocodeItem]:
        if not q or not q.strip():
            raise BadRequest("Empty query.")

        params = {
            "q": q.strip(),
            "format": "jsonv2",
            "limit": str(limit),
            "addressdetails": "1",
        }

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout, headers=self.headers
            ) as client:
                res = await client.get(self.search_url, params=params)
        except httpx.HTTPError as e:
            raise FetchFailed("Fetch failed") from e

        if not res.is_success:
            raise UpstreamError(f"Upstream error ({res.status_code})")

        raw = res.json()

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
        params = {
            "format": "jsonv2",
            "lat": str(lat),
            "lon": str(lng),
            "addressdetails": "1",
        }

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout, headers=self.headers
            ) as client:
                res = await client.get(self.reverse_url, params=params)
        except httpx.HTTPError as e:
            raise FetchFailed("Fetch failed") from e

        if not res.is_success:
            raise UpstreamError(f"Upstream error ({res.status_code})")

        raw = res.json()

        if not raw or (isinstance(raw, dict) and raw.get("error")):
            msg = (
                raw.get("error")
                if isinstance(raw, dict)
                else "No address found for these coordinates."
            )
            raise NotFound(msg)

        return GeocodeItem(
            id=raw["place_id"],
            label=raw["display_name"],
            lat=raw["lat"],
            lng=raw["lon"],
            type=raw["type"],
            boundingbox=raw["boundingbox"],
        )
