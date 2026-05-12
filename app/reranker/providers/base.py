"""Reranker Provider 抽象模块。

Provider 层只负责对向量召回结果做精排，不直接访问 Qdrant，也不拼接 Prompt。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ClassVar

from app.rag.vector_store import VectorSearchResult
from app.schemas.reranker import RerankerHealthResponse


@dataclass(frozen=True, slots=True)
class RerankedChunk:
    """Reranker 精排后的 chunk。"""

    id: str
    text: str
    similarity_score: float
    raw_score: float
    rerank_score: float
    metadata: dict[str, object]
    chunk_index: int | None = None
    dense_score: float | None = None
    keyword_score: float | None = None
    hybrid_score: float | None = None


class BaseRerankerProvider(ABC):
    """Reranker Provider 基类。"""

    provider_name: ClassVar[str] = "base"

    def __init__(self, model: str, enabled: bool = True) -> None:
        self.model = model
        self.enabled = enabled

    @abstractmethod
    async def rerank(
        self,
        *,
        query: str,
        chunks: list[VectorSearchResult],
        top_n: int,
    ) -> list[RerankedChunk]:
        """根据 query 对候选 chunks 做精排。"""

    async def health_check(self) -> RerankerHealthResponse:
        """检查 Provider 是否可用。"""

        return RerankerHealthResponse(
            provider=self.provider_name,
            model=self.model,
            reachable=True,
            enabled=self.enabled,
            error=None,
        )
