import osmnx as ox
from fastapi import APIRouter, Depends, HTTPException


from app import utils
from app.api.common import (
    DEFAULT_START_X,
    DEFAULT_START_Y,
    bbox_to_tuple,
    get_city_bbox,
    get_or_create_graph,
    graphs,
)
from app.generator.all_streets_random import AllStreetsRoute
from app.generator.astar import AStarRoute
from app.generator.dfs import DfsRoute
from app.generator.random_route import RandomRoute
from app.models import Route
from app.serializers.geocode import BoundingBox
from app.services.elevation import ElevationService
from app.visited_edges import visited_edges

router = APIRouter(tags=["Routes"])


def get_elevation_service():
    return ElevationService()


def _build_bbox(
    south: float | None,
    north: float | None,
    west: float | None,
    east: float | None,
) -> BoundingBox | None:
    if None in (south, north, west, east):
        return None
    return BoundingBox(south=south, north=north, west=west, east=east)


@router.get("/clear")
def clear():
    graphs.clear()
    visited_edges.clear()


@router.get("/route/{algorithm_type}")
def route(
    algorithm_type: str,
    nominatim_id: int = 0,
    start_x: float = DEFAULT_START_X,
    start_y: float = DEFAULT_START_Y,
    end_x: float | None = None,
    end_y: float | None = None,
    start_bbox_north: float | None = None,
    start_bbox_south: float | None = None,
    start_bbox_east: float | None = None,
    start_bbox_west: float | None = None,
    end_bbox_north: float | None = None,
    end_bbox_south: float | None = None,
    end_bbox_east: float | None = None,
    end_bbox_west: float | None = None,
    distance: int = 6000,
    prefer_new: bool = False,
    skip_elevation: bool = True,
    elevation_service: ElevationService = Depends(get_elevation_service),
) -> Route:
    start_bbox = _build_bbox(
        start_bbox_south, start_bbox_north, start_bbox_west, start_bbox_east
    )
    bbox = start_bbox

    if bbox is not None:
        G = get_or_create_graph(bbox=bbox)
        CITY_BBOX = bbox_to_tuple(bbox)
    elif nominatim_id:
        G = get_or_create_graph(nominatim_id=nominatim_id)
        CITY_BBOX = get_city_bbox(start_x, start_y)
    else:
        G = get_or_create_graph(start_x, start_y)
        CITY_BBOX = get_city_bbox(start_x, start_y)

    algorithm_map = {
        "allstreet": AllStreetsRoute,
        "random": RandomRoute,
        "dfs": DfsRoute,
        "astar": AStarRoute,
    }

    generator_class = algorithm_map.get(algorithm_type.lower())
    if not generator_class:
        raise HTTPException(
            status_code=422, detail=f"Unsupported algorithm type: {algorithm_type}"
        )

    start_node = ox.nearest_nodes(G, X=start_x, Y=start_y)
    if end_x and end_y:
        end_node = ox.nearest_nodes(G, X=end_x, Y=end_y)
    else:
        end_node = None

    with utils.time_measure("Generating route took: "):
        route = generator_class(G, visited_edges).generate(
            start_node=start_node,
            end_node=end_node,
            distance=distance,
            prefer_new=prefer_new,
        )

    x, y = utils.route_to_x_y(G, route)
    route_distance = utils.get_route_distance(G, route)
    segments = visited_edges.get_visited_segments(G, route)
    visited_edges.mark_edges_visited(route)
    if skip_elevation:
        elevation = []
    else:
        elevation = elevation_service.get(utils.zip_x_y(x, y))
        elevation = elevation_service.covert_to_list(elevation)

    total_gain, total_lose = elevation_service.calculate_total_gain_lose(elevation)

    return Route(
        rec=CITY_BBOX,
        x=x,
        y=y,
        distance=route_distance,
        segments=segments,
        elevation=elevation,
        total_gain=total_gain,
        total_lose=total_lose,
    )


@router.get("/visited-routes")
def get_visited_edges() -> list[list[tuple[float, float]]]:
    G = get_or_create_graph()
    result = []

    for u, v in visited_edges:
        # TODO remove this try, init-data logic for parsing route needs update
        try:
            data = min(G.get_edge_data(u, v).values(), key=lambda d: d["length"])
            if "geometry" in data:
                xs, ys = data["geometry"].xy
                result.append([[y, x] for (x, y) in zip(xs, ys)])
            else:
                result.append(
                    [
                        [G.nodes[u]["y"], G.nodes[u]["x"]],
                        [G.nodes[v]["y"], G.nodes[v]["x"]],
                    ]
                )
        except Exception:
            ...
    return result


@router.get("/visited-edges-as-points")
def get_visited_edges_as_points() -> list[tuple[float, float]]:
    G = get_or_create_graph()
    result = []

    for u, v in visited_edges:
        result.append((G.nodes[u]["y"], G.nodes[u]["x"]))
        result.append((G.nodes[v]["y"], G.nodes[v]["x"]))

    return result
