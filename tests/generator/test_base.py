import pytest

from travel_map.generator.base import RouteGenerator


class DummyGenerator(RouteGenerator):
    def generate(
        self,
        start_node: int,
        end_node: int | None,
        distance: int,
        tolerance: float = 0.15,
        prefer_new: bool = False,
        depth_limit: int = 100,
    ) -> list[int]:
        return []


@pytest.fixture()
def mark_edges_visited(v_edges):
    v_edges.add((0, 1))
    v_edges.add((0, 3))
    v_edges.add((6, 0))


@pytest.fixture()
def generator(graph, v_edges):
    generator = DummyGenerator(graph, v_edges)
    return generator


@pytest.mark.parametrize(
    "node, neighbors, prefer_new, expected",
    (
        (0, [], True, []),
        (0, [], False, []),
        (0, [1, 2, 3, 4, 5, 6], True, [4, 5, 2, 3, 6, 1]),
        (0, [1, 2, 3, 4, 5, 6], False, [3, 4, 6, 1, 5, 2]),
        (0, [6, 5, 4, 3, 2, 1], True, [4, 2, 5, 3, 1, 6]),
        (0, [6, 5, 4, 3, 2, 1], False, [4, 3, 1, 6, 2, 5]),
        (0, [1, 5, 6, 3, 4, 2], True, [2, 4, 5, 6, 3, 1]),
        (0, [1, 5, 6, 3, 4, 2], False, [6, 3, 2, 1, 4, 5]),
    ),
)
@pytest.mark.usefixtures("temporary_seed", "mark_edges_visited")
def test_sort(generator, node, neighbors, prefer_new, expected):
    result = generator.sort(neighbors, node, prefer_new)

    assert result == expected, result
