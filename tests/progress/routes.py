from datetime import datetime
from typing import Any

import folium as fl
import networkx as nx
import pytest
from playwright.sync_api import sync_playwright

from tests.conftest import (
    get_image_path,
)
from travel_map.utils import (
    get_graph_distance,
    route_to_zip_x_y,
)

SAVE_TO_PNG = False
OPEN_IN_BROWSER = False

start_time = None


def print_coverage(graph, v_edges):
    graph_distance = get_graph_distance(graph)
    visited_routes_distance = v_edges.get_visited_distance(graph)

    print(f"{visited_routes_distance / graph_distance * 100:.2f}")


class Routes:
    generator_class: Any

    NUMBER_OF_ROUTES: int = 10
    DISTANCE: int = 6_000

    @pytest.fixture(autouse=True)
    def init(self) -> None:
        global start_time
        if start_time is None:
            start_time = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

    @pytest.fixture()
    def generator(self, graph, v_edges):
        return self.generator_class(graph, v_edges)

    def show(
        self,
        m: fl.Map,
        graph: nx.MultiDiGraph,
        routes: list[list[int]],
        request,
        start_node: int | None = None,
        end_node: int | None = None,
    ):
        # if not isinstance(routes[0], int):
        #     routes = [routes]

        for route in routes:
            x_y = route_to_zip_x_y(graph, route, reversed=True)
            fl.PolyLine(x_y).add_to(m)

        if start_node:
            fl.Marker(
                (graph.nodes[start_node]["y"], graph.nodes[start_node]["x"]),
                icon=fl.Icon(color="green"),
            ).add_to(m)
        if end_node:
            fl.Marker(
                (graph.nodes[end_node]["y"], graph.nodes[end_node]["x"]),
                icon=fl.Icon(color="red"),
            ).add_to(m)

        if SAVE_TO_PNG:
            name = request.node.originalname
            path = get_image_path(self, start_time) / name
            path = str(path)
            html_path = f"{path}.html"
            png_path = f"{path}.png"
            m.save(html_path)

            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                page.goto(f"file://{html_path}")
                # TODO
                page.wait_for_timeout(1000)
                page.screenshot(path=png_path, full_page=True)
                browser.close()

        if OPEN_IN_BROWSER:
            m.show_in_browser()

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
        graph_distance = get_graph_distance(graph)

        routes = []
        diff = []

        for _ in range(self.NUMBER_OF_ROUTES):
            route = generator.generate(
                start_node=start_node,
                end_node=end_node,
                distance=self.DISTANCE,
                prefer_new=True,
            )
            v_edges.mark_edges_visited(route)
            routes.append(route)
            print(len(route))

            visited_routes_distance = v_edges.get_visited_distance(graph)
            diff.append(
                (visited_routes_distance - (diff[0] if len(diff) > 0 else 0))
                / graph_distance
            )

        print()
        diff = [int(d * 100) for d in diff]
        print(diff)
        print()
        print_coverage(graph, v_edges)
        self.show(fm, graph, routes, request, start_node=start_node, end_node=end_node)
