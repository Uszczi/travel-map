import matplotlib.pyplot as plt
import networkx as nx
import osmnx as ox
from matplotlib.collections import LineCollection

from app.api.common import get_city_bbox
from app.generator.all_streets_random import (
    AllStreetsRoute,
    choose_next_edge,
    remove_edge_both_directions,
)
from app.utils import remove_farthest_nodes
from app.visited_edges import VisitedEdges


def keep_largest_component(graph: nx.MultiDiGraph) -> nx.MultiDiGraph:
    components = list(nx.weakly_connected_components(graph))
    if not components:
        return graph
    largest = max(components, key=len)
    return graph.subgraph(largest).copy()


def remove_isolated_nodes(graph: nx.MultiDiGraph):
    isolates = list(nx.isolates(graph))
    graph.remove_nodes_from(isolates)


def build_edge_coords(G, u, v):
    """Return list of (lon, lat) tuples for edge (u->v)."""
    data = G.get_edge_data(u, v)
    if data is None:
        data = G.get_edge_data(v, u)
        if data is None:
            return None
    data = data[list(data.keys())[0]]
    if "geometry" in data and data["geometry"] is not None:
        return list(data["geometry"].coords)
    x1, y1 = G.nodes[u]["x"], G.nodes[u]["y"]
    x2, y2 = G.nodes[v]["x"], G.nodes[v]["y"]
    return [(x1, y1), (x2, y2)]


def step_generator(generator: AllStreetsRoute, start_node: int):
    """Yield (route, current, unvisited_edges, step_type, recovery_len) at each algorithm step."""
    graph = generator.graph
    unvisited_edges = set(graph.edges(keys=True))
    route = [start_node]
    current = start_node
    previous_edge = None  # Track the actual edge we came from (u, v, k)
    recovery_len = 0
    step_no = 0

    yield route.copy(), current, unvisited_edges.copy(), "start", recovery_len
    print(f"step {step_no}: route = {route}")

    while unvisited_edges:
        outgoing = [
            e for e in graph.out_edges(current, keys=True) if e in unvisited_edges
        ]

        if outgoing:
            chosen_edge = choose_next_edge(
                graph, current, outgoing, previous_edge, unvisited_edges
            )
            next_node = chosen_edge[1]
            remove_edge_both_directions(graph, unvisited_edges, current, next_node)
            route.append(next_node)
            previous_edge = chosen_edge  # Remember the edge we just took
            current = next_node
            step_no += 1
            yield route.copy(), current, unvisited_edges.copy(), "greedy", recovery_len
            print(f"step {step_no}: greedy -> {current}, route = {route}")
        else:
            nodes_with_unvisited = {e[0] for e in unvisited_edges}
            try:
                lengths = nx.single_source_shortest_path_length(graph, current)
                closest = min(
                    (n for n in nodes_with_unvisited if n in lengths),
                    key=lambda n: lengths[n],
                )
                recovery_path = nx.shortest_path(graph, source=current, target=closest)
                recovery_len = len(recovery_path) - 1
                route.extend(recovery_path[1:])

                for i in range(len(recovery_path) - 1):
                    u, v = recovery_path[i], recovery_path[i + 1]
                    remove_edge_both_directions(graph, unvisited_edges, u, v)

                # Track the last edge in the recovery path
                if len(recovery_path) >= 2:
                    u, v = recovery_path[-2], recovery_path[-1]
                    edge_data = graph.get_edge_data(u, v)
                    if edge_data:
                        k = list(edge_data.keys())[0]
                        previous_edge = (u, v, k)
                    else:
                        previous_edge = None
                else:
                    previous_edge = None
                current = closest

                step_no += 1
                yield route.copy(), current, unvisited_edges.copy(), "recovery", recovery_len
                print(f"step {step_no}: recovery -> {current}, route = {route}")
            except ValueError:
                step_no += 1
                yield route.copy(), current, unvisited_edges.copy(), "stuck", recovery_len
                print(f"step {step_no}: stuck at {current}")

    step_no += 1
    yield route.copy(), current, unvisited_edges.copy(), "done", recovery_len
    print(f"step {step_no}: done, route = {route}")


