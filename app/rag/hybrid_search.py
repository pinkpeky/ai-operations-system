"""Hybrid Search 模块。

该模块把 Dense Vector Search 和基于 PostgreSQL document_chunks.text 的
Keyword Search 合并为统一候选集，再交给上层 reranker 精排。
"""

import logging
import re
from dataclasses import dataclass
from typing import Literal

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document, DocumentChunk
from app.models.enums import DocumentStatus
from app.rag.retrieval import RetrievalPipeline
from app.rag.vector_store import VectorSearchResult

logger = logging.getLogger(__name__)

SearchMode = Literal["dense", "keyword", "hybrid"]


@dataclass(frozen=True, slots=True)
class HybridSearchBundle:
    """Hybrid Search 的中间结果，供 API 和 Agentic trace 使用。"""

    search_mode: SearchMode
    dense_results: list[VectorSearchResult]
    keyword_results: list[VectorSearchResult]
    merged_results: list[VectorSearchResult]


class KeywordSearch:
    """基于 PostgreSQL document_chunks.text 的简单关键词检索。"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def search(
        self,
        *,
        query: str,
        collection_name: str,
        top_k: int,
        workspace_id: str,
        source_id: str | None = None,
        status: str = DocumentStatus.ACTIVE.value,
    ) -> list[VectorSearchResult]:
        """执行 ILIKE + 简单关键词评分检索。"""

        if not workspace_id:
            raise ValueError("workspace_id is required for keyword search")
        if top_k <= 0:
            raise ValueError("top_k must be positive")

        tokens = self._tokenize(query)
        if not tokens:
            return []

        statement = (
            select(DocumentChunk, Document)
            .join(Document, Document.id == DocumentChunk.document_id)
            .where(
                DocumentChunk.collection_name == collection_name,
                Document.collection_name == collection_name,
                Document.workspace_id == workspace_id,
                Document.status == status,
                DocumentChunk.status == status,
                or_(*[DocumentChunk.text.ilike(f"%{token}%") for token in tokens]),
            )
            .order_by(DocumentChunk.created_at.desc())
            .limit(max(top_k * 3, top_k))
        )
        if source_id is not None:
            statement = statement.where(Document.source_id == source_id)

        result = await self.session.execute(statement)
        scored_results = [
            self._build_keyword_result(chunk=chunk, document=document, query_tokens=tokens)
            for chunk, document in result.all()
        ]
        scored_results.sort(
            key=lambda item: (
                item.keyword_score or 0.0,
                item.dense_score or 0.0,
                -1 * (item.chunk_index if item.chunk_index is not None else 0),
                item.id,
            ),
            reverse=True,
        )
        final_results = scored_results[:top_k]
        logger.info(
            "Keyword search completed",
            extra={"collection": collection_name, "workspace_id": workspace_id, "count": len(final_results)},
        )
        return final_results

    def _build_keyword_result(
        self,
        *,
        chunk: DocumentChunk,
        document: Document,
        query_tokens: list[str],
    ) -> VectorSearchResult:
        """把数据库 chunk 转为检索结果并计算关键词分数。"""

        keyword_score = self._score_text(chunk.text, query_tokens)
        metadata = dict(chunk.chunk_metadata or {})
        metadata.update(
            {
                "document_id": str(document.id),
                "source_id": document.source_id,
                "version": document.version,
                "workspace_id": document.workspace_id,
                "user_id": document.user_id,
                "status": chunk.status,
                "collection_name": chunk.collection_name,
            }
        )
        metadata["keyword_score"] = keyword_score
        metadata["hybrid_score"] = keyword_score
        return VectorSearchResult(
            id=chunk.qdrant_point_id,
            text=chunk.text,
            similarity_score=keyword_score,
            raw_score=keyword_score,
            metadata=metadata,
            chunk_index=chunk.chunk_index,
            dense_score=None,
            keyword_score=keyword_score,
            hybrid_score=keyword_score,
        )

    def _score_text(self, text: str, query_tokens: list[str]) -> float:
        """计算简单关键词得分，范围 0-1。"""

        lowered_text = text.lower()
        matched = 0
        frequency_bonus = 0.0
        for token in query_tokens:
            count = lowered_text.count(token)
            if count > 0:
                matched += 1
                frequency_bonus += min(count, 3) * 0.03
        base_score = matched / max(len(query_tokens), 1)
        return round(max(0.0, min(1.0, base_score + frequency_bonus)), 6)

    def _tokenize(self, text: str) -> list[str]:
        """切分中英文 token。"""

        lowered = text.lower()
        latin_tokens = re.findall(r"[a-z0-9_]+", lowered)
        cjk_tokens = re.findall(r"[\u4e00-\u9fff]", lowered)
        seen: set[str] = set()
        tokens: list[str] = []
        for token in [*latin_tokens, *cjk_tokens]:
            if token and token not in seen:
                seen.add(token)
                tokens.append(token)
        return tokens


class HybridSearchPipeline:
    """Dense + Keyword + Merge 的检索流水线。"""

    def __init__(self, retrieval_pipeline: RetrievalPipeline, keyword_search: KeywordSearch) -> None:
        self.retrieval_pipeline = retrieval_pipeline
        self.keyword_search = keyword_search

    @property
    def vector_store(self):  # type: ignore[no-untyped-def]
        """暴露底层 vector_store，兼容既有调用方。"""

        return self.retrieval_pipeline.vector_store

    @property
    def embedding_client(self):  # type: ignore[no-untyped-def]
        """暴露底层 embedding_client，供 trace 读取 provider 信息。"""

        return self.retrieval_pipeline.embedding_client

    async def search(
        self,
        *,
        query: str,
        search_mode: SearchMode,
        dense_top_k: int,
        keyword_top_k: int,
        workspace_id: str,
        source_id: str | None = None,
        status: str = DocumentStatus.ACTIVE.value,
    ) -> HybridSearchBundle:
        """执行 dense / keyword / hybrid 检索并合并候选结果。"""

        if search_mode not in {"dense", "keyword", "hybrid"}:
            raise ValueError("search_mode must be dense, keyword, or hybrid")
        if not workspace_id:
            raise ValueError("workspace_id is required for hybrid search")

        dense_results: list[VectorSearchResult] = []
        keyword_results: list[VectorSearchResult] = []

        if search_mode in {"dense", "hybrid"}:
            dense_results = await self.retrieval_pipeline.search(
                query=query,
                top_k=dense_top_k,
                source_id=source_id,
                workspace_id=workspace_id,
                status=status,
            )
        if search_mode in {"keyword", "hybrid"}:
            keyword_results = await self.keyword_search.search(
                query=query,
                collection_name=self.vector_store.collection_name,
                top_k=keyword_top_k,
                workspace_id=workspace_id,
                source_id=source_id,
                status=status,
            )

        merged_results = self.merge_results(dense_results=dense_results, keyword_results=keyword_results)
        logger.info(
            "Hybrid search completed",
            extra={
                "search_mode": search_mode,
                "dense_count": len(dense_results),
                "keyword_count": len(keyword_results),
                "merged_count": len(merged_results),
            },
        )
        return HybridSearchBundle(
            search_mode=search_mode,
            dense_results=dense_results,
            keyword_results=keyword_results,
            merged_results=merged_results,
        )

    def merge_results(
        self,
        *,
        dense_results: list[VectorSearchResult],
        keyword_results: list[VectorSearchResult],
    ) -> list[VectorSearchResult]:
        """合并 dense 和 keyword 结果，按 chunk id 去重并计算 hybrid_score。"""

        merged: dict[str, VectorSearchResult] = {}
        for result in dense_results:
            dense_score = result.dense_score if result.dense_score is not None else result.similarity_score
            metadata = dict(result.metadata)
            metadata["dense_score"] = dense_score
            metadata.setdefault("hybrid_score", dense_score)
            merged[result.id] = VectorSearchResult(
                id=result.id,
                text=result.text,
                similarity_score=result.similarity_score,
                raw_score=result.raw_score,
                metadata=metadata,
                chunk_index=result.chunk_index,
                dense_score=dense_score,
                keyword_score=None,
                hybrid_score=dense_score,
            )

        for result in keyword_results:
            keyword_score = result.keyword_score if result.keyword_score is not None else result.similarity_score
            existing = merged.get(result.id)
            if existing is None:
                metadata = dict(result.metadata)
                metadata["keyword_score"] = keyword_score
                metadata.setdefault("hybrid_score", keyword_score)
                merged[result.id] = VectorSearchResult(
                    id=result.id,
                    text=result.text,
                    similarity_score=keyword_score,
                    raw_score=result.raw_score,
                    metadata=metadata,
                    chunk_index=result.chunk_index,
                    dense_score=None,
                    keyword_score=keyword_score,
                    hybrid_score=keyword_score,
                )
                continue

            dense_score = existing.dense_score or 0.0
            hybrid_score = self._calculate_hybrid_score(dense_score=dense_score, keyword_score=keyword_score)
            metadata = dict(existing.metadata)
            metadata.update(result.metadata)
            metadata["dense_score"] = dense_score
            metadata["keyword_score"] = keyword_score
            metadata["hybrid_score"] = hybrid_score
            merged[result.id] = VectorSearchResult(
                id=existing.id,
                text=existing.text or result.text,
                similarity_score=hybrid_score,
                raw_score=hybrid_score,
                metadata=metadata,
                chunk_index=existing.chunk_index if existing.chunk_index is not None else result.chunk_index,
                dense_score=dense_score,
                keyword_score=keyword_score,
                hybrid_score=hybrid_score,
            )

        results = list(merged.values())
        results.sort(
            key=lambda item: (
                item.hybrid_score or item.similarity_score,
                item.dense_score or 0.0,
                item.keyword_score or 0.0,
                item.id,
            ),
            reverse=True,
        )
        return results

    def _calculate_hybrid_score(self, *, dense_score: float, keyword_score: float) -> float:
        """计算合并分数，dense 与 keyword 都命中时给予轻微融合增益。"""

        score = dense_score * 0.6 + keyword_score * 0.4 + 0.05
        return round(max(0.0, min(1.0, score)), 6)
