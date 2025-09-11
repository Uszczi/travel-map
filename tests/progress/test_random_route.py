from travel_map.generator.random_route import RandomRoute

from .routes import Routes


class TestRandomRoutes(Routes):
    generator_class = RandomRoute
