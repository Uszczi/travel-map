
from .routes import Routes
from travel_map.generator.astar import AStarRoute


class TestAStarRoutes(Routes):
    generator_class = AStarRoute
