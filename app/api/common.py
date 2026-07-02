import osmnx as ox
from loguru import logger
from networkx import MultiDiGraph

from app import utils
from app.serializers.geocode import BoundingBox

graphs = {}

DEFAULT_START_X = 19.1999532
DEFAULT_START_Y = 51.6101241
CITY_BBOX_DEFAULT_SIZE = 0.03

BBox = tuple[float, float, float, float]


def get_city_bbox(
    start_x=DEFAULT_START_X,
    start_y=DEFAULT_START_Y,
    size=CITY_BBOX_DEFAULT_SIZE,
) -> BBox:
    return (
        start_x - size * 2,
        start_y - size,
        start_x + size * 2,
        start_y + size,
    )


def bbox_to_osmnx(bbox: BoundingBox) -> BBox:
    """Convert a frontend BoundingBox into osmnx's (left, bottom, right, top) tuple."""
    return (bbox.west, bbox.south, bbox.east, bbox.north)


def combine_bboxes(*bboxes: BoundingBox | None) -> BoundingBox | None:
    """Merge several bounding boxes into the smallest one that contains them all."""
    valid = [b for b in bboxes if b is not None]
    if not valid:
        return None
    return BoundingBox(
        south=min(b.south for b in valid),
        north=max(b.north for b in valid),
        west=min(b.west for b in valid),
        east=max(b.east for b in valid),
    )


def bbox_to_tuple(bbox: BoundingBox) -> tuple[float, float, float, float]:
    return (bbox.west, bbox.south, bbox.east, bbox.north)


def get_or_create_graph(
    start_x: float | None = None,
    start_y: float | None = None,
    nominatim_id: int | None = None,
    bbox: BoundingBox | None = None,
) -> MultiDiGraph:
    if start_x is not None and start_y is not None:
        key = f"{start_x}_{start_y}"
        if G := graphs.get(key):
            logger.debug("Using cached graph for coords {}", key)
            return G

        logger.info("Fetching graph for coords {},{}", start_x, start_y)
        with utils.time_measure("ox.graph_from_bbox took: "):
            CITY_BBOX = get_city_bbox(start_x, start_y)
            G = ox.graph_from_bbox(CITY_BBOX, network_type="walk")
            graphs[key] = G
            return G

    if bbox is not None:
        if g := graphs.get(bbox):
            logger.debug("Using cached graph for bbox {}", bbox)
            return g

        logger.info("Fetching graph for bbox {}", bbox)
        with utils.time_measure("ox.graph_from_bbox took: "):
            # TODO: check which network_type is better
            G = ox.graph_from_bbox(bbox_to_tuple(bbox), network_type="walk")
        graphs[bbox] = G
        return G

    if nominatim_id is not None:
        logger.info("Fetching graph for nominatim_id={}", nominatim_id)
        with utils.time_measure("ox.graph_from_bbox took: "):
            CITY_BBOX = get_city_bbox(start_x, start_y)
            G = ox.graph_from_bbox(CITY_BBOX, network_type="drive")
            graphs["refactor"] = G
            return G
