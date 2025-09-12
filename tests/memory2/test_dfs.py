from travel_map.generator.dfs import DfsRoute

from .base import Routes


class TestDFSRoutes(Routes):
    generator_class = DfsRoute
