"""RAG Eval Repository 模块。"""

import logging
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rag_eval import RAGEvalItem, RAGEvalRun

logger = logging.getLogger(__name__)


class RAGEvalRepository:
    """RAG Eval 数据访问层。"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_run(
        self,
        *,
        workspace_id: str,
        name: str,
        description: str | None,
        collection_name: str,
        embedding_provider: str,
        embedding_model_name: str,
        llm_provider: str,
        llm_model: str,
        reranker_provider: str | None = None,
        reranker_model: str | None = None,
    ) -> RAGEvalRun:
        """创建评估运行。"""

        run = RAGEvalRun(
            workspace_id=workspace_id,
            name=name,
            description=description,
            collection_name=collection_name,
            embedding_provider=embedding_provider,
            embedding_model_name=embedding_model_name,
            llm_provider=llm_provider,
            llm_model=llm_model,
            reranker_provider=reranker_provider,
            reranker_model=reranker_model,
        )
        self.session.add(run)
        await self.session.commit()
        await self.session.refresh(run)
        logger.info("RAG eval run created", extra={"run_id": str(run.id), "workspace_id": workspace_id})
        return run

    async def list_runs(self, *, workspace_id: str, limit: int = 100) -> list[RAGEvalRun]:
        """查询当前 workspace 的评估运行。"""

        statement = (
            select(RAGEvalRun)
            .where(RAGEvalRun.workspace_id == workspace_id)
            .order_by(RAGEvalRun.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def get_run(self, *, run_id: UUID, workspace_id: str) -> RAGEvalRun | None:
        """按 ID 和 workspace 查询评估运行。"""

        statement = select(RAGEvalRun).where(RAGEvalRun.id == run_id, RAGEvalRun.workspace_id == workspace_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def create_item(
        self,
        *,
        run_id: UUID,
        query: str,
        expected_answer: str | None,
        retrieved_chunks: list[dict[str, Any]],
        final_prompt: str | None,
        final_answer: str | None,
        similarity_scores: list[float],
        eval_mode: str = "retrieval_rerank",
        reranker_provider: str | None = None,
        reranker_model: str | None = None,
        reranked_chunks: list[dict[str, Any]] | None = None,
        rerank_scores: list[float] | None = None,
        retrieval_before_rerank: list[dict[str, Any]] | None = None,
        retrieval_after_rerank: list[dict[str, Any]] | None = None,
        latency_ms: int | None = None,
        notes: str | None = None,
    ) -> RAGEvalItem:
        """创建评估条目。"""

        item = RAGEvalItem(
            run_id=run_id,
            query=query,
            expected_answer=expected_answer,
            retrieved_chunks=retrieved_chunks,
            final_prompt=final_prompt,
            final_answer=final_answer,
            similarity_scores=similarity_scores,
            eval_mode=eval_mode,
            reranker_provider=reranker_provider,
            reranker_model=reranker_model,
            reranked_chunks=reranked_chunks or [],
            rerank_scores=rerank_scores or [],
            retrieval_before_rerank=retrieval_before_rerank or [],
            retrieval_after_rerank=retrieval_after_rerank or [],
            latency_ms=latency_ms,
            notes=notes,
        )
        self.session.add(item)
        await self.session.commit()
        await self.session.refresh(item)
        logger.info("RAG eval item created", extra={"item_id": str(item.id), "run_id": str(run_id)})
        return item

    async def list_items(self, *, run_id: UUID) -> list[RAGEvalItem]:
        """查询评估运行下的条目。"""

        statement = (
            select(RAGEvalItem)
            .where(RAGEvalItem.run_id == run_id)
            .order_by(RAGEvalItem.created_at.asc())
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def get_item_in_workspace(self, *, item_id: UUID, workspace_id: str) -> RAGEvalItem | None:
        """按 item_id 和 workspace 查询条目。"""

        statement = (
            select(RAGEvalItem)
            .join(RAGEvalRun, RAGEvalRun.id == RAGEvalItem.run_id)
            .where(RAGEvalItem.id == item_id, RAGEvalRun.workspace_id == workspace_id)
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def update_item_score(self, *, item: RAGEvalItem, manual_score: float, notes: str | None) -> RAGEvalItem:
        """更新人工评分。"""

        item.manual_score = manual_score
        item.notes = notes
        await self.session.commit()
        await self.session.refresh(item)
        logger.info("RAG eval item score updated", extra={"item_id": str(item.id), "manual_score": manual_score})
        return item
