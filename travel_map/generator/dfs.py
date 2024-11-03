from dataclasses import dataclass

import networkx as nx


@dataclass
class DfsRoute:
    graph: nx.MultiDiGraph

    def generate(
        self,
        start_node: int,
        end_node: int,
        target_length: int,
        tolerance=0.05,
        depth_limit=100,
        allow_first_n=4,
    ) -> list[list[int]]:
        result_paths = []
        min_length = target_length * (1 - tolerance)
        max_length = target_length * (1 + tolerance)

        def dfs(current_node, path, current_length):
            if current_node == end_node and min_length <= current_length <= max_length:
                result_paths.append(path)
                return

            if len(path) > depth_limit or current_length > max_length:
                return

            for neighbor, edge_data in self.graph[current_node].items():
                for data in edge_data.values():
                    edge_length = data.get("length", 0)
                    new_length = current_length + edge_length

                    if (
                        new_length <= max_length
                        and neighbor not in path[allow_first_n:]
                        and neighbor != path[-1]
                    ):
                        dfs(neighbor, path + [neighbor], new_length)

        dfs(start_node, [start_node], 0)
        return result_paths
