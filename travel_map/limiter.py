import asyncio
import random
from contextlib import asynccontextmanager

from aiolimiter import AsyncLimiter
from redis.asyncio import Redis

from travel_map.redis import get_redis


class RedisQPSLimiter:
    def __init__(self, redis: Redis, key: str, interval_ms: int = 1000):
        self.redis = redis
        self.key = key
        self.interval_ms = interval_ms
        self._local_fallback = AsyncLimiter(1, interval_ms / 1000)

    @asynccontextmanager
    async def slot(self):
        acquired_via_redis = await self._try_acquire_redis()
        if acquired_via_redis:
            try:
                yield
            finally:
                pass
        else:
            async with self._local_fallback:
                yield

    async def _try_acquire_redis(self) -> bool:
        try:
            while True:
                ok = await self.redis.set(self.key, "1", nx=True, px=self.interval_ms)
                if ok:
                    return True
                pttl = await self.redis.pttl(self.key)
                delay = (pttl / 1000.0) if pttl and pttl > 0 else 0.05
                await asyncio.sleep(delay + random.uniform(0, 0.05))
        except Exception:
            return False


NOMINATIM_LIMITER = RedisQPSLimiter(
    get_redis(), key="rl:nominatim:qps1", interval_ms=500
)
