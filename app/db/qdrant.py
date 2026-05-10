"""Qdrant 连接管理模块。

该模块负责初始化、健康检查和关闭 Qdrant 异步客户端。
"""

import logging
import asyncio
from typing import Optional

from qdrant_client import AsyncQdrantClient

from app.core.config import Settings

logger = logging.getLogger(__name__)

qdrant_client: Optional[AsyncQdrantClient] = None


async def init_qdrant(settings: Settings) -> None:
    global qdrant_client

    try:
        # Qdrant 客户端统一在启动阶段创建，后续向量服务可直接复用。
        qdrant_client = AsyncQdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
            timeout=10,
        )
        # Qdrant 首次启动需要加载存储目录，增加重试提升 Compose 启动成功率。
        for attempt in range(1, 11):
            try:
                await check_qdrant()
                break
            except Exception:
                if attempt == 10:
                    raise
                logger.warning("Qdrant not ready, retrying", extra={"attempt": attempt})
                await asyncio.sleep(2)
        logger.info("Qdrant connection initialized")
    except Exception as exc:
        logger.exception("Failed to initialize Qdrant connection")
        await close_qdrant()
        raise RuntimeError("Qdrant initialization failed") from exc


async def check_qdrant() -> bool:
    try:
        if qdrant_client is None:
            raise RuntimeError("Qdrant client is not initialized")
        # 拉取 collections 列表用于验证 HTTP API 和鉴权是否正常。
        await qdrant_client.get_collections()
        logger.debug("Qdrant health check passed")
        return True
    except Exception as exc:
        logger.exception("Qdrant health check failed")
        raise RuntimeError("Qdrant health check failed") from exc


async def close_qdrant() -> None:
    global qdrant_client

    try:
        if qdrant_client is not None:
            # 关闭异步客户端，释放底层 HTTP 连接。
            await qdrant_client.close()
            logger.info("Qdrant connection closed")
    except Exception as exc:
        logger.exception("Failed to close Qdrant connection")
        raise RuntimeError("Qdrant shutdown failed") from exc
    finally:
        qdrant_client = None


def get_qdrant_client() -> AsyncQdrantClient:
    """获取全局 Qdrant 客户端，供向量检索层复用。"""

    try:
        if qdrant_client is None:
            raise RuntimeError("Qdrant client is not initialized")
        return qdrant_client
    except Exception as exc:
        logger.exception("Failed to get Qdrant client")
        raise RuntimeError("Qdrant client is unavailable") from exc
