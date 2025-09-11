from travel_map.generator.astar import AStarRoute

from .base import Routes


class TestAStarRoutes(Routes):
    generator_class = AStarRoute
