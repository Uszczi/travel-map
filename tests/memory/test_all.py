from travel_map.generator.astar import AStarRoute
from travel_map.generator.random_route import RandomRoute
from travel_map.generator.dfs import DfsRoute

from .base import Routes


class TestAStarRoutes(Routes):
    generator_class_1 = AStarRoute
    generator_class_2 = DfsRoute
    generator_class_3 = RandomRoute
