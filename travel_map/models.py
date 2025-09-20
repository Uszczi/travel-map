import uuid as uuid_pkg
from datetime import datetime, timezone

from pydantic import BaseModel, computed_field
from sqlalchemy import Column, text
from sqlalchemy.types import DateTime
from sqlmodel import Field, SQLModel


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
    x: list[float]
    y: list[float]
    type: str
    name: str

    ### Check if for every graph node id is the same
    nodes: list[int]


class UUIDModel(SQLModel):
    uuid: uuid_pkg.UUID = Field(
        default_factory=uuid_pkg.uuid4,
        primary_key=True,
        nullable=False,
        sa_column_kwargs={"server_default": text("gen_random_uuid()")},
    )


class TimestampModel(SQLModel):
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            DateTime(timezone=True),
            server_default=text("CURRENT_TIMESTAMP(0)"),
        ),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            DateTime(timezone=True),  # <<<<<< timezone=True
            server_default=text("CURRENT_TIMESTAMP(0)"),
            server_onupdate=text("CURRENT_TIMESTAMP(0)"),
        ),
    )


class UserModel(UUIDModel, TimestampModel, table=True):
    email: str
