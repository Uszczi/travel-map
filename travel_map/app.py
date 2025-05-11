import osmnx as ox
from fastapi import FastAPI

from travel_map import utils
from travel_map.db import mongo_db
from travel_map.generator.dfs import DfsRoute
from travel_map.generator.random import RandomRoute
from travel_map.middlewares import setup_middlewares
from travel_map.models import Route, StravaRoute
from travel_map.visited_edges import (
    get_visited_segments,
    mark_edges_visited,
    strava_route_to_route,
    visited_edges,
)

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


def get_or_create_graph(start_x: float, start_y: float) -> ox.Graph:
    if g := graphs.get("refactor"):
        return g

    with utils.time_measure("ox.graph_from_bbox took: "):
        CITY_BBOX = get_city_bbox(start_x, start_y)
        G = ox.graph_from_bbox(CITY_BBOX, network_type="drive")
        graphs["refactor"] = G
        return G


app = FastAPI()
setup_middlewares(app)

graphs = {}
generated_routes = []


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/clear")
def clear():
    graphs.clear()
    visited_edges.clear()
    generated_routes.clear()


@app.get("/route/dfs")
def route_dfs(
    start_x: float = DEFAULT_START_X,
    start_y: float = DEFAULT_START_Y,
    end_x: float = DEFAULT_START_X,
    end_y: float = DEFAULT_START_Y,
    distance: int = 5000,
) -> Route:
    CITY_BBOX = get_city_bbox(start_x, start_y)
    G = get_or_create_graph(start_x, start_y)

    start_node_id = ox.distance.nearest_nodes(G, X=start_x, Y=start_y)
    end_node_id = ox.distance.nearest_nodes(G, X=end_x, Y=end_y)
    with utils.time_measure("Genereting routes took: "):
        routes = DfsRoute(G).generate(start_node_id, end_node_id, distance)
        print(f"Generated {len(routes)} routes.")

    route = routes[0]
    generated_routes.clear()
    generated_routes.extend(routes[1:])

    x, y = utils.route_to_x_y(G, route)
    distance = utils.get_route_distance(G, route)

    segments = get_visited_segments(G, route, visited_edges)
    mark_edges_visited(G, route, visited_edges)

    return Route(rec=CITY_BBOX, x=x, y=y, distance=distance, segments=segments)


@app.get("/route/next")
def get_next_route() -> Route:
    G = graphs["refactor"]
    route = generated_routes.pop(0)

    x, y = utils.route_to_x_y(G, route)
    distance = utils.get_route_distance(G, route)

    segments = get_visited_segments(G, route, visited_edges)
    mark_edges_visited(G, route, visited_edges)

    return Route(rec=[0, 0, 0, 0], x=x, y=y, distance=distance, segments=segments)


@app.get("/route/{algorithm_type}")
def route(
    algorithm_type: str,
    start_x: float = DEFAULT_START_X,
    start_y: float = DEFAULT_START_Y,
    distance: int = 5000,
) -> Route:
    CITY_BBOX = get_city_bbox(start_x, start_y)
    G = get_or_create_graph(start_x, start_y)

    start_node_id = ox.distance.nearest_nodes(G, X=start_x, Y=start_y)
    with utils.time_measure("Genereting route took: "):
        route = RandomRoute(G).generate(start_node_id, distance)

    x, y = utils.route_to_x_y(G, route)
    distance = utils.get_route_distance(G, route)

    segments = get_visited_segments(G, route, visited_edges)
    mark_edges_visited(G, route, visited_edges)

    return Route(rec=CITY_BBOX, x=x, y=y, distance=distance, segments=segments)


@app.get("/strava/routes")
def get_strava_routes() -> list[StravaRoute]:
    collection = mongo_db["routes"]
    routes = collection.find()
    result = [StravaRoute(**route) for route in routes]
    for route in result:
        route.xy = route.xy[::2]

    return result[:1]


@app.get("/visited-routes")
def get_visited_routes() -> list[list[tuple[float, float]]]:
    start_x: float = DEFAULT_START_X
    start_y: float = DEFAULT_START_Y
    G = get_or_create_graph(start_x, start_y)

    result = []

    for u, v in visited_edges:
        try:
            data = min(G.get_edge_data(u, v).values(), key=lambda d: d["length"])
            if "geometry" in data:
                xs, ys = data["geometry"].xy
                result.append([[y, x] for (x, y) in zip(xs, ys)])
            else:
                result.append(
                    [
                        [
                            G.nodes[u]["y"],
                            G.nodes[u]["x"],
                        ],
                        [
                            G.nodes[v]["y"],
                            G.nodes[v]["x"],
                        ],
                    ]
                )
        except Exception:
            pass

    return result


@app.get("/strava-to-visited")
def strava_to_visited():
    start_x: float = DEFAULT_START_X
    start_y: float = DEFAULT_START_Y
    G = get_or_create_graph(start_x, start_y)

    collection = mongo_db["routes"]
    routes = collection.find()
    result = [StravaRoute(**route) for route in routes]
    for strava_route in result:
        route = strava_route_to_route(G, strava_route)
        route = list(dict.fromkeys(route))
        mark_edges_visited(G, route, visited_edges)

    return "ok"
