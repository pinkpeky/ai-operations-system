"""Redis 连接管理模块。

该模块负责初始化、健康检查和关闭 Redis 异步客户端。
"""

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
        # Redis 客户端使用 decode_responses，业务层可直接处理字符串。
        redis_client = Redis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=None,
        )
        # 等待 Redis 完成启动，避免 API 容器抢跑导致启动失败。
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
        # ping 是 Redis 官方推荐的基础连通性检查。
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
            # 显式关闭连接，保证应用退出时资源释放完整。
            await redis_client.aclose()
            logger.info("Redis connection closed")
    except Exception as exc:
        logger.exception("Failed to close Redis connection")
        raise RuntimeError("Redis shutdown failed") from exc
    finally:
        redis_client = None


def get_redis_client() -> Redis:
    """获取全局 Redis 客户端，供队列和业务模块复用。"""

    try:
        if redis_client is None:
            raise RuntimeError("Redis client is not initialized")
        return redis_client
    except Exception as exc:
        logger.exception("Failed to get Redis client")
        raise RuntimeError("Redis client is unavailable") from exc
