from dataclasses import dataclass, field
from typing import List, Set, Tuple
import heapq
import math
import networkx as nx


@dataclass
class BestFirstRoute:
    graph: nx.MultiDiGraph
    used_edges: Set[Tuple[int, int, int]] = field(default_factory=set)

    def generate(
        self,
        start_node: int,
        end_node: int,
        target_length: float,
        tolerance: float = 0.15,
        depth_limit: int = 100,
        allow_first_n: int = 10,
        not_allow_last_n: int = 5,
    ) -> List[List[int]]:
        result_paths = []
        min_length = target_length * (1 - tolerance)
        max_length = target_length * (1 + tolerance)

        # Pobierz współrzędne końca dla heurystyki
        try:
            end_x = self.graph.nodes[end_node]["x"]
            end_y = self.graph.nodes[end_node]["y"]
        except KeyError:
            raise ValueError("End node nie posiada współrzędnych w grafie.")

        # Heurystyka: odległość euklidesowa od bieżącego węzła do celu
        def heuristic(node: int) -> float:
            x = self.graph.nodes[node]["x"]
            y = self.graph.nodes[node]["y"]
            return math.hypot(x - end_x, y - end_y)

        # Inicjalizacja kolejki priorytetowej (priorytet, długość, krawędzie, aktualny węzeł)
        heap = []
        heapq.heappush(
            heap, (abs(0 + heuristic(start_node) - target_length), 0.0, [], start_node)
        )

        while heap and len(result_paths) < 10:
            priority, current_length, edges, current_node = heapq.heappop(heap)

            # Sprawdź warunki zakończenia
            if current_node == end_node:
                if min_length <= current_length <= max_length:
                    path_nodes = [start_node] + [v for u, v, _ in edges]
                    result_paths.append(path_nodes)
                    self.used_edges.update(edges)
                continue

            # Ograniczenia głębokości i długości
            if len(edges) >= depth_limit or current_length > max_length:
                continue

            # Przetwarzaj sąsiadów
            for neighbor, edges_dict in self.graph[current_node].items():
                for key, data in edges_dict.items():
                    edge = (current_node, neighbor, key)

                    # Pomijaj użyte krawędzie
                    if edge in self.used_edges:
                        continue

                    # Nowa długość i krawędzie
                    new_length = current_length + data.get("length", 0)
                    new_edges = edges + [edge]

                    # Sprawdź ograniczenia długości
                    if new_length > max_length:
                        continue

                    # Generuj listę węzłów dla warunków powtarzania
                    path_nodes = [start_node] + [v for u, v, _ in new_edges]

                    # Sprawdź warunki dotyczące powtarzania węzłów
                    if (
                        len(path_nodes) > allow_first_n
                        and neighbor in path_nodes[allow_first_n:]
                    ):
                        continue

                    if (
                        not_allow_last_n > 0
                        and neighbor in path_nodes[-not_allow_last_n:]
                    ):
                        continue

                    # Oblicz nowy priorytet
                    new_priority = abs(new_length + heuristic(neighbor) - target_length)

                    # Dodaj do kolejki
                    heapq.heappush(
                        heap, (new_priority, new_length, new_edges, neighbor)
                    )

        return result_paths
