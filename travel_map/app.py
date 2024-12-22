from fastapi import FastAPI, Request
import time

import osmnx as ox
from loguru import logger
from travel_map.db import mongo_db

from fastapi.middleware.cors import CORSMiddleware

from travel_map import utils
from travel_map.generator.dfs import DfsRoute
from travel_map.generator.random import RandomRoute
from travel_map.models import Route, StravaRoute
from travel_map.visited_edges import (
    get_visited_segments,
    mark_edges_visited,
    visited_edges,
)


origins = ["*"]

app = FastAPI()
graphs = {}
generated_routes = []

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def measure_execution_time(request: Request, call_next):
    start_time = time.time()

    logger.info(f"{request.url} start.")
    response = await call_next(request)

    process_time = time.time() - start_time
    logger.info(f"{request.url} took {process_time:.4f} sec.")

    return response


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/clear")
def clear():
    visited_edges.clear()
    generated_routes.clear()


@app.get("/route/dfs")
def route_dfs(
    start_x: float = 19.1999532,
    start_y: float = 51.6101241,
    end_x: float = 19.1999532,
    end_y: float = 51.6101241,
    distance: int = 5000,
) -> Route:
    # ) -> list[list[tuple[float, float]]]:
    CITY_BBOX_DEFAULT_SIZE = 0.04
    CITY_BBOX = (
        start_x - CITY_BBOX_DEFAULT_SIZE * 2,
        start_y - CITY_BBOX_DEFAULT_SIZE,
        start_x + CITY_BBOX_DEFAULT_SIZE * 2,
        start_y + CITY_BBOX_DEFAULT_SIZE,
    )
    if "refactor" in graphs:
        G = graphs["refactor"]
    else:
        with utils.time_measure("ox.graph_from_bbox took: "):
            G = ox.graph_from_bbox(CITY_BBOX, network_type="drive")
            graphs["refactor"] = G

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
    start_x: float = 19.1999532,
    start_y: float = 51.6101241,
    distance: int = 5000,
) -> Route:
    CITY_BBOX_DEFAULT_SIZE = 0.04
    CITY_BBOX = (
        start_x - CITY_BBOX_DEFAULT_SIZE * 2,
        start_y - CITY_BBOX_DEFAULT_SIZE,
        start_x + CITY_BBOX_DEFAULT_SIZE * 2,
        start_y + CITY_BBOX_DEFAULT_SIZE,
    )
    if "refactor" in graphs:
        G = graphs["refactor"]
    else:
        with utils.time_measure("ox.graph_from_bbox took: "):
            G = ox.graph_from_bbox(CITY_BBOX, network_type="drive")
            graphs["refactor"] = G

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

    return result[:10]


@app.get("/visited-routes")
def get_visited_routes() -> list[list[tuple[float, float]]]:
    start_x: float = 19.1999532
    start_y: float = 51.6101241
    CITY_BBOX_DEFAULT_SIZE = 0.04
    CITY_BBOX = (
        start_x - CITY_BBOX_DEFAULT_SIZE * 2,
        start_y - CITY_BBOX_DEFAULT_SIZE,
        start_x + CITY_BBOX_DEFAULT_SIZE * 2,
        start_y + CITY_BBOX_DEFAULT_SIZE,
    )
    if "refactor" in graphs:
        G = graphs["refactor"]
    else:
        with utils.time_measure("ox.graph_from_bbox took: "):
            G = ox.graph_from_bbox(CITY_BBOX, network_type="drive")
            graphs["refactor"] = G

    result = []

    for u, v in visited_edges:
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

    return result
