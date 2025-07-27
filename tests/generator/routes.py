from datetime import datetime
from typing import Any

import folium as fl
import pytest
from html2image import Html2Image
from html2image.html2image import shutil

from tests.conftest import (
    DEFAULT_Y_X,
    PIOTRKOWSKA_START_X,
    PIOTRKOWSKA_START_Y,
    get_image_path,
)
from travel_map.utils import (
    get_graph_distance,
    route_to_zip_x_y,
)

SAVE_TO_PNG = True
OPEN_IN_BROWSER = False

start_time = None

hti = Html2Image()


def print_coverage(graph, v_edges):
    graph_distance = get_graph_distance(graph)
    visited_routes_distance = v_edges.get_visited_distance(graph)

    print(f"{visited_routes_distance / graph_distance * 100:.2f}")


class Routes:
    generator_class: Any

    NUMBER_OF_ROUTES: int = 12
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
        graph,
        routes: list[list[int]],
        request,
        # TODO refactor this to just points
        default_start: bool = True,
        default_end: bool = False,
    ):
        # if not DEBUG:
        #     return

        for route in routes:
            x_y = route_to_zip_x_y(graph, route, reversed=True)
            fl.PolyLine(x_y).add_to(m)

        if default_start:
            fl.Marker(DEFAULT_Y_X, icon=fl.Icon(color="green")).add_to(m)
        if default_end:
            fl.Marker(
                (PIOTRKOWSKA_START_Y, PIOTRKOWSKA_START_X),
                icon=fl.Icon(color="green"),
            ).add_to(m)

        name = request.node.originalname
        path = get_image_path(self, start_time) / name
        path = str(path)
        html_path = f"{path}.html"
        png_path = f"{path}.png"

        if SAVE_TO_PNG:
            m.save(html_path)
            hti.screenshot(
                html_file=html_path,
                save_as=f"{name}.png",
            )
            shutil.move(f"{name}.png", png_path)

        if OPEN_IN_BROWSER:
            m.show_in_browser()

    def test_start(
        self,
        graph,
        fm,
        start_node,
        generator,
        request,
    ):
        [route] = generator.generate(
            start_node=start_node,
            end_node=None,
            distance=self.DISTANCE,
        )
        assert route

        self.show(fm, graph, [route], request)

    def test_start_end(
        self,
        graph,
        fm,
        start_node,
        end_node,
        generator,
        request,
    ):
        [route] = generator.generate(
            start_node=start_node,
            end_node=end_node,
            distance=self.DISTANCE,
        )
        assert route

        self.show(fm, graph, [route], request, default_end=True)

    def test_start_coverage(
        self,
        graph,
        fm,
        start_node,
        v_edges,
        generator,
        request,
    ):
        routes = []

        for _ in range(self.NUMBER_OF_ROUTES):
            [route] = generator.generate(
                start_node=start_node,
                end_node=None,
                distance=self.DISTANCE,
            )
            v_edges.mark_edges_visited(route)
            routes.append(route)

        print_coverage(graph, v_edges)
        self.show(fm, graph, routes, request, default_end=True)

    def test_start_end_coverage(
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

        for _ in range(self.NUMBER_OF_ROUTES):
            [route] = generator.generate(
                start_node=start_node,
                end_node=end_node,
                distance=self.DISTANCE,
            )
            v_edges.mark_edges_visited(route)
            routes.append(route)

        print_coverage(graph, v_edges)
        self.show(fm, graph, routes, request, default_end=True)

    def test_start_prefer_new_coverage(
        self,
        graph,
        fm,
        start_node,
        v_edges,
        generator,
        request,
    ):
        routes = []

        for _ in range(self.NUMBER_OF_ROUTES):
            [route] = generator.generate(
                start_node=start_node,
                end_node=None,
                distance=self.DISTANCE,
                prefer_new=True,
            )
            v_edges.mark_edges_visited(route)
            routes.append(route)

        print_coverage(graph, v_edges)
        self.show(fm, graph, routes, request, default_end=True)

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

        for _ in range(self.NUMBER_OF_ROUTES):
            [route] = generator.generate(
                start_node=start_node,
                end_node=end_node,
                distance=self.DISTANCE,
                prefer_new=True,
            )
            v_edges.mark_edges_visited(route)
            routes.append(route)

        print_coverage(graph, v_edges)
        self.show(fm, graph, routes, request, default_end=True)
