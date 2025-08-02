import osmnx as ox

from tests.generator.routes import Routes, print_coverage
from travel_map.generator.astar import AStarRoute


class TestAStarRoutes(Routes):
    generator_class = AStarRoute

    def test_start_coverage(self, graph, fm, start_node, v_edges): ...

    def test_start_prefer_new_coverage(self, graph, fm, start_node, v_edges): ...

    def test_start_end_prefer_new_coverage(
        self,
        graph,
        fm,
        start_node,
        end_node,
        v_edges,
        generator,
        request,
    ):
        routes = []
        end_node = ox.nearest_nodes(graph, X=19.194585084915165, Y=51.61247380201653)

        for _ in range(3):
            [route] = generator.generate(
                start_node=start_node,
                end_node=end_node,
                distance=self.DISTANCE,
                prefer_new=True,
            )
            v_edges.mark_edges_visited(route)
            routes.append(route)

        print_coverage(graph, v_edges)
        self.show(fm, graph, routes, request, end_node=end_node)
