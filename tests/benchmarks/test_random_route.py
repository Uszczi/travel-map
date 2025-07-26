from tests.benchmarks.benchmark import Benchamarks

from travel_map.generator.random import RandomRoute


class TestRandomRoute(Benchamarks):
    generator_class = RandomRoute
