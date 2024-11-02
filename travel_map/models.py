from pydantic import BaseModel


class Segment(BaseModel):
    new: bool
    distance: float


class Route(BaseModel):
    rec: tuple[float, float, float, float]
    x: list[float]
    y: list[float]
    distance: float
    segments: list[Segment]


class StravaRoute(BaseModel):
    id: int
    xy: list[tuple[float, float]]
    type: str
    name: str
