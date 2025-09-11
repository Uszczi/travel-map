from dataclasses import dataclass

import networkx as nx

from travel_map import utils
from travel_map.generator.base import RouteGenerator
from travel_map.visited_edges import VisitedEdges


@dataclass
class RandomRoute(RouteGenerator):
    graph: nx.MultiDiGraph
    v_edges: VisitedEdges

    SEG_MAX_STEPS: int = 300
    SEG_RESTARTS: int = 1000_0000_00

    def _random_segment(
        self,
        s: int,
        t: int,
        min_length: float,
        len_targets: int,
        max_remaining: float,
        prefer_new: bool,
        prefer_new_v2: bool,
        ignored_edges: list[tuple[int, int]],
        ignored_nodes: list[int],
    ) -> list[int]:
        if len_targets > 1:
            min_length = 0

        for _restart in range(self.SEG_RESTARTS + 1):
            path = [s]
            used = 0.0
            current = s
            prev = None

            for _step in range(self.SEG_MAX_STEPS):
                if current == t:
                    if min_length:
                        if used > min_length:
                            return path
                    else:
                        return path

                neighbors = self.get_neighbours_and_sort(
                    current,
                    prefer_new,
                    [prev] if prev is not None else None,
                    v2=prefer_new_v2,
                    ignored_edges=ignored_edges,
                    ignored_nodes=ignored_nodes,
                )

                if not neighbors:
                    if prev is None:
                        break
                    next_node = prev
                else:
                    next_node = neighbors[0]

                next_node = int(next_node)
                step_len = utils.get_distance_between(self.graph, current, next_node)
                if step_len <= 0:
                    break

                if used + step_len > max_remaining:
                    break

                path.append(next_node)
                used += step_len
                prev, current = current, next_node

        raise Exception(
            f"Nie udało się znaleźć segmentu {s} -> {t} w budżecie {max_remaining:.1f} m."
        )

    def _path_length(self, path: list[int]) -> float:
        dist = 0.0
        for u, v in zip(path, path[1:]):
            dist += utils.get_distance_between(self.graph, u, v)
        return dist

    def generate(
        self,
        start_node: int,
        end_node: int | None,
        distance: int,
        tolerance: float = 0.20,
        prefer_new: bool = False,
        prefer_new_v2: bool = False,
        depth_limit: int = 1_000_000,
        ignored_edges: list[tuple[int, int]] | None = None,
        ignored_nodes: list[int] | None = None,
        middle_nodes: list[int] | None = None,
    ) -> list[int]:
        ignored_edges = ignored_edges or []
        ignored_nodes = ignored_nodes or []
        middle_nodes = middle_nodes or []

        min_length, max_length = self.calculate_min_max_length(tolerance, distance)

        targets: list[int] = middle_nodes[:]
        len_targets = len(targets) + 1
        if end_node is not None:
            targets.append(end_node)

        route: list[int] = [start_node]
        used_total = 0.0

        for t in targets:
            max_remaining = max_length - used_total
            if max_remaining <= 0:
                raise Exception(
                    "Przekroczony maksymalny dozwolony dystans (max_length)."
                )

            seg = self._random_segment(
                s=route[-1],
                t=t,
                min_length=min_length,
                len_targets=len_targets,
                max_remaining=max_remaining,
                prefer_new=prefer_new,
                prefer_new_v2=prefer_new_v2,
                ignored_edges=ignored_edges,
                ignored_nodes=ignored_nodes,
            )

            if route[-1] == seg[0]:
                route.extend(seg[1:])
            else:
                route.extend(seg)

            used_total += self._path_length(seg)

        return route
