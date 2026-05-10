"""本地 Embedding Provider 预留模块。

该 Provider 当前只保留配置入口，后续可接入本地 embedding 服务。
"""

import logging

from app.rag.providers.base import BaseEmbeddingProvider

logger = logging.getLogger(__name__)


class LocalEmbeddingProvider(BaseEmbeddingProvider):
    """本地 embedding 服务 Provider 预留实现。"""

    provider_name = "local"

    def __init__(
        self,
        base_url: str,
        model: str,
        dimension: int,
        timeout_seconds: float,
    ) -> None:
        super().__init__(dimension=dimension, model=model)
        self.base_url = base_url
        self.timeout_seconds = timeout_seconds

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """预留真实本地 embedding 调用接口。"""

        logger.warning(
            "Local embedding provider is not implemented",
            extra={
                "provider": self.provider_name,
                "base_url": self.base_url,
                "model": self.model,
                "dimension": self.dimension,
                "count": len(texts),
            },
        )
        raise NotImplementedError("LocalEmbeddingProvider is reserved for future integration")
