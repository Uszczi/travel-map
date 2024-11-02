from fastapi import FastAPI, Request
import time

import osmnx as ox
from loguru import logger

from fastapi.middleware.cors import CORSMiddleware

from travel_map import utils
from travel_map.generator.random import RandomRoute
from travel_map.models import Route
from travel_map.visited_edges import (
    get_visited_segments,
    mark_edges_visited,
    visited_edges,
)


origins = ["*"]

app = FastAPI()

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
    with utils.time_measure("ox.graph_from_bbox took: "):
        G = ox.graph_from_bbox(CITY_BBOX, network_type="drive")

    start_node_id = ox.distance.nearest_nodes(G, X=start_x, Y=start_y)
    with utils.time_measure("Genereting route took: "):
        route = RandomRoute(G).generate(start_node_id, distance)

    x, y = utils.route_to_x_y(G, route)
    distance = utils.get_route_distance(G, route)

    segments = get_visited_segments(G, route, visited_edges)
    mark_edges_visited(G, route, visited_edges)

    return Route(rec=CITY_BBOX, x=x, y=y, distance=distance, segments=segments)
