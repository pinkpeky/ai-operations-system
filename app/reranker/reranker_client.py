"""Reranker Client 模块。

Client 负责按配置选择 provider，并向上层编排器暴露统一 rerank/health 接口。
"""

import logging

from app.core.config import Settings, get_settings
from app.rag.vector_store import VectorSearchResult
from app.reranker.providers.base import BaseRerankerProvider, RerankedChunk
from app.reranker.providers.local_reranker_provider import LocalRerankerProvider
from app.reranker.providers.mock_reranker_provider import MockRerankerProvider
from app.schemas.reranker import RerankerHealthResponse

logger = logging.getLogger(__name__)


class RerankerClient:
    """Reranker 统一客户端。"""

    def __init__(
        self,
        settings: Settings | None = None,
        provider: BaseRerankerProvider | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.provider = provider or self._create_provider(self.settings)

    async def rerank(
        self,
        *,
        query: str,
        chunks: list[VectorSearchResult],
        top_n: int | None = None,
    ) -> list[RerankedChunk]:
        """对候选 chunks 做精排。"""

        if not chunks:
            return []
        resolved_top_n = top_n or self.settings.rerank_top_n
        if resolved_top_n <= 0:
            raise ValueError("rerank top_n must be positive")
        try:
            results = await self.provider.rerank(query=query, chunks=chunks, top_n=resolved_top_n)
            logger.info(
                "Reranker client completed",
                extra={
                    "provider": self.provider.provider_name,
                    "model": self.provider.model,
                    "candidate_count": len(chunks),
                    "returned_count": len(results),
                },
            )
            return results
        except ValueError:
            logger.exception("Reranker request validation failed")
            raise
        except Exception as exc:
            logger.exception("Reranker client failed")
            raise RuntimeError(f"Reranker client failed: {exc}") from exc

    async def health_check(self) -> RerankerHealthResponse:
        """检查当前 Reranker Provider 健康状态。"""

        return await self.provider.health_check()

    def _create_provider(self, settings: Settings) -> BaseRerankerProvider:
        """按配置创建 Reranker Provider。"""

        provider_name = settings.reranker_provider.strip().lower()
        if provider_name == "mock":
            return MockRerankerProvider()
        if provider_name == "local":
            return LocalRerankerProvider(
                base_url=settings.local_reranker_base_url,
                model=settings.local_reranker_model,
                timeout_seconds=settings.llm_timeout_seconds,
                allow_fallback=settings.local_reranker_allow_fallback,
            )
        raise ValueError(f"Unsupported reranker provider: {settings.reranker_provider}")
