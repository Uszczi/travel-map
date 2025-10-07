from typing import Generic, Iterator, TypeVar

import networkx as nx

from app.models import Segment
from app.utils import get_distance_between

K = TypeVar("K")


class VisitedEdges(Generic[K]):
    def __init__(self) -> None:
        self._map: dict[K, int] = {}

    def __getitem__(self, key: K) -> int:
        return self._map[key]

    def __contains__(self, key: K) -> bool:
        return key in self._map

    def __len__(self) -> int:
        return len(self._map)

    def __iter__(self) -> Iterator[K]:
        return iter(self._map)

    def clear(self) -> None:
        self._map.clear()

    def add(self, key: K) -> None:
        if key in self._map:
            self._map[key] += 1
        else:
            self._map[key] = 1

    def get_visited_segments(
        self,
        graph: nx.MultiDiGraph,
        route: list[int],
    ) -> list[Segment]:
        result = []
        for u, v in zip(route[:-1], route[1:]):
            data = min(graph.get_edge_data(u, v).values(), key=lambda d: d["length"])
            if (u, v) in self._map or (v, u) in self._map:
                segment = Segment(new=False, distance=data["length"])
            else:
                segment = Segment(new=True, distance=data["length"])
            result.append(segment)
        return result

    def get_visited_distance(self, graph: nx.MultiDiGraph) -> float:
        visited_routes_distance = 0

        for start, end, _ in graph.edges:
            if (start, end) in self._map or (end, start) in self._map:
                visited_routes_distance += get_distance_between(graph, start, end)

        return visited_routes_distance

    def mark_edges_visited(self, route: list[int]):
        for u, v in zip(route[:-1], route[1:]):
            self.add((u, v))


# For more users it has to be refactored
visited_edges = VisitedEdges[tuple[int, int]]()
