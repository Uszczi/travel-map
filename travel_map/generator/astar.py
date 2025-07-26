import random
import heapq
from dataclasses import dataclass

import networkx as nx

from travel_map import utils
from travel_map.visited_edges import VisitedEdges
from dataclasses import dataclass

import networkx as nx

from travel_map import utils
from travel_map.visited_edges import VisitedEdges

from math import radians, sin, cos, sqrt, atan2


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
class AStarRoute:
    graph: nx.MultiDiGraph
    v_edges: VisitedEdges

    def generate(
        self,
        start_node: int,
        end_node: int,
        distance: int,
        prefer_new: bool = False,
        tolerance: float = 0.30,
    ) -> list[list[int]]:
        min_length = distance * (1 - tolerance)
        max_length = distance * (1 + tolerance)

        open_set = [(0.0, start_node)]
        came_from = {}
        g_score = {start_node: 0.0}

        while open_set:
            a, current = heapq.heappop(open_set)
            print(a)

            # printx(g_score)

            if current == end_node and g_score[current] >= min_length:
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                return [list(reversed(path))]

            for neighbor in self.graph.neighbors(current):
                # TODO
                # Pomijaj krawędź prowadzącą z powrotem (opcjonalnie)

                # TODO co jesli sie skonczą
                # if prefer_new and (
                #     (current, neighbor) in self.v_edges
                #     or (neighbor, current) in self.v_edges
                # ):
                #     continue

                tmp_g_score = g_score[current] + utils.get_distance_between(
                    self.graph, current, neighbor
                )

                if tmp_g_score > max_length:
                    path = [current]
                    while current in came_from:
                        current = came_from[current]
                        path.append(current)
                    return [list(reversed(path))]
                    continue

                if neighbor not in g_score or tmp_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tmp_g_score
                    f_score = tmp_g_score + heuristic(self.graph, neighbor, end_node)
                    heapq.heappush(open_set, (f_score, neighbor))

        raise Exception("Nie udało się znaleźć ścieżki A*.")
