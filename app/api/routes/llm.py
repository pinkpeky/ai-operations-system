"""LLM 测试 API 路由模块。

该接口只用于验证 Phase 2.5 的 LLM Client Layer，不承担任务调度或队列消费职责。
"""

import logging

from fastapi import APIRouter

from app.agents.llm_client import LLMClient
from app.core.errors import AppError
from app.schemas.llm import LLMHealthResponse, LLMRequest, LLMResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/llm", tags=["llm"])


@router.get("/health", response_model=LLMHealthResponse)
async def llm_health() -> LLMHealthResponse:
    """检查当前 LLM Provider 是否可用。"""

    try:
        client = LLMClient()
        return await client.health_check()
    except Exception as exc:
        logger.exception("LLM health API failed")
        raise AppError(str(exc) or "LLM health check failed", status_code=500) from exc


@router.post("/test", response_model=LLMResponse)
async def test_llm(request: LLMRequest) -> LLMResponse:
    """测试 LLM Client Layer。"""

    try:
        client = LLMClient()
        response = await client.generate(request)
        logger.info(
            "LLM test API completed",
            extra={"provider": response.provider, "model": response.model},
        )
        return response
    except ValueError as exc:
        logger.warning("LLM test API received invalid request", extra={"error": str(exc)})
        raise AppError(str(exc), status_code=400) from exc
    except Exception as exc:
        logger.exception("LLM test API failed")
        raise AppError(str(exc) or "LLM test failed", status_code=500) from exc
