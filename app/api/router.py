"""API 路由聚合模块。

该模块集中挂载所有版本化 API 路由，当前 Phase 1 先提供健康检查能力。
"""

import logging

from fastapi import APIRouter

from app.api.routes.health import router as health_router

logger = logging.getLogger(__name__)


def create_api_router() -> APIRouter:
    try:
        # 统一使用 /api/v1 前缀，为后续接口版本演进预留空间。
        router = APIRouter(prefix="/api/v1")
        router.include_router(health_router)
        logger.info("API router configured")
        return router
    except Exception as exc:
        logger.exception("Failed to configure API router")
        raise RuntimeError("API router configuration failed") from exc
