import osmnx as ox
from networkx import MultiDiGraph

from travel_map import utils

graphs = {}

DEFAULT_START_X = 19.1999532
DEFAULT_START_Y = 51.6101241
CITY_BBOX_DEFAULT_SIZE = 0.04


def get_city_bbox(start_x=DEFAULT_START_X, start_y=DEFAULT_START_Y):
    return (
        start_x - CITY_BBOX_DEFAULT_SIZE * 2,
        start_y - CITY_BBOX_DEFAULT_SIZE,
        start_x + CITY_BBOX_DEFAULT_SIZE * 2,
        start_y + CITY_BBOX_DEFAULT_SIZE,
    )


def get_or_create_graph(
    start_x: float = DEFAULT_START_X, start_y: float = DEFAULT_START_Y
) -> MultiDiGraph:
    if g := graphs.get("refactor"):
        return g

    with utils.time_measure("ox.graph_from_bbox took: "):
        CITY_BBOX = get_city_bbox(start_x, start_y)
        G = ox.graph_from_bbox(CITY_BBOX, network_type="drive")
        graphs["refactor"] = G
        return G
