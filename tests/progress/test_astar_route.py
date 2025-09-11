from travel_map.generator.astar import AStarRoute

from .routes import Routes


class TestAStarRoutes(Routes):
    generator_class = AStarRoute
