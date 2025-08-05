from pydantic import BaseModel, computed_field


class Segment(BaseModel):
    new: bool
    distance: float


class Route(BaseModel):
    rec: tuple[float, float, float, float]
    x: list[float]
    y: list[float]
    distance: float
    segments: list[Segment]
    elevation: list[int]
    total_gain: int
    total_lose: int

    @computed_field(return_type=float)
    @property
    def total_new(self) -> float:
        return sum(s.distance for s in self.segments if s.new)

    @computed_field(return_type=float)
    @property
    def total_old(self) -> float:
        return sum(s.distance for s in self.segments if not s.new)

    @computed_field(return_type=float)
    @property
    def percent_of_new(self) -> float:
        if self.distance == 0:
            return 0.0
        return (self.total_new / self.distance) * 100


class StravaRoute(BaseModel):
    id: int
    xy: list[tuple[float, float]]
    type: str
    name: str
