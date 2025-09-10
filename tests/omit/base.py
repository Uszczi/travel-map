from datetime import datetime
from typing import Any

import folium as fl
import gpxpy
import networkx as nx
import osmnx as ox
import pytest
from playwright.sync_api import sync_playwright

from tests.conftest import (
    get_image_path,
)
from travel_map.utils import (
    ROOT_PATH,
    get_graph_distance,
    route_to_zip_x_y,
)

INIT_DATA_PATH = ROOT_PATH / "init_data"

SAVE_TO_PNG = False
SAVE_TO_HTML = True or SAVE_TO_PNG
OPEN_IN_BROWSER = False

P = (1177493762, 1177493777)  # "Środek Piotrkowskiej"
L = (1177493766, 1177493886)  # "Odnoga na początku Lubelskiej"
W = (2131056242, 2131056249)  # "Wysoka"
IGNORED_EDGES = (P, L, W)


start_time = None


def print_coverage(graph, v_edges):
    graph_distance = get_graph_distance(graph)
    visited_routes_distance = v_edges.get_visited_distance(graph)

    print(f"{visited_routes_distance / graph_distance * 100:.2f}")


class Routes:
    generator_class: Any
    use_end_node: bool = True

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
        paths: list[list[int]] | None = None,
    ):
        # if not isinstance(routes[0], int):
        #     routes = [routes]

        for path in paths or []:
            x_y = route_to_zip_x_y(graph, path, reversed=True)
            fl.PolyLine(x_y, color="red").add_to(m)

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

        if SAVE_TO_HTML:
            name = request.node.originalname
            path = get_image_path(self, start_time) / name
            path = str(path)
            html_path = f"{path}.html"
            m.save(html_path)

            if SAVE_TO_PNG:
                png_path = f"{path}.png"
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

    def load_init_data(self, graph, v_edges) -> list[list[int]]:
        paths = []
        for path in sorted(INIT_DATA_PATH.glob("*.gpx")):
            with path.open("r", encoding="utf-8") as f:
                gpx = gpxpy.parse(f)

            points: list[tuple[float, float]] = []
            if gpx.tracks:
                for trk in gpx.tracks:
                    for seg in trk.segments:
                        for p in seg.points:
                            points.append((float(p.longitude), float(p.latitude)))
            elif gpx.routes:
                for rte in gpx.routes:
                    for p in rte.points:
                        points.append((float(p.longitude), float(p.latitude)))

            x: list[float] = []
            y: list[float] = []
            prev = None
            for lon, lat in points:
                pair = (lon, lat)
                if pair != prev:
                    x.append(lon)
                    y.append(lat)
                    prev = pair

            nodes = ox.nearest_nodes(graph, x, y)
            nodes = list(dict.fromkeys(nodes))

            filtered_nodes = []
            _nodes = nodes[:]
            current_node = _nodes.pop(0)
            next_node = _nodes.pop(0)
            while _nodes:
                if graph.get_edge_data(current_node, next_node):
                    filtered_nodes.append(current_node)
                    filtered_nodes.append(next_node)
                    current_node = next_node
                    if _nodes:
                        next_node = _nodes.pop(0)
                else:
                    # TODO
                    # Move tail few time (50?) until it finds edge otherwise move head
                    current_node = next_node
                    if _nodes:
                        next_node = _nodes.pop(0)

            filtered_nodes = list(dict.fromkeys(filtered_nodes))
            paths.append(filtered_nodes)

        for path in paths:
            v_edges.mark_edges_visited(path)

        return paths

    def test_omit(
        self,
        graph,
        fm,
        start_node,
        end_node,
        v_edges,
        generator,
        request,
    ):
        paths = self.load_init_data(graph, v_edges)
        print_coverage(graph, v_edges)

        routes = []
        for _ in range(self.NUMBER_OF_ROUTES):
            route = generator.generate(
                start_node=start_node,
                end_node=end_node if self.use_end_node else None,
                distance=self.DISTANCE,
                prefer_new=True,
                ignored_edges=IGNORED_EDGES,
            )
            if route:
                v_edges.mark_edges_visited(route)
                routes.append(route)
            else:
                print("Generating route failed.")

        print_coverage(graph, v_edges)
        self.show(fm, graph, routes, request, start_node, end_node, paths)
