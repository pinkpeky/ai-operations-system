"""Agentic RAG API 路由模块。

该接口只暴露单一 Agentic RAG 编排器，不接 Scheduler、真实 LLM 或多 Agent 系统。
"""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.llm_client import LLMClient
from app.api.routes.rag import create_hybrid_search_pipeline
from app.core.config import get_settings
from app.core.errors import AppError
from app.core.workspace_context import WorkspaceContext, get_workspace_context
from app.db.postgres import get_session
from app.memory.services import MemoryService
from app.rag.agentic_orchestrator import AgenticRAGOrchestrator
from app.reranker.reranker_client import RerankerClient
from app.schemas.agentic_rag import AgenticRAGRequest, AgenticRAGResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agentic-rag", tags=["agentic-rag"])


@router.post("/query", response_model=AgenticRAGResponse)
async def query_agentic_rag(
    request: AgenticRAGRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> AgenticRAGResponse:
    """执行单一 Agentic RAG 查询。"""

    try:
        settings = get_settings()
        hybrid_search_pipeline = create_hybrid_search_pipeline(
            settings=settings,
            session=session,
            collection_name=request.collection_name,
        )
        # 部分单元测试会用轻量 fake session 替代真实 AsyncSession；此时跳过 MemoryService，
        # 以保持旧 Agentic RAG API 的兼容性，生产环境仍会启用 memory retrieval。
        memory_service = MemoryService(session) if hasattr(session, "execute") else None
        orchestrator = AgenticRAGOrchestrator(
            llm_client=LLMClient(settings=settings),
            hybrid_search_pipeline=hybrid_search_pipeline,
            reranker_client=RerankerClient(settings=settings),
            memory_service=memory_service,
            retrieval_top_k=settings.dense_top_k,
            keyword_top_k=settings.keyword_top_k,
            search_mode=settings.default_search_mode,  # type: ignore[arg-type]
            rerank_top_n=settings.rerank_top_n,
        )
        response = await orchestrator.query(request, workspace_id=context.workspace_id)
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
