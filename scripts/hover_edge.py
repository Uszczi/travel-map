import osmnx as ox
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from travel_map.api.common import get_or_create_graph


def infer_mode_from_highway(hw):
    if isinstance(hw, list) and hw:
        hw = hw[0]
    if not isinstance(hw, str):
        return "unknown"
    road = {
        "motorway",
        "trunk",
        "primary",
        "secondary",
        "tertiary",
        "residential",
        "service",
        "unclassified",
    }
    bike = {"cycleway"}
    foot = {"footway", "path", "pedestrian", "steps", "living_street", "sidewalk"}
    if hw in road:
        return "car"
    if hw in bike:
        return "bike"
    if hw in foot:
        return "foot"
    return "unknown"


def build_edge_segments(G):
    segments = []
    edge_info = []

    for u, v, k, data in G.edges(keys=True, data=True):
        if "mode" not in data:
            data["mode"] = infer_mode_from_highway(data.get("highway"))

        if "geometry" in data and data["geometry"] is not None:
            coords = list(data["geometry"].coords)
        else:
            x1, y1 = G.nodes[u]["x"], G.nodes[u]["y"]
            x2, y2 = G.nodes[v]["x"], G.nodes[v]["y"]
            coords = [(x1, y1), (x2, y2)]

        segments.append(coords)
        edge_info.append(
            {
                "u": u,
                "v": v,
                "k": k,
                "mode": data.get("mode", "unknown"),
                "highway": data.get("highway"),
                "name": data.get("name"),
            }
        )

    return segments, edge_info


def plot_graph_with_hover(G, figsize=(10, 10), pickradius=5):
    segments, edge_info = build_edge_segments(G)

    fig, ax = plt.subplots(figsize=figsize)
    lc = LineCollection(segments, linewidths=0.7, alpha=0.9)
    ax.add_collection(lc)
    ax.autoscale()
    ax.set_aspect("equal", adjustable="datalim")
    ax.axis("off")

    lc.set_picker(True)
    lc.set_pickradius(pickradius)

    annot = ax.annotate(
        "",
        xy=(0, 0),
        xytext=(10, 10),
        textcoords="offset points",
        bbox=dict(boxstyle="round", fc="w"),
        arrowprops=dict(arrowstyle="->"),
    )
    annot.set_visible(False)

    hovered_idx = {"ind": None}

    def show_annot(i, event):
        info = edge_info[i]
        annot.xy = (event.xdata, event.ydata)
        text = f"{info["u"]=} {info["v"]=}"
        print(text)

        annot.set_text(text)
        annot.set_visible(True)

    def on_move(event):
        if event.inaxes is not ax or event.xdata is None or event.ydata is None:
            if annot.get_visible():
                annot.set_visible(False)
                fig.canvas.draw_idle()
            return

        hit, details = lc.contains(event)
        if hit and "ind" in details and any(details["ind"]):
            i = details["ind"][0]
            if hovered_idx["ind"] != i:
                hovered_idx["ind"] = i
                show_annot(i, event)
                fig.canvas.draw_idle()
        else:
            if annot.get_visible():
                annot.set_visible(False)
                hovered_idx["ind"] = None
                fig.canvas.draw_idle()

    fig.canvas.mpl_connect("motion_notify_event", on_move)
    return fig, ax



G = get_or_create_graph()
fig, ax = plot_graph_with_hover(G)
plt.show()
