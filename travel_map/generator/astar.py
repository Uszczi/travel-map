import heapq
import random
from dataclasses import dataclass
from math import atan2, cos, radians, sin, sqrt

import networkx as nx

from travel_map import utils
from travel_map.generator.base import RouteGenerator
from travel_map.visited_edges import VisitedEdges


def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # promień Ziemi w metrach
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    )
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def heuristic(graph: nx.MultiDiGraph, a: int, b: int) -> float:
    # Uwaga: w OSMnx x=lon, y=lat. Haversine(lat, lon, ...)
    lon1 = graph.nodes[a]["x"]
    lat1 = graph.nodes[a]["y"]
    lon2 = graph.nodes[b]["x"]
    lat2 = graph.nodes[b]["y"]
    return haversine(lat1, lon1, lat2, lon2)


@dataclass
class AStarRoute(RouteGenerator):
    graph: nx.MultiDiGraph
    v_edges: VisitedEdges

    def _reconstruct_path(self, came_from: dict[int, int], current: int) -> list[int]:
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path

    def _segment_distance(self, path: list[int]) -> float:
        dist = 0.0
        for u, v in zip(path, path[1:]):
            dist += utils.get_distance_between(self.graph, u, v)
        return dist

    def _astar_segment(
        self,
        s: int,
        t: int,
        max_remaining: float,
        prefer_new: bool,
        prefer_new_v2: bool,
        ignored_edges: list[tuple[int, int]],
    ) -> list[int]:
        open_set: list[tuple[float, int]] = []
        heapq.heappush(open_set, (heuristic(self.graph, s, t), s))

        came_from: dict[int, int] = {}
        g_score: dict[int, float] = {s: 0.0}

        while open_set:
            _, u = heapq.heappop(open_set)

            if u == t:
                return self._reconstruct_path(came_from, u)

            prev = came_from.get(u)

            neighbors = self.get_neighbours_and_sort(
                u,
                prefer_new,
                [prev] if prev is not None else None,
                v2=prefer_new_v2,
                ignored_edges=ignored_edges,
            )
            if prefer_new_v2:
                neighbors = neighbors[:2]

            for v in neighbors:
                tentative_g = g_score[u] + utils.get_distance_between(self.graph, u, v)
                if tentative_g > max_remaining:
                    continue

                if tentative_g < g_score.get(v, float("inf")):
                    came_from[v] = u
                    g_score[v] = tentative_g
                    f = tentative_g + heuristic(self.graph, v, t)
                    heapq.heappush(open_set, (f, v))

        raise Exception(f"Brak ścieżki dla odcinka {s} -> {t} (limit długości?).")

    def generate(
        self,
        start_node: int,
        end_node: int,
        distance: int,
        tolerance: float = 0.30,
        prefer_new: bool = False,
        prefer_new_v2: bool = False,
        depth_limit: int = 0,
        ignored_edges: list[tuple[int, int]] | None = None,
        ignored_nodes: list[int] | None = None,
        middle_nodes: list[int] | None = None,
    ) -> list[int]:
        ignored_edges = ignored_edges or []
        ignored_nodes = ignored_nodes or []
        middle_nodes = middle_nodes or []

        min_length, max_length = self.calculate_min_max_length(tolerance, distance)

        targets: list[int] = middle_nodes[:]
        if end_node is not None:
            targets.append(end_node)

        route: list[int] = [start_node]
        used = 0.0

        for t in targets:
            max_remaining = max_length - used
            if max_remaining <= 0:
                raise Exception(
                    "Przekroczony maksymalny dozwolony dystans (max_length)."
                )

            seg = self._astar_segment(
                route[-1],
                t,
                max_remaining,
                prefer_new=prefer_new,
                prefer_new_v2=prefer_new_v2,
                ignored_edges=ignored_edges,
            )

            if route[-1] == seg[0]:
                route.extend(seg[1:])
            else:
                route.extend(seg)

            used += self._segment_distance(seg)

        return route
