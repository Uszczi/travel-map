import random
from dataclasses import dataclass

import networkx as nx

from travel_map import utils


@dataclass
class RandomRoute:
    graph: nx.MultiDiGraph

    def generate(
        self, start_node_id: int, end_node_id: int | None, distance: int
    ) -> list[list[int]]:
        route = [start_node_id]
        current_distance, i = 0, 0
        current_node = start_node_id
        previous_node = None

        while (current_distance <= distance) and i < 1000:
            i += 1

            neighbors = [
                n for n in self.graph.neighbors(current_node) if n != previous_node
            ]
            if not neighbors:
                next_node = previous_node
            else:
                next_node = random.choice(neighbors)

            next_node = int(next_node)
            current_distance += utils.get_distance_between(
                self.graph, current_node, next_node
            )

            route.append(next_node)
            previous_node = current_node
            current_node = next_node

        return [route]
