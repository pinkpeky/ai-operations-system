"""Mock Reranker Provider 模块。

当前阶段不接真实 reranker 模型，使用 query/token overlap 做稳定、可测试的精排。
"""

import logging
import math
import re

from app.rag.vector_store import VectorSearchResult
from app.reranker.providers.base import BaseRerankerProvider, RerankedChunk

logger = logging.getLogger(__name__)


class MockRerankerProvider(BaseRerankerProvider):
    """基于 token overlap 的 Mock Reranker。"""

    provider_name = "mock"

    def __init__(self, model: str = "mock-reranker") -> None:
        super().__init__(model=model, enabled=True)

    async def rerank(
        self,
        *,
        query: str,
        chunks: list[VectorSearchResult],
        top_n: int,
    ) -> list[RerankedChunk]:
        """按 query 与 chunk 文本 token 重叠度稳定排序。"""

        if top_n <= 0:
            raise ValueError("top_n must be positive")
        query_tokens = self._tokenize(query)
        scored_chunks = [self._score_chunk(query_tokens, chunk) for chunk in chunks]
        scored_chunks.sort(
            key=lambda item: (
                item.rerank_score,
                item.similarity_score,
                -1 * (item.chunk_index if item.chunk_index is not None else 0),
                item.id,
            ),
            reverse=True,
        )
        results = scored_chunks[:top_n]
        logger.info(
            "Mock reranker completed",
            extra={"candidate_count": len(chunks), "returned_count": len(results), "top_n": top_n},
        )
        return results

    def _score_chunk(self, query_tokens: set[str], chunk: VectorSearchResult) -> RerankedChunk:
        """计算单个 chunk 的 mock rerank 分数。"""

        chunk_tokens = self._tokenize(chunk.text)
        if not query_tokens or not chunk_tokens:
            overlap_score = 0.0
        else:
            overlap = len(query_tokens & chunk_tokens)
            overlap_score = overlap / math.sqrt(len(query_tokens) * len(chunk_tokens))
        # 让 rerank 以文本相关性为主，同时保留原始向量召回分数作为稳定 tie-break 信号。
        rerank_score = round(max(0.0, min(1.0, overlap_score * 0.8 + chunk.similarity_score * 0.2)), 6)
        return RerankedChunk(
            id=chunk.id,
            text=chunk.text,
            similarity_score=chunk.similarity_score,
            raw_score=chunk.raw_score,
            rerank_score=rerank_score,
            metadata=chunk.metadata,
            chunk_index=chunk.chunk_index,
            dense_score=chunk.dense_score,
            keyword_score=chunk.keyword_score,
            hybrid_score=chunk.hybrid_score,
        )

    def _tokenize(self, text: str) -> set[str]:
        """切分中英文 token，保证中文查询也能产生稳定 overlap。"""

        lowered = text.lower()
        latin_tokens = re.findall(r"[a-z0-9_]+", lowered)
        cjk_tokens = re.findall(r"[\u4e00-\u9fff]", lowered)
        return {token for token in [*latin_tokens, *cjk_tokens] if token}
