import statistics
import time

import osmnx as ox

from travel_map.api.common import DEFAULT_START_X, DEFAULT_START_Y
from travel_map.generator.random import RandomRoute


def test_10_random_route(graph):
    start_node_id = ox.nearest_nodes(graph, X=DEFAULT_START_X, Y=DEFAULT_START_Y)

    times = []
    for _ in range(12):
        start_time = time.time()
        RandomRoute(graph).generate(
            start_node_id=start_node_id, end_node_id=None, distance=10000
        )
        end_time = time.time()

        times.append(end_time - start_time)

    times.remove(max(times))
    times.remove(min(times))

    print(f"\nGenerating random route at avg took: {statistics.mean(times):.6f}s")


def test_10_random_route_start_end(graph):
    start_node_id = ox.nearest_nodes(graph, X=DEFAULT_START_X, Y=DEFAULT_START_Y)

    times = []
    for _ in range(12):
        start_time = time.time()
        RandomRoute(graph).generate(
            start_node_id=start_node_id, end_node_id=None, distance=10000
        )
        end_time = time.time()

        times.append(end_time - start_time)

    times.remove(max(times))
    times.remove(min(times))

    print(
        f"\nGenerating random route start end at avg took: {statistics.mean(times):.6f}s"
    )


def test_10_random_route_round(graph):
    start_node_id = ox.nearest_nodes(graph, X=DEFAULT_START_X, Y=DEFAULT_START_Y)

    times = []
    for _ in range(12):
        start_time = time.time()
        RandomRoute(graph).generate(
            start_node_id=start_node_id, end_node_id=None, distance=10000
        )
        end_time = time.time()

        times.append(end_time - start_time)

    times.remove(max(times))
    times.remove(min(times))

    print(f"\nGenerating random route round at avg took: {statistics.mean(times):.6f}s")
