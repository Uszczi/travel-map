from dataclasses import dataclass
from fastapi import FastAPI

from pydantic import BaseModel
import networkx as nx
import random
import osmnx as ox

from fastapi.middleware.cors import CORSMiddleware

from travel_map import utils


origins = ["*"]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


class Route(BaseModel):
    rec: tuple[float, float, float, float]
    x: list[float]
    y: list[float]
    distance: float


@dataclass
class RandomRoute:
    graph: nx.MultiDiGraph

    def generate(self, start_node_id: int, distance: int) -> list[int]:
        route = [start_node_id]
        current_distance, i = 0, 0
        current_node = start_node_id
        previous_node = None

        while (current_distance <= distance) and i < 1000:
            i += 1

            neighbors = [
                n for n in self.graph.neighbors(current_node) if n != previous_node
            ]
            if not neighbors:
                next_node = previous_node
            else:
                next_node = random.choice(neighbors)

            current_distance += utils.get_distance_between(
                self.graph, current_node, next_node
            )

            route.append(next_node)
            previous_node = current_node
            current_node = next_node

        return route


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
    G = ox.graph_from_bbox(CITY_BBOX, network_type="drive")
    start_node_id = ox.distance.nearest_nodes(G, X=start_x, Y=start_y)
    route = RandomRoute(G).generate(start_node_id, distance)

    x, y = utils.route_to_x_y(G, route)
    distance = utils.get_route_distance(G, route)

    return Route(rec=CITY_BBOX, x=x, y=y, distance=distance)
