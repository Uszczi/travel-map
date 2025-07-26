from tests.benchmarks.benchmark import Benchamarks

from travel_map.generator.dfs import DfsRoute


class TestDFSRoute(Benchamarks):
    generator_class = DfsRoute
