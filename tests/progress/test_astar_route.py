import osmnx as ox

from .routes import Routes, print_coverage
from travel_map.generator.astar import AStarRoute


class TestAStarRoutes(Routes):
    generator_class = AStarRoute
