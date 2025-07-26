from tests.generator.routes import Routes

from travel_map.generator.astar import AStarRoute
from travel_map.generator.dfs import DfsRoute


class TestAStarRoutes(Routes):
    generator_class = AStarRoute

    def test_start(self, graph, fm, start_node, v_edges): ...
    def test_start_coverage(self, graph, fm, start_node, v_edges): ...
    def test_start_prefer_new_coverage(self, graph, fm, start_node, v_edges): ...
