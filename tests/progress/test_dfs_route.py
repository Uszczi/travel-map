from travel_map.generator.dfs import DfsRoute

from .routes import Routes


class TestDFSRoutes(Routes):
    generator_class = DfsRoute
