"""Agentic RAG 任务 Handler 模块。

该 Handler 接收 agentic_rag_query 任务 payload，调用单一 AgenticRAGOrchestrator 并返回标准执行结果。
"""

import logging
from collections.abc import Callable
from inspect import signature
from typing import Any

from app.agents.llm_client import LLMClient
from app.core.config import Settings, get_settings
from app.rag.agentic_orchestrator import AgenticRAGOrchestrator
from app.rag.embedding_client import EmbeddingClient
from app.rag.retrieval import RetrievalPipeline
from app.rag.vector_store import QdrantVectorStore
from app.schemas.agentic_rag import AgenticRAGRequest
from app.workers.handlers.base import BaseTaskHandler, TaskExecutionResult

logger = logging.getLogger(__name__)

AGENTIC_RAG_TASK_TYPE = "agentic_rag_query"
OrchestratorFactory = Callable[[AgenticRAGRequest], AgenticRAGOrchestrator]


class AgenticRAGHandler(BaseTaskHandler):
    """Agentic RAG 查询任务 Handler。"""

    task_type = AGENTIC_RAG_TASK_TYPE

    def __init__(
        self,
        settings: Settings | None = None,
        orchestrator_factory: OrchestratorFactory | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.orchestrator_factory = orchestrator_factory or self._create_orchestrator

    async def handle(self, payload: dict[str, Any]) -> TaskExecutionResult:
        """执行 agentic_rag_query 任务。"""

        try:
            request = AgenticRAGRequest.model_validate(payload)
            orchestrator = self.orchestrator_factory(request)
            workspace_id = payload.get("workspace_id")
            task_id = payload.get("task_id")
            response = await self._query_orchestrator(
                orchestrator=orchestrator,
                request=request,
                workspace_id=str(workspace_id) if workspace_id is not None else None,
                task_id=str(task_id) if task_id is not None else None,
            )
            logger.info(
                "Agentic RAG task handled",
                extra={
                    "collection": request.collection_name,
                    "used_retrieval": response.used_retrieval,
                    "provider": response.provider,
                    "model": response.model,
                    "latency_ms": response.debug.latency_ms if response.debug is not None else None,
                    "error": None,
                    "workspace_id": workspace_id,
                    "task_id": task_id,
                },
            )
            return TaskExecutionResult(
                success=True,
                data=response.model_dump(),
            )
        except Exception as exc:
            logger.exception(
                "Agentic RAG task handler failed",
                extra={"workspace_id": payload.get("workspace_id"), "task_id": payload.get("task_id"), "error": str(exc)},
            )
            return TaskExecutionResult(success=False, error=str(exc))

    def _create_orchestrator(self, request: AgenticRAGRequest) -> AgenticRAGOrchestrator:
        """按任务请求创建 Agentic RAG 编排器。"""

        embedding_client = EmbeddingClient(settings=self.settings)
        vector_store = QdrantVectorStore(
            collection_name=request.collection_name or self.settings.qdrant_collection_name,
            embedding_dimension=self.settings.embedding_dimension,
            allow_collection_delete=self.settings.app_env == "test",
        )
        retrieval_pipeline = RetrievalPipeline(
            embedding_client=embedding_client,
            vector_store=vector_store,
        )
        return AgenticRAGOrchestrator(
            llm_client=LLMClient(settings=self.settings),
            retrieval_pipeline=retrieval_pipeline,
        )

    async def _query_orchestrator(
        self,
        *,
        orchestrator: AgenticRAGOrchestrator,
        request: AgenticRAGRequest,
        workspace_id: str | None,
        task_id: str | None,
    ):
        """兼容旧测试替身和真实 orchestrator 的 query 签名。"""

        parameters = signature(orchestrator.query).parameters
        kwargs: dict[str, str | None] = {}
        if "workspace_id" in parameters:
            kwargs["workspace_id"] = workspace_id
        if "task_id" in parameters:
            kwargs["task_id"] = task_id
        return await orchestrator.query(request, **kwargs)
