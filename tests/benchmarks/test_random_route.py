from tests.benchmarks.benchmark import Benchamarks
from travel_map.generator.random_route import RandomRoute


class TestRandomRoute(Benchamarks):
    generator_class = RandomRoute
