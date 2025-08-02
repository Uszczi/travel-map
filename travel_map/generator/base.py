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

    def calculate_min_max_length(self, tolerance, distance):
        min_length = distance * (1 - tolerance)
        max_length = distance * (1 + tolerance)
        return min_length, max_length
