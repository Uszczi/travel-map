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


def heuristic(graph, a, b):
    lat1 = graph.nodes[a]["x"]
    lon1 = graph.nodes[a]["y"]
    lat2 = graph.nodes[b]["x"]
    lon2 = graph.nodes[b]["y"]
    return haversine(lat1, lon1, lat2, lon2)


@dataclass
class AStarRoute(RouteGenerator):
    graph: nx.MultiDiGraph
    v_edges: VisitedEdges

    def generate(
        self,
        start_node: int,
        end_node: int,
        distance: int,
        tolerance: float = 0.30,
        prefer_new: bool = False,
        depth_limit: int = 0,
    ) -> list[list[int]]:
        min_length, max_length = self.calculate_min_max_length(tolerance, distance)
        open_set = [(0.0, start_node)]
        came_from = {}
        g_score = {start_node: 0.0}

        if end_node:
            change_end_node = False
        else:
            change_end_node = True

        def to_route(current, came_from) -> list[int]:
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            return list(reversed(path))

        while open_set:
            _, current = heapq.heappop(open_set)
            previous_node = came_from.get(current)

            if change_end_node:
                neighbors = [n for n in self.graph.neighbors(current)]
                second_neighbors = set()
                for n in neighbors:
                    second_neighbors.update(self.graph.neighbors(n))

                second_neighbors.discard(current)
                second_neighbors.difference_update(neighbors)

                end_node = random.choice(list(second_neighbors))

            if current == end_node:
                return [to_route(current, came_from)]

            if current == end_node and g_score[current] >= min_length:
                return [to_route(current, came_from)]

            neighbors = [n for n in self.graph.neighbors(current) if n != previous_node]
            if prefer_new:
                n_neighbors = [
                    n
                    for n in neighbors
                    if (n, current) not in self.v_edges
                    and (current, n) not in self.v_edges
                ]

                if n_neighbors:
                    neighbors = n_neighbors

            for neighbor in neighbors:
                tmp_g_score = g_score[current] + utils.get_distance_between(
                    self.graph, current, neighbor
                )

                if tmp_g_score > max_length:
                    continue

                if neighbor not in g_score or tmp_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tmp_g_score
                    f_score = tmp_g_score + heuristic(self.graph, neighbor, end_node)
                    heapq.heappush(open_set, (f_score, neighbor))

        raise Exception("Nie udało się znaleźć ścieżki A*.")
