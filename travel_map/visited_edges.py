import networkx as nx

from travel_map.models import Segment


class VisitedEdges:
    def __init__(self) -> None:
        self._map = {}

    def __getitem__(self, key):
        return self._map[key]

    def __contains__(self, key):
        return key in self._map

    def __len__(self):
        return len(self._map)

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
