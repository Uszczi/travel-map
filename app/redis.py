from typing import Optional

from loguru import logger
from redis.asyncio import Redis

from app.settings import settings

_redis_client: Optional[Redis] = None


def get_redis() -> Redis:
    global _redis_client
    if _redis_client is None:
        logger.info("Initializing Redis client at {}", settings.REDIS_URL)
        _redis_client = Redis.from_url(
            settings.REDIS_URL, encoding="utf-8", decode_responses=True
        )
    return _redis_client
