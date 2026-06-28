import osmnx as ox

from app.api.common import get_city_bbox
from app.utils import remove_farthest_nodes

from app.generator.all_streets_random import AllStreetsRoute
from app.visited_edges import VisitedEdges

import networkx as nx


def keep_largest_component(graph: nx.MultiDiGraph) -> nx.MultiDiGraph:
    # 1. Get all weakly connected components (returns a list of sets of nodes)
    components = list(nx.weakly_connected_components(graph))

    if not components:
        return graph

    # 2. Find the largest component by measuring the length of each set
    largest_component_nodes = max(components, key=len)

    # 3. Create and return a new graph containing ONLY those nodes
    # .copy() ensures it becomes an independent graph, not just a view
    cleaned_graph = graph.subgraph(largest_component_nodes).copy()

    return cleaned_graph


def remove_isolated_nodes(graph: nx.MultiDiGraph):
    # Find all nodes that have no edges connected to them
    isolates = list(nx.isolates(graph))

    # Remove them from the graph
    graph.remove_nodes_from(isolates)


def test_random_route():
    DEFAULT_START_X = 19.1999532
    DEFAULT_START_Y = 51.6101241
    start_x = DEFAULT_START_X
    start_y = DEFAULT_START_Y

    CITY_BBOX = get_city_bbox(start_x, start_y, size=0.02)
    G = ox.graph_from_bbox(CITY_BBOX, network_type="drive")

    G = remove_farthest_nodes(G, start_x, start_y, radius=1000)
    remove_isolated_nodes(G)
    G = keep_largest_component(G)

    print(len(list(G.nodes())))

    ox.plot_graph(G)

    all_streets = AllStreetsRoute(G, v_edges=VisitedEdges())
    start_node = ox.nearest_nodes(G, X=start_x, Y=start_y)
    route = all_streets.generate(start_node=start_node)

    print(route)

    ox.plot_graph(G)
    assert 0
