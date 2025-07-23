import folium
import osmnx as ox
import pytest

from travel_map.api.common import get_or_create_graph

DEFAULT_START_X = 19.1999532
DEFAULT_START_Y = 51.6101241
END_DEFAULT_START_X = 19.1912713
END_DEFAULT_START_Y = 51.6191531

DEFAULT_X_Y = (DEFAULT_START_X, DEFAULT_START_Y)
DEFAULT_Y_X = (DEFAULT_START_Y, DEFAULT_START_X)
END_DEFAULT_X_Y = (END_DEFAULT_START_X, END_DEFAULT_START_Y)
END_DEFAULT_Y_X = (END_DEFAULT_START_Y, END_DEFAULT_START_X)


@pytest.fixture()
def graph():
    return get_or_create_graph(DEFAULT_START_X, DEFAULT_START_Y)


@pytest.fixture()
def start_node_id(graph):
    return ox.nearest_nodes(graph, X=DEFAULT_START_X, Y=DEFAULT_START_Y)


@pytest.fixture()
def end_node_id(graph):
    return ox.nearest_nodes(graph, X=END_DEFAULT_START_X, Y=END_DEFAULT_START_Y)


@pytest.fixture()
def fm():
    return folium.Map(location=(DEFAULT_START_Y, DEFAULT_START_X), zoom_start=15)
