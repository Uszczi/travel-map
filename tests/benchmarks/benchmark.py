import statistics
import time
from contextlib import contextmanager
from typing import Any

import pytest

from travel_map.visited_edges import VisitedEdges

visited_edges = VisitedEdges[tuple[int, int]]()


@contextmanager
def save_time(times: list[float]):
    start_time = time.time()
    yield
    end_time = time.time()

    times.append(end_time - start_time)


class Benchamarks:
    # TODO it can be some kind of protocol
    generator_class: Any

    NUMBER_OF_ROUTES = 10
    DISTANCE = 6_000

    @pytest.fixture()
    def times(self):
        return []

    def show_times(self, times: list[float]) -> None:
        assert len(times) == self.NUMBER_OF_ROUTES

        times.remove(max(times))
        times.remove(min(times))

        print(
            f"\nGenerating {self.generator_class.__name__} route at avg took: {statistics.mean(times):.6f}s"
        )

    def test_start(self, graph, start_node, times):
        for _ in range(self.NUMBER_OF_ROUTES):
            with save_time(times):
                self.generator_class(graph, visited_edges).generate(
                    start_node=start_node,
                    end_node=None,
                    distance=self.DISTANCE,
                )

        self.show_times(times)

    def test_start_end(self, graph, start_node, end_node, times):
        for _ in range(self.NUMBER_OF_ROUTES):
            with save_time(times):
                self.generator_class(graph, visited_edges).generate(
                    start_node=start_node,
                    end_node=end_node,
                    distance=self.DISTANCE,
                )

        self.show_times(times)

    def test_start_prefer_new(self, graph, start_node, times):
        for _ in range(self.NUMBER_OF_ROUTES):
            with save_time(times):
                self.generator_class(graph, visited_edges).generate(
                    start_node=start_node,
                    end_node=None,
                    distance=self.DISTANCE,
                )

        self.show_times(times)

    def test_start_end_prefer_new(self, graph, start_node, end_node, times):
        for _ in range(self.NUMBER_OF_ROUTES):
            with save_time(times):
                self.generator_class(graph, visited_edges).generate(
                    start_node=start_node,
                    end_node=end_node,
                    distance=self.DISTANCE,
                )

        self.show_times(times)