def main():
    DEFAULT_START_X = 19.1999532
    DEFAULT_START_Y = 51.6101241

    print("Downloading graph...")
    CITY_BBOX = get_city_bbox(DEFAULT_START_X, DEFAULT_START_Y, size=0.02)
    G = ox.graph_from_bbox(CITY_BBOX, network_type="drive")
    G = remove_farthest_nodes(G, DEFAULT_START_X, DEFAULT_START_Y, radius=500)
    remove_isolated_nodes(G)
    G = keep_largest_component(G)

    print(f"Graph: {len(G.nodes)} nodes, {len(G.edges)} edges")
    print("Node IDs:", sorted(G.nodes()))

    v_edges = VisitedEdges()
    generator = AllStreetsRoute(G, v_edges=v_edges)
    start_node = ox.nearest_nodes(G, X=DEFAULT_START_X, Y=DEFAULT_START_Y)

    # Collect all steps first
    all_steps = list(step_generator(generator, start_node))
    total = len(all_steps)
    print(f"Total steps: {total}")

    # Build background edge segments
    all_segments = []
    for u, v, k, data in G.edges(keys=True, data=True):
        if "geometry" in data and data["geometry"] is not None:
            coords = list(data["geometry"].coords)
        else:
            x1, y1 = G.nodes[u]["x"], G.nodes[u]["y"]
            x2, y2 = G.nodes[v]["x"], G.nodes[v]["y"]
            coords = [(x1, y1), (x2, y2)]
        all_segments.append(coords)

    fig, ax = plt.subplots(figsize=(14, 10))
    fig.subplots_adjust(bottom=0.08)

    bg = LineCollection(all_segments, linewidths=0.3, colors="lightgray", alpha=0.4)
    ax.add_collection(bg)

    remaining_lc = LineCollection(
        [], linewidths=0.6, colors="orange", alpha=0.5, zorder=2
    )
    visited_lc = LineCollection(
        [], linewidths=2.5, colors="#4A90D9", alpha=0.5, zorder=3
    )
    route_lc = LineCollection([], linewidths=3.0, colors="#2ECC40", alpha=0.9, zorder=4)
    recovery_lc = LineCollection(
        [], linewidths=3.0, colors="#FF4136", linestyle="dashed", alpha=0.8, zorder=4
    )
    start_marker = ax.plot([], [], "go", markersize=10, zorder=6, label="start")[0]
    current_marker = ax.plot([], [], "ro", markersize=8, zorder=6, label="current")[0]

    for coll in (remaining_lc, visited_lc, route_lc, recovery_lc):
        ax.add_collection(coll)

    ax.autoscale()
    ax.set_aspect("equal")
    ax.axis("off")

    title = ax.set_title("", fontsize=12)
    stats_text = ax.text(
        0.02,
        0.02,
        "",
        transform=ax.transAxes,
        fontsize=10,
        verticalalignment="bottom",
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.8),
    )

    step_index = [0]

    def draw(step_idx):
        route, current, unvisited, step_type, recovery_len = all_steps[step_idx]

        visited_set = set()
        for i in range(len(route) - 1):
            u, v = route[i], route[i + 1]
            visited_set.add((u, v))
            visited_set.add((v, u))

        remaining_segs = []
        visited_segs = []
        route_segs = []
        recovery_segs = []

        for u, v, k, data in G.edges(keys=True, data=True):
            is_visited = (u, v) in visited_set or (v, u) in visited_set
            edge_key = (u, v, k)
            coords = None

            if "geometry" in data and data["geometry"] is not None:
                coords = list(data["geometry"].coords)
            else:
                x1, y1 = G.nodes[u]["x"], G.nodes[u]["y"]
                x2, y2 = G.nodes[v]["x"], G.nodes[v]["y"]
                coords = [(x1, y1), (x2, y2)]

            if edge_key in unvisited:
                remaining_segs.append(coords)
            elif is_visited:
                visited_segs.append(coords)

        # Build route path segments (the path taken so far)
        for i in range(len(route) - 1):
            u, v = route[i], route[i + 1]
            coords = build_edge_coords(G, u, v)
            if coords is None:
                continue

            is_recovery = False
            if step_type == "recovery":
                rl = recovery_len
                if len(route) - 1 - rl <= i < len(route) - 1:
                    is_recovery = True

            if is_recovery:
                recovery_segs.append(coords)
            else:
                route_segs.append(coords)

        remaining_lc.set_segments(remaining_segs)
        visited_lc.set_segments(visited_segs)
        route_lc.set_segments(route_segs)
        recovery_lc.set_segments(recovery_segs)

        cx, cy = G.nodes[current]["x"], G.nodes[current]["y"]
        sx, sy = G.nodes[route[0]]["x"], G.nodes[route[0]]["y"]
        current_marker.set_data([cx], [cy])
        start_marker.set_data([sx], [sy])

        total_edges = len(set(G.edges(keys=True)))
        unvisited_count = len(unvisited)
        visited_count = total_edges - unvisited_count
        pct = visited_count / total_edges * 100 if total_edges else 0

        step_label = step_type.upper()
        title.set_text(
            f"Step {step_idx + 1}/{total} — {step_label}  |  "
            f"route length: {len(route)} nodes, "
            f"{unvisited_count} unvisited / {total_edges} total edges"
        )
        stats_text.set_text(
            f"visited: {visited_count}/{total_edges} ({pct:.1f}%)  |  "
            f"press any key → next step | q → quit"
        )

        fig.canvas.draw_idle()

    def on_key(event):
        if event.key == "q" or event.key == "escape":
            plt.close(fig)
            return
        step_index[0] = (step_index[0] + 1) % total
        draw(step_index[0])

    fig.canvas.mpl_connect("key_press_event", on_key)

    draw(0)

    # Legend
    from matplotlib.lines import Line2D

    legend_elements = [
        Line2D([0], [0], color="#2ECC40", linewidth=3, label="Route (greedy)"),
        Line2D(
            [0],
            [0],
            color="#FF4136",
            linewidth=3,
            linestyle="dashed",
            label="Deadhead (recovery)",
        ),
        Line2D(
            [0], [0], color="#4A90D9", linewidth=2.5, alpha=0.5, label="Visited edges"
        ),
        Line2D([0], [0], color="orange", linewidth=0.6, label="Unvisited edges"),
        Line2D([0], [0], color="lightgray", linewidth=0.3, label="Graph background"),
    ]
    ax.legend(handles=legend_elements, loc="upper right", fontsize=9)

    print("Press any key to advance one step. Press 'q' to quit.")
    plt.show()


if __name__ == "__main__":
    main()
