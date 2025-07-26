from tests.generator.routes import Routes
from travel_map.generator.random import RandomRoute


class TestRandomRoutes(Routes):
    generator_class = RandomRoute
