from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

from travel_map.api import include_routers, init_sentry, setup_middlewares
from travel_map.extensions.prometheus import include_prometheus
from travel_map.settings import settings


# TODO move this
@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    redis = aioredis.from_url(settings.REDIS_URL)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield


init_sentry()

app = FastAPI(lifespan=lifespan, root_path=settings.URL_PREFIX)

setup_middlewares(app)

include_routers(app)

include_prometheus(app)
