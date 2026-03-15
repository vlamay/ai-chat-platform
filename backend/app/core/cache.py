"""
Cache configuration and utilities for Redis caching
"""
import logging
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from app.core.config import settings

logger = logging.getLogger(__name__)


async def init_cache():
    """Initialize Redis cache backend"""
    try:
        redis = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf8",
            decode_responses=True,
        )
        FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
        logger.info("✓ Redis cache initialized successfully")
        return redis
    except Exception as e:
        logger.warning(f"Failed to initialize Redis cache: {e}")
        logger.warning("Caching disabled - install Redis and set REDIS_URL to enable")
        return None
