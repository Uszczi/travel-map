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

    def to_list(self) -> list[float]:
        return [self.south, self.north, self.west, self.east]

    def center(self) -> tuple[float, float]:
        return (self.south + self.north) / 2, (self.west + self.east) / 2

    def __hash__(self):
        return hash(self.south) + hash(self.north) + hash(self.west) + hash(self.east)


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
        if type(v) is list:
            return BoundingBox.from_nominatim(v)
        return v


class GeocodeResponse(BaseModel):
    items: List[GeocodeItem]
