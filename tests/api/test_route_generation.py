from unittest.mock import AsyncMock, MagicMock, patch

import networkx as nx
import pytest

from app.api.common import graphs
from app.models import Route, Segment
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
    G.add_edge(2, 1, length=100.0, geometry=None)
    G.add_edge(2, 3, length=150.0, geometry=None)
    G.add_edge(3, 2, length=150.0, geometry=None)
    G.add_edge(3, 4, length=200.0, geometry=None)
    G.add_edge(4, 3, length=200.0, geometry=None)
    G.add_edge(1, 3, length=250.0, geometry=None)
    G.add_edge(3, 1, length=250.0, geometry=None)
    G.add_edge(2, 4, length=350.0, geometry=None)
    G.add_edge(4, 2, length=350.0, geometry=None)
    return G


@pytest.fixture
def mock_elevation_service():
    with patch("app.api.route_generation.ElevationService") as mock_cls:
        mock_instance = mock_cls.return_value
        mock_instance.get = MagicMock(
            return_value={
                (19.2, 51.6): 100,
                (19.21, 51.61): 110,
                (19.22, 51.62): 105,
                (19.23, 51.63): 115,
            }
        )
        mock_instance.covert_to_list = MagicMock(return_value=[100, 110, 105, 115])
        mock_instance.calculate_total_gain_lose = MagicMock(return_value=(15, 5))
        yield mock_instance


@pytest.fixture
def mock_route_generator():
    with (
        patch("app.api.route_generation.RandomRoute") as mock_random,
        patch("app.api.route_generation.DfsRoute") as mock_dfs,
        patch("app.api.route_generation.AStarRoute") as mock_astar,
    ):

        mock_route = [1, 2, 3, 4]

        for mock_cls in [mock_random, mock_dfs, mock_astar]:
            mock_instance = mock_cls.return_value
            mock_instance.generate = MagicMock(return_value=mock_route)

        yield mock_random, mock_dfs, mock_astar


@pytest.fixture(autouse=True)
def clear_graphs_and_edges():
    graphs.clear()
    visited_edges.clear()
    yield
    graphs.clear()
    visited_edges.clear()


async def test_clear_endpoint(client):
    graphs["refactor"] = nx.MultiDiGraph()
    visited_edges.add((1, 2))

    res = await client.get("/clear")

    assert res.status_code == 200
    assert graphs == {}
    assert len(visited_edges) == 0


async def test_route_invalid_algorithm(client):
    res = await client.get("/route/invalid_algorithm")

    assert res.status_code == 422


@patch("app.api.route_generation.get_or_create_graph")
@patch("app.api.route_generation.ox.nearest_nodes")
async def test_route_random_algorithm(
    mock_nearest_nodes,
    mock_get_graph,
    client,
    mock_graph,
    mock_elevation_service,
    mock_route_generator,
):
    mock_get_graph.return_value = mock_graph
    mock_nearest_nodes.side_effect = [1, 3]

    res = await client.get("/route/random")

    assert res.status_code == 200, res.json()
    data = res.json()
    assert "x" in data
    assert "y" in data
    assert "distance" in data
    assert "segments" in data
    assert "elevation" in data
    assert "total_gain" in data
    assert "total_lose" in data


@patch("app.api.route_generation.get_or_create_graph")
@patch("app.api.route_generation.ox.nearest_nodes")
async def test_route_dfs_algorithm(
    mock_nearest_nodes,
    mock_get_graph,
    client,
    mock_graph,
    mock_elevation_service,
    mock_route_generator,
):
    mock_get_graph.return_value = mock_graph
    mock_nearest_nodes.side_effect = [1, 3]

    res = await client.get("/route/dfs")

    assert res.status_code == 200, res.json()


@patch("app.api.route_generation.get_or_create_graph")
@patch("app.api.route_generation.ox.nearest_nodes")
async def test_route_astar_algorithm(
    mock_nearest_nodes,
    mock_get_graph,
    client,
    mock_graph,
    mock_elevation_service,
    mock_route_generator,
):
    mock_get_graph.return_value = mock_graph
    mock_nearest_nodes.side_effect = [1, 3]

    res = await client.get("/route/astar")

    assert res.status_code == 200, res.json()


@patch("app.api.route_generation.get_or_create_graph")
@patch("app.api.route_generation.ox.nearest_nodes")
async def test_route_with_end_coordinates(
    mock_nearest_nodes,
    mock_get_graph,
    client,
    mock_graph,
    mock_elevation_service,
    mock_route_generator,
):
    mock_get_graph.return_value = mock_graph
    mock_nearest_nodes.side_effect = [1, 3]

    res = await client.get("/route/random?end_x=19.22&end_y=51.62")

    assert res.status_code == 200, res.json()


@patch("app.api.route_generation.get_or_create_graph")
@patch("app.api.route_generation.ox.nearest_nodes")
async def test_route_with_custom_distance(
    mock_nearest_nodes,
    mock_get_graph,
    client,
    mock_graph,
    mock_elevation_service,
    mock_route_generator,
):
    mock_get_graph.return_value = mock_graph
    mock_nearest_nodes.side_effect = [1, 3]

    res = await client.get("/route/random?distance=10000")

    assert res.status_code == 200, res.json()


@patch("app.api.route_generation.get_or_create_graph")
@patch("app.api.route_generation.ox.nearest_nodes")
async def test_route_with_prefer_new(
    mock_nearest_nodes,
    mock_get_graph,
    client,
    mock_graph,
    mock_elevation_service,
    mock_route_generator,
):
    mock_get_graph.return_value = mock_graph
    mock_nearest_nodes.side_effect = [1, 3]

    res = await client.get("/route/random?prefer_new=true")

    assert res.status_code == 200, res.json()


async def test_visited_routes_endpoint(client, mock_graph, mock_elevation_service):
    with patch("app.api.route_generation.get_or_create_graph", return_value=mock_graph):
        visited_edges.add((1, 2))

        res = await client.get("/visited-routes")

        assert res.status_code == 200, res.json()
        data = res.json()
        assert isinstance(data, list)


async def test_visited_edges_as_points_endpoint(
    client, mock_graph, mock_elevation_service
):
    with patch("app.api.route_generation.get_or_create_graph", return_value=mock_graph):
        visited_edges.add((1, 2))

        res = await client.get("/visited-edges-as-points")

        assert res.status_code == 200, res.json()
        data = res.json()
        assert isinstance(data, list)


@patch("app.api.route_generation.get_or_create_graph")
@patch("app.api.route_generation.ox.nearest_nodes")
async def test_route_response_structure(
    mock_nearest_nodes,
    mock_get_graph,
    client,
    mock_graph,
    mock_elevation_service,
    mock_route_generator,
):
    mock_get_graph.return_value = mock_graph
    mock_nearest_nodes.side_effect = [1, 3]

    res = await client.get("/route/random")

    assert res.status_code == 200
    data = res.json()

    assert isinstance(data["rec"], list)
    assert len(data["rec"]) == 4
    assert isinstance(data["x"], list)
    assert isinstance(data["y"], list)
    assert isinstance(data["distance"], float)
    assert isinstance(data["segments"], list)
    assert isinstance(data["elevation"], list)
    assert isinstance(data["total_gain"], int)
    assert isinstance(data["total_lose"], int)

    for segment in data["segments"]:
        assert "new" in segment
        assert "distance" in segment
        assert isinstance(segment["new"], bool)
        assert isinstance(segment["distance"], float)
