from typing import Any

import folium as fl

from tests.conftest import (
    DEFAULT_Y_X,
    END_DEFAULT_Y_X,
)
from travel_map.utils import (
    get_graph_distance,
    route_to_zip_x_y,
)

DEBUG = False


def show(
    m: fl.Map,
    graph,
    route,
    default_start: bool = True,
    default_end: bool = False,
):
    if not DEBUG:
        return

    x_y = route_to_zip_x_y(graph, route, reversed=True)
    fl.PolyLine(x_y).add_to(m)

    if default_start:
        fl.Marker(DEFAULT_Y_X, icon=fl.Icon(color="green")).add_to(m)
    if default_end:
        fl.Marker(END_DEFAULT_Y_X, icon=fl.Icon(color="green")).add_to(m)

    m.show_in_browser()


def print_coverage(graph, v_edges):
    graph_distance = get_graph_distance(graph)
    visited_routes_distance = v_edges.get_visited_distance(graph)

    print(f"{visited_routes_distance / graph_distance * 100:.2f}")


class Routes:
    generator_class: Any

    NUMBER_OF_ROUTES: int = 12
    DISTANCE: int = 10_000

    def test_start(self, graph, fm, start_node, v_edges):
        [route] = self.generator_class(graph, v_edges).generate(
            start_node=start_node,
            end_node=None,
            distance=self.DISTANCE,
        )
        assert route

        show(fm, graph, route)

    def test_start_end(self, graph, fm, start_node, end_node, v_edges):
        [route] = self.generator_class(graph, v_edges).generate(
            start_node=start_node,
            end_node=end_node,
            distance=self.DISTANCE,
        )
        assert route

        show(fm, graph, route, default_end=True)
