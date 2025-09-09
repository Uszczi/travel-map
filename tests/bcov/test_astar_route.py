from travel_map.generator.astar import AStarRoute

from .base import Routes


class TestAStarRoutes(Routes):
    NUMBER_OF_ROUTES = 100
    generator_class = AStarRoute
