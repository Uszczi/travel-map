from dataclasses import dataclass
import random
import networkx as nx

from travel_map import utils
from travel_map.generator.base import RouteGenerator
from travel_map.visited_edges import VisitedEdges


@dataclass
class RandomRoute(RouteGenerator):
    graph: nx.MultiDiGraph
    v_edges: VisitedEdges

    # proste limity dla pojedynczego segmentu
    SEG_MAX_STEPS: int = 10_000  # maks. kroków losowych na segment
    SEG_RESTARTS: int = 1000  # ile restartów segmentu, zanim uznamy porażkę

    def _random_segment(
        self,
        s: int,
        t: int,
        max_remaining: float,
        prefer_new: bool,
        prefer_new_v2: bool,
        ignored_edges: list[tuple[int, int]],
    ) -> list[int]:
        for _restart in range(self.SEG_RESTARTS + 1):
            path = [s]
            used = 0.0
            current = s
            prev = None

            for _step in range(self.SEG_MAX_STEPS):
                if current == t:
                    return path

                neighbors = self.get_neighbours_and_sort(
                    current,
                    prefer_new,
                    [prev] if prev is not None else None,
                    v2=prefer_new_v2,
                    ignored_edges=ignored_edges,
                )

                if not neighbors:
                    # ślepy zaułek – spróbuj wrócić 1 krok, jeśli się da
                    if prev is None:
                        break  # restart segmentu
                    next_node = prev
                else:
                    # unikaj natychmiastowego zawracania, jeśli są inne opcje
                    cand = [n for n in neighbors if n != prev] or neighbors
                    next_node = random.choice(cand)

                next_node = int(next_node)
                step_len = utils.get_distance_between(self.graph, current, next_node)
                if step_len <= 0:
                    # bezsensowny krok – spróbuj innego sąsiada w tej iteracji
                    # (jeśli nie ma innych, restart segmentu)
                    # tu: po prostu restartujemy segment
                    break

                if used + step_len > max_remaining:
                    # przekroczylibyśmy budżet segmentu – restart
                    break

                # wykonaj krok
                path.append(next_node)
                used += step_len
                prev, current = current, next_node

            # jeśli pętla skończyła się bez dotarcia do t, robimy restart
            # po wyczerpaniu restartów – zwracamy porażkę
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
        depth_limit: int = 1_000_000,  # nieużywane tutaj bezpośrednio
        ignored_edges: list[tuple[int, int]] | None = None,
        middle_nodes: list[int] | None = None,
    ) -> list[int]:
        ignored_edges = ignored_edges or []
        middle_nodes = (middle_nodes or [])[:]

        min_length, max_length = self.calculate_min_max_length(tolerance, distance)

        targets: list[int] = middle_nodes[:]
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
                max_remaining=max_remaining,
                prefer_new=prefer_new,
                prefer_new_v2=prefer_new_v2,
                ignored_edges=ignored_edges,
            )

            if route[-1] == seg[0]:
                route.extend(seg[1:])
            else:
                route.extend(seg)

            used_total += self._path_length(seg)

        # if used_total < min_length:
        #     raise Exception(
        #         f"Trasa segmentowa {used_total:.1f} m krótsza niż min_length {min_length:.1f} m. "
        #         f"Zwiększ distance/tolerance lub dodaj więcej punktów pośrednich."
        #     )

        return route
