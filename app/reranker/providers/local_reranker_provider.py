"""本地 Reranker Provider 模块。

Ollama 当前没有稳定通用的原生 rerank API。本 Provider 预留 HTTP 接口，
如果本地服务不可用或接口不存在，则优雅回退到 MockRerankerProvider。
"""

import logging
from typing import Any, Protocol

import httpx

from app.rag.vector_store import VectorSearchResult
from app.reranker.providers.base import BaseRerankerProvider, RerankedChunk
from app.reranker.providers.mock_reranker_provider import MockRerankerProvider
from app.schemas.reranker import RerankerHealthResponse

logger = logging.getLogger(__name__)


class AsyncHTTPClient(Protocol):
    """LocalRerankerProvider 依赖的最小异步 HTTP Client 协议。"""

    async def get(self, url: str) -> Any:
        """发送 GET 请求。"""

    async def post(self, url: str, json: dict[str, Any]) -> Any:
        """发送 POST 请求。"""


class LocalRerankerProvider(BaseRerankerProvider):
    """本地 reranker 服务 Provider，当前以 graceful fallback 为主。"""

    provider_name = "local"

    def __init__(
        self,
        *,
        base_url: str,
        model: str,
        timeout_seconds: float,
        http_client: AsyncHTTPClient | None = None,
        fallback_provider: MockRerankerProvider | None = None,
    ) -> None:
        super().__init__(model=model, enabled=True)
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self._http_client = http_client
        self._fallback_provider = fallback_provider or MockRerankerProvider()

    async def rerank(
        self,
        *,
        query: str,
        chunks: list[VectorSearchResult],
        top_n: int,
    ) -> list[RerankedChunk]:
        """调用预留本地 rerank 接口，失败时回退到 mock rerank。"""

        try:
            data = await self._post_json(
                "/api/rerank",
                {
                    "model": self.model,
                    "query": query,
                    "documents": [chunk.text for chunk in chunks],
                },
            )
            scores = data.get("scores")
            if not isinstance(scores, list) or len(scores) != len(chunks):
                raise RuntimeError("local reranker response scores are invalid")
            reranked = [
                RerankedChunk(
                    id=chunk.id,
                    text=chunk.text,
                    similarity_score=chunk.similarity_score,
                    raw_score=chunk.raw_score,
                    rerank_score=max(0.0, min(1.0, float(score))),
                    metadata=chunk.metadata,
                    chunk_index=chunk.chunk_index,
                    dense_score=chunk.dense_score,
                    keyword_score=chunk.keyword_score,
                    hybrid_score=chunk.hybrid_score,
                )
                for chunk, score in zip(chunks, scores, strict=True)
            ]
            reranked.sort(key=lambda item: (item.rerank_score, item.similarity_score), reverse=True)
            logger.info("Local reranker completed", extra={"model": self.model, "top_n": top_n})
            return reranked[:top_n]
        except Exception as exc:
            logger.warning("Local reranker unavailable, falling back to mock", extra={"error": str(exc)})
            return await self._fallback_provider.rerank(query=query, chunks=chunks, top_n=top_n)

    async def health_check(self) -> RerankerHealthResponse:
        """检查预留本地 reranker 服务；Ollama 无原生接口时返回清晰不可达状态。"""

        try:
            await self._get_json("/api/tags")
            return RerankerHealthResponse(
                provider=self.provider_name,
                model=self.model,
                reachable=False,
                enabled=self.enabled,
                error="Local Ollama is reachable, but native reranker API is not enabled; mock fallback will be used.",
            )
        except Exception as exc:
            logger.warning("Local reranker health check failed", extra={"error": str(exc)})
            return RerankerHealthResponse(
                provider=self.provider_name,
                model=self.model,
                reachable=False,
                enabled=self.enabled,
                error=f"{exc}; mock fallback will be used.",
            )

    async def _get_json(self, path: str) -> dict[str, Any]:
        """发送 GET 请求并解析 JSON。"""

        response = await self._request("GET", path)
        return self._response_json(response)

    async def _post_json(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        """发送 POST 请求并解析 JSON。"""

        response = await self._request("POST", path, payload)
        return self._response_json(response)

    async def _request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> Any:
        """发送 HTTP 请求，支持测试注入 client。"""

        url = f"{self.base_url}{path}"
        if self._http_client is not None:
            if method == "GET":
                return await self._http_client.get(url)
            return await self._http_client.post(url, json=payload or {})

        timeout = httpx.Timeout(self.timeout_seconds)
        async with httpx.AsyncClient(timeout=timeout) as client:
            if method == "GET":
                return await client.get(url)
            return await client.post(url, json=payload or {})

    def _response_json(self, response: Any) -> dict[str, Any]:
        """统一处理 HTTP 响应。"""

        if hasattr(response, "raise_for_status"):
            response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict):
            raise RuntimeError("Local reranker response JSON must be an object")
        return data
