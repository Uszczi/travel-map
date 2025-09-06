import gpxpy
from fastapi import APIRouter
from loguru import logger
from pydantic import BaseModel

from travel_map.db import strava_db
from travel_map.models import StravaRoute
from travel_map.utils import ROOT_PATH, get_graph_distance
from travel_map.visited_edges import strava_route_to_nodes, visited_edges

from . import common

router = APIRouter(prefix="/strava")

INIT_DATA_PATH = ROOT_PATH / "init_data"


@router.get("/routes")
def get_strava_routes() -> list[StravaRoute]:
    collection = strava_db["routes"]
    routes = collection.find()
    result = [StravaRoute(**route) for route in routes]  # type: ignore[missing-argument]
    return result


@router.get("/mark-as-visited")
def mark_as_visited() -> str:
    G = common.get_or_create_graph()

    collection = strava_db["routes"]
    routes = collection.find()
    result = [StravaRoute(**route) for route in routes]  # type: ignore[missing-argument]
    for strava_route in result:
        logger.info(f"{strava_route.id}")
        route = strava_route_to_nodes(G, strava_route)
        visited_edges.mark_edges_visited(route)

    graph_distance = get_graph_distance(G)
    visited_routes_distance = visited_edges.get_visited_distance(G)

    return f"{visited_routes_distance / graph_distance * 100:.2f}"


class InitDataResponse(BaseModel):
    inserted: list[int]
    already_saved: list[int]
    errors: dict[str, str]


@router.get("/init-data")
def load_init_data() -> InitDataResponse:
    collection = strava_db["routes"]

    saved_ids = {doc["id"] for doc in collection.find({}, {"id": 1, "_id": 0})}

    already_saved: list[int] = []
    inserted: list[int] = []
    errors: dict[str, str] = {}

    for path in sorted(INIT_DATA_PATH.glob("*.gpx")):
        file_id = int(path.stem)

        if file_id in saved_ids:
            already_saved.append(file_id)
            continue

        try:
            with path.open("r", encoding="utf-8") as f:
                gpx = gpxpy.parse(f)

            name = (
                (gpx.name.strip() if gpx.name else None)
                or next((t.name.strip() for t in gpx.tracks if t.name), None)
                or next((r.name.strip() for r in gpx.routes if r.name), None)
                or f"Route {file_id}"
            )

            points: list[tuple[float, float]] = []
            if gpx.tracks:
                for trk in gpx.tracks:
                    for seg in trk.segments:
                        for p in seg.points:
                            points.append((float(p.longitude), float(p.latitude)))
            elif gpx.routes:
                for rte in gpx.routes:
                    for p in rte.points:
                        points.append((float(p.longitude), float(p.latitude)))
            else:
                raise ValueError("No tracks or routes found in GPX")

            xy: list[tuple[float, float]] = []
            prev = None
            for lon, lat in points:
                pair = (lon, lat)
                if pair != prev:
                    xy.append(pair)
                    prev = pair

            if not xy:
                raise ValueError("No coordinate points extracted from GPX")

            doc = StravaRoute(
                id=file_id,
                xy=xy,  # (x=lon, y=lat)
                type="gpx",
                name=name,
            )
            collection.insert_one(doc.model_dump())
            inserted.append(file_id)

        except Exception as e:
            errors[str(file_id)] = f"{type(e).__name__}: {e}"

    return InitDataResponse(
        inserted=inserted,
        already_saved=already_saved,
        errors=errors,
    )
