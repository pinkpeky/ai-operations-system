"""Embedding Client 模块。

该模块负责根据配置选择 Embedding Provider，不直接操作 Qdrant，也不参与 LLM Client 调用。
"""

import logging

from app.core.config import Settings, get_settings
from app.rag.providers.base import BaseEmbeddingProvider
from app.rag.providers.local_embedding_provider import LocalEmbeddingProvider
from app.rag.providers.mock_embedding_provider import MockEmbeddingProvider
from app.schemas.rag import EmbeddingHealthResponse

logger = logging.getLogger(__name__)


class EmbeddingClient:
    """统一 Embedding 客户端。"""

    def __init__(
        self,
        settings: Settings | None = None,
        provider: BaseEmbeddingProvider | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.provider = provider or self._create_provider(self.settings)

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """生成文本向量。"""

        try:
            normalized_texts = [text for text in texts if text.strip()]
            if len(normalized_texts) != len(texts):
                raise ValueError("Embedding text cannot be empty")
            embeddings = await self.provider.embed_texts(normalized_texts)
            self._validate_embeddings(embeddings, len(normalized_texts))
            logger.info(
                "Embeddings generated",
                extra={
                    "provider": self.provider.provider_name,
                    "model": self.provider.model,
                    "count": len(embeddings),
                },
            )
            return embeddings
        except ValueError:
            logger.exception("Embedding request validation failed")
            raise
        except NotImplementedError as exc:
            logger.exception("Embedding provider is not implemented")
            raise RuntimeError(str(exc)) from exc
        except Exception as exc:
            logger.exception("Embedding generation failed")
            raise RuntimeError(str(exc) or "Embedding generation failed") from exc

    async def embed_query(self, query: str) -> list[float]:
        """生成查询向量。"""

        if not query.strip():
            raise ValueError("Query cannot be empty")
        embedding = await self.provider.embed_query(query)
        self._validate_embeddings([embedding], 1)
        return embedding

    async def health_check(self) -> EmbeddingHealthResponse:
        """检查当前 Embedding Provider 是否可用。"""

        try:
            return await self.provider.health_check()
        except Exception as exc:
            logger.exception("Embedding health check failed")
            return EmbeddingHealthResponse(
                provider=self.provider.provider_name,
                model=self.provider.model,
                reachable=False,
                dimension=getattr(self.provider, "dimension", None),
                error=str(exc),
            )

    async def resolve_dimension(self) -> int:
        """解析当前 Provider 的真实向量维度。"""

        health = await self.health_check()
        if not health.reachable or health.dimension is None:
            raise RuntimeError(health.error or "Embedding provider is not reachable")
        self.provider.dimension = health.dimension
        return health.dimension

    def _create_provider(self, settings: Settings) -> BaseEmbeddingProvider:
        """根据配置创建 Embedding Provider。"""

        provider_name = settings.embedding_provider.strip().lower()
        try:
            if provider_name == "mock":
                return MockEmbeddingProvider(dimension=settings.embedding_dimension)
            if provider_name == "local":
                return LocalEmbeddingProvider(
                    base_url=settings.local_embedding_base_url,
                    model=settings.local_embedding_model,
                    dimension=settings.embedding_dimension,
                    timeout_seconds=settings.llm_timeout_seconds,
                )
            raise ValueError(f"Unsupported embedding provider: {settings.embedding_provider}")
        except ValueError:
            logger.exception("Invalid embedding provider configuration")
            raise
        except Exception as exc:
            logger.exception("Failed to create embedding provider", extra={"provider": provider_name})
            raise RuntimeError("Failed to create embedding provider") from exc

    def _validate_embeddings(self, embeddings: list[list[float]], expected_count: int) -> None:
        """校验 Provider 返回的向量数量和维度。"""

        if len(embeddings) != expected_count:
            raise ValueError("Embedding provider returned unexpected embedding count")
        for embedding in embeddings:
            if len(embedding) != self.provider.dimension:
                raise ValueError("Embedding provider returned unexpected embedding dimension")
