import random
from abc import ABC, abstractmethod
from dataclasses import dataclass

import networkx as nx

from travel_map.visited_edges import VisitedEdges


@dataclass
class RouteGenerator(ABC):
    graph: nx.MultiDiGraph
    v_edges: VisitedEdges

    @abstractmethod
    def generate(
        self,
        start_node: int,
        end_node: int | None,
        distance: int,
        tolerance: float = 0.15,
        prefer_new: bool = False,
        depth_limit: int = 100,
    ) -> list[int]: ...

    def calculate_min_max_length(self, tolerance, distance) -> tuple[float, float]:
        min_length = distance * (1 - tolerance)
        max_length = distance * (1 + tolerance)
        return min_length, max_length

    def get_neighbours(
        self, current_node: int, exclude: list[int] | None = None
    ) -> list[int]:
        exclude = exclude or []
        neighbors = [
            neighbor
            for neighbor in self.graph.neighbors(current_node)
            if neighbor not in exclude
        ]
        return neighbors

    def sort(
        self, neighbors: list[int], current_node: int, prefer_new: bool
    ) -> list[int]:
        n = neighbors.copy()
        random.shuffle(n)

        if not prefer_new:
            return n

        n.sort(
            key=lambda node: (current_node, node) not in self.v_edges
            and (node, current_node) not in self.v_edges,
            reverse=True,
        )
        return n

    def sort_by_occurrance(self, neighbors: list[int], current_node: int) -> list[int]:
        n = neighbors.copy()
        random.shuffle(n)

        def _sort(node: int):
            if (current_node, node) in self.v_edges:
                v = self.v_edges[current_node, node]
            elif (node, current_node) in self.v_edges:
                v = self.v_edges[node, current_node]
            else:
                v = 0

            return v

        n.sort(key=_sort)
        return n

    def get_neighbours_and_sort(self, current_node, prefer_new, exclude):
        neighbors = self.get_neighbours(current_node, exclude)
        neighbors = self.sort_by_occurrance(neighbors, current_node)
        # neighbors = self.sort(neighbors, current_node, prefer_new)
        return neighbors
