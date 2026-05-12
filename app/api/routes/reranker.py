"""Reranker API 路由模块。"""

import logging

from fastapi import APIRouter

from app.core.errors import AppError
from app.reranker.reranker_client import RerankerClient
from app.schemas.reranker import RerankerHealthResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reranker", tags=["reranker"])


@router.get("/health", response_model=RerankerHealthResponse)
async def reranker_health() -> RerankerHealthResponse:
    """检查当前 Reranker Provider 是否可用。"""

    try:
        client = RerankerClient()
        return await client.health_check()
    except Exception as exc:
        logger.exception("Reranker health API failed")
        raise AppError(str(exc) or "Reranker health check failed", status_code=500) from exc
