from typing import Any, List, Optional

from pydantic import BaseModel, field_validator


class BoundingBox(BaseModel):
    south: float
    north: float
    west: float
    east: float

    @classmethod
    def from_nominatim(cls, v: Optional[List[Any]]) -> Optional["BoundingBox"]:
        if not v or len(v) != 4:
            return None
        s, n, w, e = map(float, v)
        return cls(south=s, north=n, west=w, east=e)


class GeocodeItem(BaseModel):
    id: int
    label: str
    lat: float
    lng: float
    type: str
    boundingbox: BoundingBox

    @field_validator("boundingbox", mode="before")
    @classmethod
    def _bbox_from_list(cls, v):
        return BoundingBox.from_nominatim(v)


class GeocodeResponse(BaseModel):
    items: List[GeocodeItem]
