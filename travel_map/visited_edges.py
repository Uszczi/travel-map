from typing import Generic, Iterator, TypeVar

import networkx as nx
import osmnx as ox

from travel_map.models import Route, Segment, StravaRoute

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
                segment = Segment(new=True, distance=data["length"])
                result.append(segment)
        return result

    def mark_edges_visited(self, route: list[int]):
        for u, v in zip(route[:-1], route[1:]):
            self.add((u, v))


# For more users it has to be refactored
visited_edges = VisitedEdges[tuple[int, int]]()


# TODO co z tym
def strava_route_to_route(graph: nx.MultiDiGraph, strava_route: StravaRoute) -> Route:
    nodes = [ox.nearest_nodes(graph, x, y) for y, x in strava_route.xy]
    return nodes

    segments = [(nodes[i], nodes[i + 1]) for i in range(len(nodes) - 1)]

    return Route(
        # TODO wyznaczyć rec przy pomocy cords
        rec=(0, 0, 0, 0),
        x=[coord[0] for coord in strava_route.xy],
        y=[coord[1] for coord in strava_route.xy],
        # Możesz obliczyć dystans używając `utils.get_route_distance`
        distance=0,
        segments=segments,
    )
