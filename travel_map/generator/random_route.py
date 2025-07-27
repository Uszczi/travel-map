import random
from dataclasses import dataclass

import networkx as nx

from travel_map import utils
from travel_map.generator.base import RouteGenerator
from travel_map.visited_edges import VisitedEdges


@dataclass
class RandomRoute(RouteGenerator):
    graph: nx.MultiDiGraph
    v_edges: VisitedEdges

    def generate(
        self,
        start_node: int,
        end_node: int | None,
        distance: int,
        tolerance: float = 0.15,
        prefer_new: bool = False,
        depth_limit: int = 10_000_000,
    ) -> list[list[int]]:
        route = [start_node]
        current_distance = 0
        iterations = 0
        current_node = start_node
        previous_node = None
        min_length, max_length = self.calculate_min_max_length(tolerance, distance)

        while iterations < depth_limit:
            iterations += 1

            neighbors = [
                n for n in self.graph.neighbors(current_node) if n != previous_node
            ]
            if not neighbors:
                next_node = previous_node
            else:
                if prefer_new:
                    n_neighbors = [
                        n
                        for n in neighbors
                        if (current_node, n) not in self.v_edges
                        and (n, current_node) not in self.v_edges
                    ]
                    if n_neighbors:
                        next_node = random.choice(n_neighbors)
                    else:
                        next_node = random.choice(neighbors)
                else:
                    next_node = random.choice(neighbors)

            next_node = int(next_node)
            current_distance += utils.get_distance_between(
                self.graph, current_node, next_node
            )

            route.append(next_node)
            previous_node = current_node
            current_node = next_node

            if end_node:
                if current_distance > max_length:
                    route = [start_node]
                    current_distance = 0
                    current_node = start_node
                    previous_node = None
                    continue

                if current_distance > min_length and end_node == current_node:
                    return [route]
            else:
                if current_distance > min_length:
                    return [route]

        raise Exception("Couldn't generate random route.")
