from dataclasses import dataclass

import networkx as nx

from app import utils
from app.generator.base import RouteGenerator
from app.visited_edges import VisitedEdges


@dataclass
class DfsRoute(RouteGenerator):
    graph: nx.MultiDiGraph
    v_edges: VisitedEdges

    def _segment_distance(self, path: list[int]) -> float:
        dist = 0.0
        for u, v in zip(path, path[1:]):
            dist += utils.get_distance_between(self.graph, u, v)
        return dist

    def _dfs_segment(
        self,
        s: int,
        t: int | None,
        max_remaining: float,
        prefer_new: bool,
        prefer_new_v2: bool,
        ignored_edges: list[tuple[int, int]],
        ignored_nodes: list[int],
        depth_limit: int,
        used: float,
        min_length: float,
        len_targets: int,
    ) -> list[int]:
        result: list[int] | None = None
        # if len_targets > 1:
        #     min_length = 0

        def dfs(
            current: int, path: list[int], length_so_far: float, depth: int
        ) -> None:
            nonlocal result
            if result is not None:
                return
            if length_so_far > max_remaining:
                return
            if depth > depth_limit:
                return

            if t is None:
                if used + length_so_far > min_length:
                    result = path
                    return

            if current == t and used + length_so_far > min_length / len_targets:
                result = path
                return

            previous = path[-2] if len(path) >= 2 else None
            neighbors = self.get_neighbours_and_sort(
                current,
                prefer_new,
                [previous] if previous is not None else None,
                v2=prefer_new_v2,
                ignored_edges=ignored_edges,
                ignored_nodes=ignored_nodes,
            )
            if prefer_new_v2:
                neighbors = neighbors[:2]

            for nb in neighbors:
                step = utils.get_distance_between(self.graph, current, nb)
                dfs(nb, path + [nb], length_so_far + step, depth + 1)

        dfs(s, [s], 0.0, 0)

        if result is None:
            raise Exception(
                f"Brak ścieżki DFS dla odcinka {s} -> {t} (limit długości/głębokości?)."
            )
        return result

    def generate(
        self,
        start_node: int,
        end_node: int | None,
        distance: int,
        tolerance: float = 0.15,
        prefer_new: bool = False,
        prefer_new_v2: bool = False,
        depth_limit: int = 1000,
        ignored_edges: list[tuple[int, int]] | None = None,
        ignored_nodes: list[int] | None = None,
        middle_nodes: list[int] | None = None,
    ) -> list[int]:
        ignored_edges = ignored_edges or []
        ignored_nodes = ignored_nodes or []
        middle_nodes = middle_nodes or []

        min_length, max_length = self.calculate_min_max_length(tolerance, distance)

        targets: list[int | None] = middle_nodes[:]
        targets.append(end_node)
        len_targets = len(targets)

        route: list[int] = [start_node]
        used = 0.0

        for t in targets:
            max_remaining = (max_length - used) / len(targets)
            if max_remaining <= 0:
                raise Exception(
                    "Przekroczony maksymalny dozwolony dystans (max_length)."
                )

            seg = self._dfs_segment(
                route[-1],
                t,
                min_length=min_length,
                used=used,
                len_targets=len_targets,
                max_remaining=max_remaining,
                prefer_new=prefer_new,
                prefer_new_v2=prefer_new_v2,
                ignored_edges=ignored_edges,
                ignored_nodes=ignored_nodes,
                depth_limit=depth_limit,
            )

            if route[-1] == seg[0]:
                route.extend(seg[1:])
            else:
                route.extend(seg)

            used += self._segment_distance(seg)

        return route
