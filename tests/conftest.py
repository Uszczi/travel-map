import pytest

from travel_map.api.common import get_or_create_graph


@pytest.fixture(scope="session", autouse=True)
def graph():
    return get_or_create_graph()
