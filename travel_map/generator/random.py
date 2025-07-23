import random
from dataclasses import dataclass

import networkx as nx

from travel_map import utils


@dataclass
class RandomRoute:
    graph: nx.MultiDiGraph

    def generate(
        self,
        start_node_id: int,
        end_node_id: int | None,
        distance: int,
        prefer_new: bool = False,
    ) -> list[list[int]]:
        route = [start_node_id]
        current_distance = 0
        iterations = 0
        current_node = start_node_id
        previous_node = None

        while iterations < 100_000:
            iterations += 1

            neighbors = [
                n for n in self.graph.neighbors(current_node) if n != previous_node
            ]
            if not neighbors:
                next_node = previous_node
            else:
                if prefer_new:
                    # TODO
                    ...
                else:
                    next_node = random.choice(neighbors)

            next_node = int(next_node)
            current_distance += utils.get_distance_between(
                self.graph, current_node, next_node
            )

            route.append(next_node)
            previous_node = current_node
            current_node = next_node

            if end_node_id:
                if current_distance > distance * 1.4:
                    route = [start_node_id]
                    current_distance = 0
                    current_node = start_node_id
                    previous_node = None
                    continue

                if distance * 0.8 < current_distance and end_node_id == current_node:
                    return [route]
            else:
                if current_distance > distance:
                    return [route]

        return []
