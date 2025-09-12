from travel_map.generator.random_route import RandomRoute

from .base import Routes


class TestRandomRoutes(Routes):
    generator_class = RandomRoute
