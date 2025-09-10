# pip install osmnx matplotlib
import matplotlib.pyplot as plt
import osmnx as ox
from shapely.geometry import LineString

# Twój graf
from travel_map.api.common import get_or_create_graph

P = (1177493762, 1177493777)  # "Środek Piotrkowskiej"
L = (1177493766, 1177493886)  # "Odnoga na początku Lubelskiej"
W = (2131056242, 2131056249)  # "Wysoka"

SELECTED = [
    ("Piotrkowska", P),
    ("Lubelska", L),
    ("Wysoka", W),
]

G = get_or_create_graph()


def edges_between_with_geom(G, u, v):
    found = []
    # u -> v
    data_uv = G.get_edge_data(u, v, default=None)
    if data_uv:
        for k, data in data_uv.items():
            geom = data.get("geometry")
            if geom is None:
                x1, y1 = G.nodes[u]["x"], G.nodes[u]["y"]
                x2, y2 = G.nodes[v]["x"], G.nodes[v]["y"]
                geom = LineString([(x1, y1), (x2, y2)])
            found.append((u, v, k, geom, data))
    # v -> u (drugi kierunek jeśli istnieje)
    data_vu = G.get_edge_data(v, u, default=None)
    if data_vu:
        for k, data in data_vu.items():
            geom = data.get("geometry")
            if geom is None:
                x1, y1 = G.nodes[v]["x"], G.nodes[v]["y"]
                x2, y2 = G.nodes[u]["x"], G.nodes[u]["y"]
                geom = LineString([(x1, y1), (x2, y2)])
            found.append((v, u, k, geom, data))
    return found


fig, ax = ox.plot_graph(
    G,
    node_size=0,
    # edge_color="#9aa",
    edge_linewidth=0.7,
    show=False,
    close=False,
    # bgcolor="white",
)

color_for = {
    "Piotrkowska": "tab:red",
    "Lubelska": "tab:red",
    "Wysoka": "tab:red",
}

highlight_handles = []
for name, (u, v) in SELECTED:
    edges = edges_between_with_geom(G, u, v)

    for uu, vv, k, geom, data in edges:
        xs, ys = geom.xy
        (h,) = ax.plot(
            xs, ys, linewidth=3.0, alpha=0.95, color=color_for[name], label=name
        )

plt.show()
