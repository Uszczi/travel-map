from tests.benchmarks.benchmark import Benchamarks
from travel_map.generator.astar import AStarRoute


class TestAStarRoute(Benchamarks):
    generator_class = AStarRoute

    def test_start(self, graph, start_node, times): ...

    def test_start_prefer_new(self, graph, start_node, times): ...
