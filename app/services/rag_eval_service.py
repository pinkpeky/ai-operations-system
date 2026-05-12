"""RAG Eval Service 模块。"""

import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.errors import AppError
from app.models.rag_eval import RAGEvalItem, RAGEvalRun
from app.repositories.collection_repository import CollectionRepository
from app.repositories.rag_eval_repository import RAGEvalRepository
from app.schemas.rag_eval import RAGEvalItemCreateRequest, RAGEvalRunCreateRequest, RAGEvalScoreUpdateRequest

logger = logging.getLogger(__name__)


class RAGEvalService:
    """RAG Eval 业务服务。"""

    def __init__(
        self,
        *,
        session: AsyncSession,
        settings: Settings,
        repository: RAGEvalRepository | None = None,
        collection_repository: CollectionRepository | None = None,
    ) -> None:
        self.session = session
        self.settings = settings
        self.repository = repository or RAGEvalRepository(session)
        self.collection_repository = collection_repository or CollectionRepository(session)

    async def create_run(self, *, workspace_id: str, request: RAGEvalRunCreateRequest) -> RAGEvalRun:
        """创建评估运行，并记录当前 embedding/LLM 配置。"""

        collection = await self.collection_repository.get_by_name(
            request.collection_name,
            workspace_id=workspace_id,
        )
        embedding_provider = collection.embedding_provider if collection else self.settings.embedding_provider
        embedding_model = collection.embedding_model_name if collection else self._get_embedding_model_name()
        llm_provider = self.settings.llm_provider
        llm_model = self._get_llm_model_name()
        reranker_provider = self.settings.reranker_provider
        reranker_model = self._get_reranker_model_name()
        return await self.repository.create_run(
            workspace_id=workspace_id,
            name=request.name,
            description=request.description,
            collection_name=request.collection_name,
            embedding_provider=embedding_provider,
            embedding_model_name=embedding_model,
            llm_provider=llm_provider,
            llm_model=llm_model,
            reranker_provider=reranker_provider,
            reranker_model=reranker_model,
        )

    async def list_runs(self, *, workspace_id: str, limit: int = 100) -> list[RAGEvalRun]:
        """查询当前 workspace 的评估运行。"""

        return await self.repository.list_runs(workspace_id=workspace_id, limit=limit)

    async def create_item(self, *, workspace_id: str, run_id: UUID, request: RAGEvalItemCreateRequest) -> RAGEvalItem:
        """创建评估条目。"""

        run = await self.repository.get_run(run_id=run_id, workspace_id=workspace_id)
        if run is None:
            raise AppError("RAG eval run not found in workspace", status_code=404)
        return await self.repository.create_item(
            run_id=run.id,
            query=request.query,
            expected_answer=request.expected_answer,
            retrieved_chunks=request.retrieved_chunks,
            final_prompt=request.final_prompt,
            final_answer=request.final_answer,
            similarity_scores=request.similarity_scores,
            eval_mode=request.eval_mode,
            reranker_provider=request.reranker_provider,
            reranker_model=request.reranker_model,
            reranked_chunks=request.reranked_chunks,
            rerank_scores=request.rerank_scores,
            retrieval_before_rerank=request.retrieval_before_rerank,
            retrieval_after_rerank=request.retrieval_after_rerank,
            latency_ms=request.latency_ms,
            notes=request.notes,
        )

    async def list_items(self, *, workspace_id: str, run_id: UUID) -> list[RAGEvalItem]:
        """查询评估条目。"""

        run = await self.repository.get_run(run_id=run_id, workspace_id=workspace_id)
        if run is None:
            raise AppError("RAG eval run not found in workspace", status_code=404)
        return await self.repository.list_items(run_id=run.id)

    async def update_score(self, *, workspace_id: str, item_id: UUID, request: RAGEvalScoreUpdateRequest) -> RAGEvalItem:
        """更新人工评分。"""

        item = await self.repository.get_item_in_workspace(item_id=item_id, workspace_id=workspace_id)
        if item is None:
            raise AppError("RAG eval item not found in workspace", status_code=404)
        return await self.repository.update_item_score(
            item=item,
            manual_score=request.manual_score,
            notes=request.notes,
        )

    def _get_embedding_model_name(self) -> str:
        """根据配置返回 embedding 模型名。"""

        if self.settings.embedding_provider == "local":
            return self.settings.local_embedding_model
        return "mock-embedding-model"

    def _get_llm_model_name(self) -> str:
        """根据配置返回 LLM 模型名。"""

        if self.settings.llm_provider == "local":
            return self.settings.local_llm_model
        if self.settings.llm_provider == "server":
            return self.settings.server_llm_model
        return "mock-llm"

    def _get_reranker_model_name(self) -> str:
        """根据配置返回 Reranker 模型名称。"""

        if self.settings.reranker_provider == "local":
            return self.settings.local_reranker_model
        return "mock-reranker"
