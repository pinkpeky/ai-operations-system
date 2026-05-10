"""Agentic RAG API 路由模块。

该接口只暴露单一 Agentic RAG 编排器，不接 Scheduler、真实 LLM 或多 Agent 系统。
"""

import logging

from fastapi import APIRouter

from app.agents.llm_client import LLMClient
from app.api.routes.rag import create_retrieval_pipeline
from app.core.config import get_settings
from app.core.errors import AppError
from app.rag.agentic_orchestrator import AgenticRAGOrchestrator
from app.schemas.agentic_rag import AgenticRAGRequest, AgenticRAGResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agentic-rag", tags=["agentic-rag"])


@router.post("/query", response_model=AgenticRAGResponse)
async def query_agentic_rag(request: AgenticRAGRequest) -> AgenticRAGResponse:
    """执行单一 Agentic RAG 查询。"""

    try:
        settings = get_settings()
        retrieval_pipeline = create_retrieval_pipeline(
            settings=settings,
            collection_name=request.collection_name,
        )
        orchestrator = AgenticRAGOrchestrator(
            llm_client=LLMClient(settings=settings),
            retrieval_pipeline=retrieval_pipeline,
        )
        response = await orchestrator.query(request)
        logger.info(
            "Agentic RAG API completed",
            extra={
                "used_retrieval": response.used_retrieval,
                "provider": response.provider,
                "model": response.model,
            },
        )
        return response
    except ValueError as exc:
        logger.warning("Agentic RAG API received invalid request", extra={"error": str(exc)})
        raise AppError(str(exc), status_code=400) from exc
    except Exception as exc:
        logger.exception("Agentic RAG API failed")
        raise AppError(str(exc) or "Agentic RAG query failed", status_code=500) from exc
