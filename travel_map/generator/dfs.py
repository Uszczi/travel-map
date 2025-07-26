from dataclasses import dataclass

from travel_map import utils

import networkx as nx

from travel_map.visited_edges import VisitedEdges


@dataclass
class DfsRoute:
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
    ) -> list[list[int]]:
        result_paths = []
        min_length = distance * (1 - tolerance)
        max_length = distance * (1 + tolerance)

        def dfs(current_node, path, current_length):
            if len(result_paths) >= 1:
                return

            if min_length <= current_length <= max_length:
                if end_node and current_node != end_node:
                    return
                else:
                    result_paths.append(path)
                    return

            if len(path) > depth_limit or current_length > max_length:
                return

            previous_node = path[-2] if len(path) >= 2 else None
            neighbors = [
                n for n in self.graph.neighbors(current_node) if n != previous_node
            ]

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
        return result_paths
