"""API 路由聚合模块。

该模块集中挂载所有版本化 API 路由，当前 Phase 1 先提供健康检查能力。
"""

import logging

from fastapi import APIRouter

from app.api.routes.agentic_rag import router as agentic_rag_router
from app.api.routes.agents import router as agents_router
from app.api.routes.health import router as health_router
from app.api.routes.llm import router as llm_router
from app.api.routes.rag import router as rag_router
from app.api.routes.tasks import router as tasks_router

logger = logging.getLogger(__name__)


def create_api_router() -> APIRouter:
    try:
        # 统一使用 /api/v1 前缀，为后续接口版本演进预留空间。
        router = APIRouter(prefix="/api/v1")
        router.include_router(agentic_rag_router)
        router.include_router(agents_router)
        router.include_router(health_router)
        router.include_router(llm_router)
        router.include_router(rag_router)
        router.include_router(tasks_router)
        logger.info("API router configured")
        return router
    except Exception as exc:
        logger.exception("Failed to configure API router")
        raise RuntimeError("API router configuration failed") from exc
