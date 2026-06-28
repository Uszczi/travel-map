from unittest.mock import MagicMock, patch

import networkx as nx
import pytest

from app.api.common import graphs
from app.serializers.geocode import GeocodeItem
from app.visited_edges import visited_edges

pytestmark = [pytest.mark.asyncio]


@pytest.fixture
def mock_graph():
    G = nx.MultiDiGraph()
    G.add_node(1, x=19.2, y=51.6)
    G.add_node(2, x=19.21, y=51.61)
    G.add_node(3, x=19.22, y=51.62)
    G.add_node(4, x=19.23, y=51.63)
    G.add_edge(1, 2, length=100.0, geometry=None)
    G.add_edge(2, 3, length=150.0, geometry=None)
    G.add_edge(3, 4, length=200.0, geometry=None)
    return G


@pytest.fixture
def mock_route_generator():
    with patch("app.api.route_generation.RandomRoute") as mock_random:
        mock_random.return_value.generate = MagicMock(return_value=[1, 2, 3, 4])
        yield mock_random


@pytest.fixture(autouse=True)
def clear_graphs_and_edges():
    graphs.clear()
    visited_edges.clear()
    yield
    graphs.clear()
    visited_edges.clear()


async def test_index_page(client):
    res = await client.get("/")

    assert res.status_code == 200, res.text
    assert "text/html" in res.headers["content-type"]
    body = res.text
    assert 'id="map"' in body
    assert "leaflet" in body.lower()
    assert "htmx.org" in body
    assert "/htmx/route" in body


async def test_static_css_served(client):
    res = await client.get("/static/css/app.css")

    assert res.status_code == 200
    assert "text/css" in res.headers["content-type"]


@patch("app.api.route_generation.get_or_create_graph")
@patch("app.api.route_generation.ox.nearest_nodes")
async def test_htmx_route_returns_fragment(
    mock_nearest_nodes,
    mock_get_graph,
    client,
    mock_graph,
    mock_route_generator,
):
    mock_get_graph.return_value = mock_graph
    mock_nearest_nodes.side_effect = [1, 3]

    res = await client.get("/htmx/route?algorithm=random&distance=4000")

    assert res.status_code == 200, res.text
    body = res.text
    assert "Generated route" in body
    assert "window.TravelMap.drawRoute" in body
    # No full HTML document — just a fragment.
    assert "<!DOCTYPE html>" not in body


async def test_htmx_visited_routes(client, mock_graph):
    with patch(
        "app.api.route_generation.get_or_create_graph", return_value=mock_graph
    ):
        visited_edges.add((1, 2))

        res = await client.get("/htmx/visited-routes")

    assert res.status_code == 200, res.text
    assert "window.TravelMap.drawVisited" in res.text


async def test_htmx_geocode_results(client):
    items = [
        GeocodeItem(
            id=1,
            label="Warsaw, Poland",
            lat=52.23,
            lng=21.01,
            type="city",
            boundingbox=[52.0, 52.4, 20.8, 21.3],
        )
    ]
    with patch("app.web.htmx.NominatimService") as mock_cls:
        mock_cls.return_value.search = _async_return(items)

        res = await client.get("/htmx/geocode?q=Warsaw")

    assert res.status_code == 200, res.text
    body = res.text
    assert "Warsaw, Poland" in body
    assert 'data-lat="52.23"' in body
    assert "window.TravelMap.flyTo" in body


async def test_htmx_geocode_empty_query(client):
    res = await client.get("/htmx/geocode?q=")

    assert res.status_code == 200
    assert "window.TravelMap.flyTo" not in res.text


def _async_return(value):
    async def _inner(*args, **kwargs):
        return value

    return _inner
