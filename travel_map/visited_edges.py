import networkx as nx
import osmnx as ox

from travel_map.models import Route, Segment, StravaRoute


class VisitedEdges:
    def __init__(self) -> None:
        self._map = {}

    def __getitem__(self, key):
        return self._map[key]

    def __contains__(self, key):
        return key in self._map

    def __len__(self):
        return len(self._map)

    def __iter__(self):
        return iter(self._map)

    def clear(self):
        self._map = {}

    def add(self, key):
        if key in self._map:
            self._map[key] += 1
        else:
            self._map[key] = 1


visited_edges = VisitedEdges()


def get_visited_segments(
    graph: nx.MultiDiGraph, route: list[int], visited_edges: VisitedEdges
) -> list[Segment]:
    result = []
    for u, v in zip(route[:-1], route[1:]):
        data = min(graph.get_edge_data(u, v).values(), key=lambda d: d["length"])
        if (u, v) in visited_edges or (v, u) in visited_edges:
            segment = Segment(new=False, distance=data["length"])
        else:
            segment = Segment(new=True, distance=data["length"])
        result.append(segment)
    return result


def mark_edges_visited(
    graph: nx.MultiGraph, route: list[int], visited_edges: VisitedEdges
):
    for u, v in zip(route[:-1], route[1:]):
        visited_edges.add((u, v))


def strava_route_to_route(graph: nx.MultiDiGraph, strava_route: StravaRoute) -> Route:
    nodes = [ox.distance.nearest_nodes(graph, x, y) for y, x in strava_route.xy]
    return nodes

    segments = [(nodes[i], nodes[i + 1]) for i in range(len(nodes) - 1)]

    return Route(
        rec=[0, 0, 0, 0],
        x=[coord[0] for coord in strava_route.xy],
        y=[coord[1] for coord in strava_route.xy],
        # Możesz obliczyć dystans używając `utils.get_route_distance`
        distance=0,
        segments=segments,
    )
