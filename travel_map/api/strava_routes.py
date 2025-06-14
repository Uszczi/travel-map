from fastapi import APIRouter

from travel_map.db import mongo_db
from travel_map.models import StravaRoute
from travel_map.visited_edges import strava_route_to_route, visited_edges

from . import common

router = APIRouter(prefix="/strava")


@router.get("/routes")
def get_strava_routes() -> list[StravaRoute]:
    collection = mongo_db["routes"]
    routes = collection.find()
    result = [StravaRoute(**route) for route in routes]  # type: ignore[missing-argument]
    for route in result:
        route.xy = route.xy[::2]
    return result[:1]


@router.get("/mark-as-visited")
def mark_as_visited(
    start_x: float = common.DEFAULT_START_X,
    start_y: float = common.DEFAULT_START_Y,
):
    G = common.get_or_create_graph(start_x, start_y)

    collection = mongo_db["routes"]
    routes = collection.find()
    result = [StravaRoute(**route) for route in routes]  # type: ignore[missing-argument]
    for strava_route in result:
        route = strava_route_to_route(G, strava_route)
        route = list(dict.fromkeys(route))
        visited_edges.mark_edges_visited(route)

    return "ok"
