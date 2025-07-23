import folium as fl
import matplotlib

from tests.conftest import (
    DEFAULT_Y_X,
    END_DEFAULT_Y_X,
)
from travel_map.generator.random import RandomRoute
from travel_map.utils import (
    get_graph_distance,
    route_to_zip_x_y,
)
from travel_map.visited_edges import VisitedEdges

DEBUG = False

matplotlib.use("QtAgg")


def show(m: fl.Map):
    if not DEBUG:
        return

    m.show_in_browser()


def test_random_route(graph, fm, start_node_id):
    [route] = RandomRoute(graph).generate(
        start_node_id=start_node_id, end_node_id=None, distance=6_000
    )

    x_y = route_to_zip_x_y(graph, route, reversed=True)
    fl.PolyLine(x_y).add_to(fm)
    fl.Marker(DEFAULT_Y_X, icon=fl.Icon(color="green")).add_to(fm)
    show(fm)


def test_random_route_end(graph, fm, start_node_id, end_node_id):
    [route] = RandomRoute(graph).generate(
        start_node_id=start_node_id, end_node_id=end_node_id, distance=6_000
    )

    x_y = route_to_zip_x_y(graph, route, reversed=True)
    fl.PolyLine(x_y).add_to(fm)
    fl.Marker(DEFAULT_Y_X, icon=fl.Icon(color="green")).add_to(fm)
    fl.Marker(END_DEFAULT_Y_X, icon=fl.Icon(color="red")).add_to(fm)
    show(fm)


def test_random_route_coverage(graph, fm, start_node_id):
    routes = []
    visited_edges = VisitedEdges[tuple[int, int]]()

    for _ in range(10):
        [route] = RandomRoute(graph).generate(
            start_node_id=start_node_id,
            end_node_id=None,
            distance=6_000,
        )
        visited_edges.mark_edges_visited(route)
        routes.append(route)

    graph_distance = get_graph_distance(graph)
    visited_routes_distance = visited_edges.get_visited_distance(graph)

    print(graph_distance)
    print(visited_routes_distance)
    print(visited_routes_distance / graph_distance * 100)
    assert 0


def test_random_route_end_coverage(graph, fm, start_node_id, end_node_id):
    routes = []
    visited_edges = VisitedEdges[tuple[int, int]]()

    for _ in range(10):
        [route] = RandomRoute(graph).generate(
            start_node_id=start_node_id,
            end_node_id=end_node_id,
            distance=6_000,
        )
        visited_edges.mark_edges_visited(route)
        routes.append(route)

    graph_distance = get_graph_distance(graph)
    visited_routes_distance = visited_edges.get_visited_distance(graph)

    print(graph_distance)
    print(visited_routes_distance)
    print(visited_routes_distance / graph_distance * 100)
    assert 0


def test_random_prefer_new_route_coverage(graph, fm, start_node_id):
    routes = []
    visited_edges = VisitedEdges[tuple[int, int]]()

    for _ in range(10):
        [route] = RandomRoute(graph).generate(
            start_node_id=start_node_id,
            end_node_id=None,
            distance=6_000,
            prefer_new=True,
        )
        visited_edges.mark_edges_visited(route)
        routes.append(route)

    graph_distance = get_graph_distance(graph)
    visited_routes_distance = visited_edges.get_visited_distance(graph)

    print(graph_distance)
    print(visited_routes_distance)
    print(visited_routes_distance / graph_distance * 100)
    assert 0


def test_random_prefer_new_route_end_coverage(graph, fm, start_node_id, end_node_id):
    routes = []
    visited_edges = VisitedEdges[tuple[int, int]]()

    for _ in range(10):
        [route] = RandomRoute(graph).generate(
            start_node_id=start_node_id,
            end_node_id=end_node_id,
            distance=6_000,
            prefer_new=True,
        )
        visited_edges.mark_edges_visited(route)
        routes.append(route)

    graph_distance = get_graph_distance(graph)
    visited_routes_distance = visited_edges.get_visited_distance(graph)

    print(graph_distance)
    print(visited_routes_distance)
    print(visited_routes_distance / graph_distance * 100)
    assert 0
