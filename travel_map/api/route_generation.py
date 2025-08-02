import osmnx as ox
from fastapi import APIRouter

from travel_map import utils
from travel_map.api.common import (
    DEFAULT_START_X,
    DEFAULT_START_Y,
    get_city_bbox,
    get_or_create_graph,
    graphs,
)
from travel_map.generator.astar import AStarRoute
from travel_map.generator.dfs import DfsRoute
from travel_map.generator.random_route import RandomRoute
from travel_map.models import Route
from travel_map.visited_edges import visited_edges

router = APIRouter()


@router.get("/")
def read_root():
    return {"Hello": "World"}


@router.get("/clear")
def clear():
    graphs.clear()
    visited_edges.clear()


@router.get("/route/{algorithm_type}")
def route(
    algorithm_type: str,
    start_x: float = DEFAULT_START_X,
    start_y: float = DEFAULT_START_Y,
    end_x: float | None = None,
    end_y: float | None = None,
    distance: int = 6000,
    prefer_new: bool = False,
) -> Route:
    CITY_BBOX = get_city_bbox(start_x, start_y)
    G = get_or_create_graph(start_x, start_y)

    algorithm_map = {
        "random": RandomRoute,
        "dfs": DfsRoute,
        "astar": AStarRoute,
    }

    generator_class = algorithm_map.get(algorithm_type.lower())
    if not generator_class:
        raise ValueError(f"Unsupported algorithm type: {algorithm_type}")

    start_node = ox.nearest_nodes(G, X=start_x, Y=start_y)
    if end_x and end_y:
        end_node = ox.nearest_nodes(G, X=end_x, Y=end_y)
    else:
        end_node = None

    with utils.time_measure("Generating route took: "):
        routes = generator_class(G, visited_edges).generate(
            start_node=start_node,
            end_node=end_node,
            distance=distance,
            prefer_new=prefer_new,
        )
        route = routes[0]

    x, y = utils.route_to_x_y(G, route)
    route_distance = utils.get_route_distance(G, route)
    segments = visited_edges.get_visited_segments(G, route)
    visited_edges.mark_edges_visited(route)

    return Route(rec=CITY_BBOX, x=x, y=y, distance=route_distance, segments=segments)


@router.get("/visited-routes")
def get_visited_routes(
    start_x: float = DEFAULT_START_X,
    start_y: float = DEFAULT_START_Y,
) -> list[list[tuple[float, float]]]:
    G = get_or_create_graph(start_x, start_y)
    result = []

    for u, v in visited_edges:
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

    return result
