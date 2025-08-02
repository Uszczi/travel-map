import random
from dataclasses import dataclass

import networkx as nx

from travel_map import utils
from travel_map.generator.base import RouteGenerator
from travel_map.visited_edges import VisitedEdges


@dataclass
class DfsRoute(RouteGenerator):
    graph: nx.MultiDiGraph
    v_edges: VisitedEdges

    def generate(
        self,
        start_node: int,
        end_node: int | None,
        distance: int,
        tolerance: float = 0.15,
        depth_limit: int = 100,
        prefer_new: bool = False,
    ) -> list[int]:
        min_length, max_length = self.calculate_min_max_length(tolerance, distance)
        result = None

        def dfs(current_node, path, current_length):
            nonlocal result
            if result:  # type: ignore[unresolved-reference]
                return

            if min_length <= current_length <= max_length:
                if end_node and current_node != end_node:
                    return
                else:
                    result = path
                    return

            if len(path) > depth_limit or current_length > max_length:
                return

            previous_node = path[-2] if len(path) >= 2 else None
            neighbors = [
                n for n in self.graph.neighbors(current_node) if n != previous_node
            ]
            random.shuffle(neighbors)

            if prefer_new:
                neighbors.sort(
                    key=lambda node: (current_node, node) not in self.v_edges
                    and (node, current_node) not in self.v_edges,
                    reverse=True,
                )

            for neighbor in neighbors:
                c_distance = utils.get_distance_between(
                    self.graph, current_node, neighbor
                )
                new_length = current_length + c_distance

                if new_length <= max_length:
                    dfs(neighbor, path + [neighbor], new_length)

        dfs(start_node, [start_node], 0)

        if not result:
            raise Exception("Couldn't generate DFS route.")

        return result
