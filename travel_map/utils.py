from networkx import MultiDiGraph


def route_to_x_y(
    graph: MultiDiGraph,
    route: list[int],
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

    return x, y


def get_distance_between(graph: MultiDiGraph, start: int, end: int):
    print(start, end)
    data = min(graph.get_edge_data(start, end).values(), key=lambda d: d["length"])
    return data["length"]


def get_route_distance(graph: MultiDiGraph, route: list[int]) -> float:
    distance = 0
    for u, v in zip(route[:-1], route[1:]):
        # if there are parallel edges, select the shortest in length
        data = min(graph.get_edge_data(u, v).values(), key=lambda d: d["length"])
        distance += data["length"]
    return distance
