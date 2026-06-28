import time
from contextlib import contextmanager
from math import atan2, cos, radians, sin, sqrt
from pathlib import Path

from loguru import logger
from networkx import MultiDiGraph

ROOT_PATH = Path(__file__).parent.parent


@contextmanager
def time_measure(msg: str):
    start_time = time.time()
    yield
    end_time = time.time()
    elapsed_time = end_time - start_time
    logger.info(msg + f"{elapsed_time:.4f} sec.")


def time_measure_decorator(msg: str):
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            elapsed_time = time.time() - start_time
            logger.info(msg + f"{elapsed_time:.4f} sec.")
            return result

        return wrapper

    return decorator


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371000
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    )
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def remove_farthest_nodes(
    graph: MultiDiGraph, center_x: float, center_y: float, radius: float
) -> MultiDiGraph:
    nodes_to_remove = []
    for node, data in graph.nodes(data=True):
        dist = haversine(center_y, center_x, data["y"], data["x"])
        if dist > radius:
            nodes_to_remove.append(node)
    graph.remove_nodes_from(nodes_to_remove)
    return graph


def route_to_x_y(
    graph: MultiDiGraph,
    route: list[int],
    reversed: bool = False,
) -> tuple[list[float], list[float]]:
    x = []
    y = []
    for u, v in zip(route[:-1], route[1:]):
        # if there are parallel edges, select the shortest in length
        # TODO remove try
        try:
            data = min(graph.get_edge_data(u, v).values(), key=lambda d: d["length"])
        except Exception:
            continue

        if data.get("geometry"):
            # if geometry attribute exists, add all its coords to list
            xs, ys = data["geometry"].xy
            x.extend(xs)
            y.extend(ys)
        else:
            # otherwise, the edge is a straight line from node to node
            x.extend((graph.nodes[u]["x"], graph.nodes[v]["x"]))
            y.extend((graph.nodes[u]["y"], graph.nodes[v]["y"]))

    if reversed:
        return y, x
    return x, y


def route_to_zip_x_y(
    graph: MultiDiGraph,
    route: list[int],
    reversed: bool = False,
) -> list[tuple[float, float]]:
    x, y = route_to_x_y(graph, route, reversed)

    return list(zip(x, y))


def zip_x_y(
    x: list[float],
    y: list[float],
) -> list[tuple[float, float]]:
    return list(zip(x, y))


def get_distance_between(graph: MultiDiGraph, start: int, end: int) -> float:
    data = min(graph.get_edge_data(start, end).values(), key=lambda d: d["length"])
    return data["length"]


def get_route_distance(graph: MultiDiGraph, route: list[int]) -> float:
    distance = 0
    for u, v in zip(route[:-1], route[1:]):
        data = min(graph.get_edge_data(u, v).values(), key=lambda d: d["length"])
        distance += data["length"]
    return distance


def get_graph_distance(graph: MultiDiGraph) -> float:
    total = 0
    for start, end, _ in graph.edges:
        distance = get_distance_between(graph, start, end)
        total += distance
    return total
