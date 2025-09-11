from tests.generator.routes import Routes
from travel_map.generator.dfs import DfsRoute


class TestDFSRoutes(Routes):
    generator_class = DfsRoute
