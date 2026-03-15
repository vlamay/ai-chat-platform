"""
Cache configuration and utilities for Redis caching
"""
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


async def init_cache():
    """Initialize Redis cache backend - with lazy imports to avoid import errors"""
    try:
        # Lazy imports - only import if we actually need them
        from fastapi_cache import FastAPICache
        from fastapi_cache.backends.redis import RedisBackend
        from redis import asyncio as aioredis

        redis = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf8",
            decode_responses=True,
        )
        FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
        logger.info("✓ Redis cache initialized successfully")
        return redis
    except ImportError as e:
        logger.warning(f"Redis client not installed: {e}")
        logger.warning("Caching disabled - install redis-py to enable")
        return None
    except Exception as e:
        logger.warning(f"Failed to initialize Redis cache: {e}")
        logger.warning("Caching disabled - check Redis connection and configuration")
        return None
