import math
from dataclasses import dataclass

import networkx as nx
from loguru import logger

from app.generator.base import RouteGenerator
from app.visited_edges import VisitedEdges


def _bearing(graph: nx.MultiDiGraph, u: int, v: int) -> float:
    """Compass-ish bearing (radians) of the edge u -> v from node coordinates."""
    x1, y1 = graph.nodes[u]["x"], graph.nodes[u]["y"]
    x2, y2 = graph.nodes[v]["x"], graph.nodes[v]["y"]
    return math.atan2(y2 - y1, x2 - x1)


def _angle_diff(a: float, b: float) -> float:
    """Smallest absolute angle between two bearings (radians, 0..pi)."""
    d = abs(a - b) % (2 * math.pi)
    return min(d, 2 * math.pi - d)


def remove_edge_both_directions(
    graph: nx.MultiDiGraph,
    unvisited_edges: set[tuple[int, int, int]],
    u: int,
    v: int,
) -> None:
    """Mark the street between u and v covered in *both* directions.

    In an OSMnx drive graph a two-way street is two directed edges,
    (u, v, k) and (v, u, k). Driving it once physically covers the street,
    so we drop every parallel edge between u and v regardless of direction;
    otherwise the reverse edge lingers as "unvisited" and the walk later
    deadheads back over a street it already drove.
    """
    for a, b in ((u, v), (v, u)):
        data = graph.get_edge_data(a, b)
        if data:
            for k in data:
                unvisited_edges.discard((a, b, k))


def choose_next_edge(
    graph: nx.MultiDiGraph,
    current: int,
    outgoing: list[tuple[int, int, int]],
    previous_edge: tuple[int, int, int] | None,
    unvisited_edges: set[tuple[int, int, int]],
) -> tuple[int, int, int]:
    """Pick the next unvisited outgoing edge.

    Heuristic (in priority order):
      1. Avoid immediate u-turns (going straight back the way we came) when
         another option exists.
      2. Prefer edges whose target still has *onward* unvisited edges, so we
         don't dive into dead-ends/stubs and immediately have to retrace them.
      3. Break ties by continuing as straight as possible (smallest turn),
         which keeps the walk flowing forward instead of doubling back.
    """
    candidates = outgoing

    if len(candidates) > 1 and previous_edge is not None:
        prev_node = previous_edge[0]
        no_uturn = [e for e in candidates if e[1] != prev_node]
        if no_uturn:
            candidates = no_uturn

    if len(candidates) == 1:
        return candidates[0]

    def onward_count(edge: tuple[int, int, int]) -> int:
        target = edge[1]
        return sum(
            1
            for oe in graph.out_edges(target, keys=True)
            if oe in unvisited_edges and oe[1] != current
        )

    incoming_bearing = None
    if previous_edge is not None:
        incoming_bearing = _bearing(graph, previous_edge[0], previous_edge[1])

    def turn_penalty(edge: tuple[int, int, int]) -> float:
        if incoming_bearing is None:
            return 0.0
        return _angle_diff(incoming_bearing, _bearing(graph, current, edge[1]))

    # Maximise onward options first, then prefer the straightest continuation.
    return max(
        candidates,
        key=lambda e: (onward_count(e), -turn_penalty(e)),
    )


@dataclass
class AllStreetsRoute(RouteGenerator):
    graph: nx.MultiDiGraph
    v_edges: VisitedEdges

    def generate(
        self,
        start_node: int,
        end_node: int | None = None,
        distance: int = 6000,
        tolerance: float = 0.15,
        prefer_new: bool = False,
        prefer_new_v2: bool = False,
        depth_limit: int = 100,
        ignored_edges: list[tuple[int, int]] | None = None,
        ignored_nodes: list[int] | None = None,
        middle_nodes: list[int] | None = None,
    ) -> list[int]:
        logger.info(
            "AllStreets start={} distance={} unvisited={}",
            start_node,
            distance,
            len(self.graph.edges(keys=True)),
        )

        unvisited_edges = set(self.graph.edges(keys=True))

        route: list[int] = [start_node]
        current = start_node
        previous_edge = None  # Track the actual edge we came from (u, v, k)

        while unvisited_edges:
            logger.debug(
                "AllStreets at node={}, unvisited={}, route_len={}",
                current,
                len(unvisited_edges),
                len(route),
            )
            outgoing = [
                e for e in self.graph.neighbors(current) if e in unvisited_edges
            ]

            if outgoing:
                chosen_edge = choose_next_edge(
                    self.graph, current, outgoing, previous_edge, unvisited_edges
                )
                next_node = chosen_edge[1]

                # Mark the street visited in both directions
                remove_edge_both_directions(
                    self.graph, unvisited_edges, current, next_node
                )

                route.append(next_node)
                previous_edge = chosen_edge  # Remember the edge we just took
                current = next_node

            else:
                # RECOVERY STEP: We are stuck. All immediate streets are visited,
                # but 'unvisited_edges' is not empty. We must "deadhead".

                # Identify all nodes in the graph that still have unvisited outgoing streets
                nodes_with_unvisited = {e[0] for e in unvisited_edges}

                try:
                    # Find the shortest path lengths from 'current' to all other nodes
                    lengths = nx.single_source_shortest_path_length(self.graph, current)

                    # Filter for only the nodes that have unvisited streets, and find the closest one
                    closest_recovery_node = min(
                        (n for n in nodes_with_unvisited if n in lengths),
                        key=lambda n: lengths[n],
                    )

                    # Calculate the actual path to get to that closest node
                    recovery_path = nx.shortest_path(
                        self.graph, source=current, target=closest_recovery_node
                    )

                    # Add the recovery path to our route (skip index 0 as it's our 'current' node)
                    route.extend(recovery_path[1:])
                    for i in range(len(recovery_path) - 1):
                        u, v = recovery_path[i], recovery_path[i + 1]
                        remove_edge_both_directions(self.graph, unvisited_edges, u, v)

                    # Track the last edge in the recovery path
                    if len(recovery_path) >= 2:
                        u, v = recovery_path[-2], recovery_path[-1]
                        edge_data = self.graph.get_edge_data(u, v)
                        if edge_data:
                            k = list(edge_data.keys())[0]
                            previous_edge = (u, v, k)
                        else:
                            previous_edge = None
                    else:
                        previous_edge = None
                    current = closest_recovery_node

                except ValueError:
                    logger.warning(
                        "AllStreets cannot recover at node={}, {} unvisited remain",
                        current,
                        len(unvisited_edges),
                    )
                    break

        logger.info(
            "AllStreets done: route={} nodes, visited={} edges",
            len(route),
            len(self.graph.edges(keys=True)) - len(unvisited_edges),
        )
        return route
