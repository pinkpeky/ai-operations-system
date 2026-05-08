import logging
import asyncio
from typing import Optional

from redis.asyncio import Redis

from app.core.config import Settings

logger = logging.getLogger(__name__)

redis_client: Optional[Redis] = None


async def init_redis(settings: Settings) -> None:
    global redis_client

    try:
        redis_client = Redis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
        )
        for attempt in range(1, 11):
            try:
                await check_redis()
                break
            except Exception:
                if attempt == 10:
                    raise
                logger.warning("Redis not ready, retrying", extra={"attempt": attempt})
                await asyncio.sleep(2)
        logger.info("Redis connection initialized")
    except Exception as exc:
        logger.exception("Failed to initialize Redis connection")
        await close_redis()
        raise RuntimeError("Redis initialization failed") from exc


async def check_redis() -> bool:
    try:
        if redis_client is None:
            raise RuntimeError("Redis client is not initialized")
        pong = await redis_client.ping()
        if pong is not True:
            raise RuntimeError("Redis ping did not return PONG")
        logger.debug("Redis health check passed")
        return True
    except Exception as exc:
        logger.exception("Redis health check failed")
        raise RuntimeError("Redis health check failed") from exc


async def close_redis() -> None:
    global redis_client

    try:
        if redis_client is not None:
            await redis_client.aclose()
            logger.info("Redis connection closed")
    except Exception as exc:
        logger.exception("Failed to close Redis connection")
        raise RuntimeError("Redis shutdown failed") from exc
    finally:
        redis_client = None
