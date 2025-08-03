import time
from contextlib import contextmanager

from loguru import logger
from networkx import MultiDiGraph


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


def route_to_x_y(
    graph: MultiDiGraph,
    route: list[int],
    reversed: bool = False,
) -> tuple[list[float], list[float]]:
    x = []
    y = []
    for u, v in zip(route[:-1], route[1:]):
        # if there are parallel edges, select the shortest in length
        data = min(graph.get_edge_data(u, v).values(), key=lambda d: d["length"])
        if "geometry" in data:
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
