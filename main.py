from fastapi import FastAPI, Request
import time

import matplotlib.pyplot as plt
import osmnx as ox
from loguru import logger
from travel_map.db import mongo_db

from fastapi.middleware.cors import CORSMiddleware

from travel_map import utils
from travel_map.generator.dfs import DfsRoute
from travel_map.generator.random import RandomRoute
from travel_map.models import Route, StravaRoute
from travel_map.visited_edges import (
    get_visited_segments,
    mark_edges_visited,
    strava_route_to_route,
    visited_edges,
)

start_x: float = 19.1999532
start_y: float = 51.6101241
CITY_BBOX_DEFAULT_SIZE = 0.04
CITY_BBOX = (
    start_x - CITY_BBOX_DEFAULT_SIZE * 2,
    start_y - CITY_BBOX_DEFAULT_SIZE,
    start_x + CITY_BBOX_DEFAULT_SIZE * 2,
    start_y + CITY_BBOX_DEFAULT_SIZE,
)
G = ox.graph_from_bbox(CITY_BBOX, network_type="drive")

fig, ax = ox.plot_graph(G, show=False)

node_to_highlight = 2470903748


for a in [
    9354082715,
    1790548836,
    9354082714,
    1790548809,
    5312455454,
    1790548807,
    1452823560,
    2131056248,
    2131056247,
    1177493746,
    2131056249,
    1177493813,
    1177493766,
    1177493568,
    1651708412,
    1177493871,
    34087415,
    1177493869,
    1177493739,
    1177493717,
    1177493623,
    34227978,
    904195694,
    538482301,
    538482298,
    9418309742,
    1452823527,
    1452823524,
    1792903423,
    1156800504,
    6513065442,
]:
    # Zaznaczenie konkretnego wierzchołka na wykresie
    highlight_x = G.nodes[a]["x"]
    highlight_y = G.nodes[a]["y"]
    ax.scatter(
        highlight_x,
        highlight_y,
        color="red",
        s=100,  # Rozmiar zaznaczonego wierzchołka
        zorder=5,  # Umieść na wierzchu
        label="Highlighted Node",
    )

plt.show()
