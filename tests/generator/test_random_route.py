import folium as fl

from tests.conftest import (
    DEFAULT_Y_X,
    END_DEFAULT_Y_X,
)
from travel_map.generator.random import RandomRoute
from travel_map.utils import route_to_x_y, route_to_zip_x_y

DEBUG = False


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


def test_random_route_5_coverage(graph, fm, start_node_id):
    routes = []
    for _ in range(5):
        [route] = RandomRoute(graph).generate(
            start_node_id=start_node_id, end_node_id=None, distance=6_000
        )
        routes.append(route)

    print([len(r) for r in routes])
    assert 0
