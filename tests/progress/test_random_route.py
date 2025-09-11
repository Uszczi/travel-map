from .routes import Routes
from travel_map.generator.random_route import RandomRoute


class TestRandomRoutes(Routes):
    generator_class = RandomRoute
