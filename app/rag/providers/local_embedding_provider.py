"""本地 Embedding Provider 模块。

该 Provider 兼容 Ollama /api/embeddings 接口，用于接入本机 bge-m3 embedding。
"""

import logging
from typing import Any, Protocol

import httpx

from app.rag.providers.base import BaseEmbeddingProvider
from app.schemas.rag import EmbeddingHealthResponse

logger = logging.getLogger(__name__)


class AsyncHTTPClient(Protocol):
    """LocalEmbeddingProvider 依赖的最小异步 HTTP Client 协议，便于单元测试替换。"""

    async def post(self, url: str, json: dict[str, Any]) -> Any:
        """发送 POST 请求。"""


class LocalEmbeddingProvider(BaseEmbeddingProvider):
    """Ollama 本地 embedding 服务 Provider。"""

    provider_name = "local"

    def __init__(
        self,
        base_url: str,
        model: str,
        dimension: int,
        timeout_seconds: float,
        http_client: AsyncHTTPClient | None = None,
    ) -> None:
        super().__init__(dimension=dimension, model=model)
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self._http_client = http_client
        self._detected_dimension: int | None = None

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """调用 Ollama /api/embeddings 生成文本向量。"""

        try:
            embeddings = [await self._embed_one(text) for text in texts]
            logger.info(
                "Local Ollama embeddings generated",
                extra={
                    "provider": self.provider_name,
                    "model": self.model,
                    "count": len(embeddings),
                    "dimension": self.dimension,
                },
            )
            return embeddings
        except Exception as exc:
            logger.exception("Local Ollama embedding provider failed")
            raise RuntimeError(f"Local Ollama embedding provider failed: {exc}") from exc

    async def health_check(self) -> EmbeddingHealthResponse:
        """通过一次轻量 embedding 请求检查 Ollama bge-m3 是否可用并探测维度。"""

        try:
            embedding = await self._embed_one("embedding health check")
            return EmbeddingHealthResponse(
                provider=self.provider_name,
                model=self.model,
                reachable=True,
                dimension=len(embedding),
                error=None,
            )
        except Exception as exc:
            logger.warning("Local Ollama embedding health check failed", extra={"error": str(exc)})
            return EmbeddingHealthResponse(
                provider=self.provider_name,
                model=self.model,
                reachable=False,
                dimension=self._detected_dimension,
                error=str(exc),
            )

    async def _embed_one(self, text: str) -> list[float]:
        """调用 Ollama 单条 embedding 接口并返回向量。"""

        payload = {
            "model": self.model,
            "prompt": text,
        }
        data = await self._post_json("/api/embeddings", payload)
        embedding = data.get("embedding")
        if not isinstance(embedding, list) or not embedding:
            raise RuntimeError("Ollama embedding response is empty")
        vector = [float(value) for value in embedding]
        self._set_detected_dimension(len(vector))
        return vector

    async def _post_json(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        """发送 POST 请求并解析 JSON。"""

        response = await self._request(path, payload)
        if hasattr(response, "raise_for_status"):
            response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict):
            raise RuntimeError("Ollama embedding response JSON must be an object")
        return data

    async def _request(self, path: str, payload: dict[str, Any]) -> Any:
        """发送 HTTP 请求，支持注入测试 client。"""

        url = f"{self.base_url}{path}"
        if self._http_client is not None:
            return await self._http_client.post(url, json=payload)

        timeout = httpx.Timeout(self.timeout_seconds)
        async with httpx.AsyncClient(timeout=timeout) as client:
            return await client.post(url, json=payload)

    def _set_detected_dimension(self, dimension: int) -> None:
        """记录 Ollama 返回的真实向量维度。"""

        if dimension <= 0:
            raise ValueError("Embedding dimension must be positive")
        if self._detected_dimension is not None and self._detected_dimension != dimension:
            raise ValueError(
                "Ollama embedding dimension changed: "
                f"existing={self._detected_dimension}, received={dimension}"
            )
        self._detected_dimension = dimension
        self.dimension = dimension
