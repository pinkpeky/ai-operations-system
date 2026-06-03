"""Local semantic reranker runtime backed by Ollama embeddings."""

from __future__ import annotations

import asyncio
import logging
import math
from typing import Any, Protocol

import httpx

from worker.reranker_worker.config import RerankerWorkerSettings
from worker.reranker_worker.schemas import RerankerRuntimeHealthResponse, RerankRequest, RerankResponse

logger = logging.getLogger(__name__)


class AsyncHTTPClient(Protocol):
    """Minimal async HTTP client protocol used for tests and runtime."""

    async def post(self, url: str, json: dict[str, Any]) -> Any:
        """Send a POST request."""


class OllamaEmbeddingRerankerRuntime:
    """Semantic reranker that scores query/document pairs through a local embedding model."""

    def __init__(self, *, settings: RerankerWorkerSettings, http_client: AsyncHTTPClient | None = None) -> None:
        self.settings = settings
        self.provider = settings.reranker_runtime_provider
        self.engine = settings.reranker_runtime_engine.strip().lower()
        if self.engine != "ollama_embedding":
            raise ValueError(f"Unsupported reranker runtime engine: {settings.reranker_runtime_engine}")
        self.model = settings.reranker_runtime_model
        self.embedding_model = settings.reranker_runtime_embedding_model
        self.base_url = settings.reranker_runtime_embedding_base_url.rstrip("/")
        self.timeout_seconds = settings.reranker_runtime_timeout_seconds
        self.max_documents = settings.reranker_runtime_max_documents
        self.max_document_chars = settings.reranker_runtime_max_document_chars
        self.embedding_concurrency = settings.reranker_runtime_embedding_concurrency
        self._http_client = http_client
        self._detected_dimension: int | None = None

    async def health_check(self) -> RerankerRuntimeHealthResponse:
        """Verify the embedding backend with a lightweight request."""

        try:
            embedding = await self._embed_one("reranker health check")
            return RerankerRuntimeHealthResponse(
                provider=self.provider,
                model=self.model,
                engine=self.engine,
                embedding_model=self.embedding_model,
                reachable=True,
                enabled=True,
                dimension=len(embedding),
                error=None,
            )
        except Exception as exc:
            logger.warning("Reranker runtime health check failed", extra={"error": str(exc)})
            return RerankerRuntimeHealthResponse(
                provider=self.provider,
                model=self.model,
                engine=self.engine,
                embedding_model=self.embedding_model,
                reachable=False,
                enabled=True,
                dimension=self._detected_dimension,
                error=str(exc),
            )

    async def rerank(self, request: RerankRequest) -> RerankResponse:
        """Score all documents and return scores in the original document order."""

        query = request.query.strip()
        documents = [item.strip() for item in request.documents]
        if not query:
            raise ValueError("query cannot be empty")
        if not documents:
            raise ValueError("documents cannot be empty")
        if len(documents) > self.max_documents:
            raise ValueError(f"documents exceed limit: {len(documents)} > {self.max_documents}")
        if any(not item for item in documents):
            raise ValueError("documents cannot contain empty text")

        truncated_documents = [item[: self.max_document_chars] for item in documents]
        query_embedding = await self._embed_one(query)
        document_embeddings = await self._embed_many(truncated_documents)
        scores = [self._score(query_embedding, document_embedding) for document_embedding in document_embeddings]
        ranked_indices = sorted(range(len(scores)), key=lambda index: scores[index], reverse=True)
        top_n = min(request.top_n or len(scores), len(scores))
        return RerankResponse(
            provider=self.provider,
            model=request.model or self.model,
            engine=self.engine,
            embedding_model=self.embedding_model,
            scores=scores,
            ranked_indices=ranked_indices[:top_n],
            top_n=top_n,
        )

    async def _embed_many(self, texts: list[str]) -> list[list[float]]:
        semaphore = asyncio.Semaphore(self.embedding_concurrency)

        async def embed_with_limit(text: str) -> list[float]:
            async with semaphore:
                return await self._embed_one(text)

        return await asyncio.gather(*(embed_with_limit(text) for text in texts))

    async def _embed_one(self, text: str) -> list[float]:
        data = await self._post_json(
            "/api/embeddings",
            {
                "model": self.embedding_model,
                "prompt": text,
            },
        )
        embedding = data.get("embedding")
        if not isinstance(embedding, list) or not embedding:
            raise RuntimeError("embedding response is empty")
        vector = [float(value) for value in embedding]
        self._set_detected_dimension(len(vector))
        return vector

    async def _post_json(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        response = await self._request(path, payload)
        if hasattr(response, "raise_for_status"):
            response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict):
            raise RuntimeError("embedding response JSON must be an object")
        return data

    async def _request(self, path: str, payload: dict[str, Any]) -> Any:
        url = f"{self.base_url}{path}"
        if self._http_client is not None:
            return await self._http_client.post(url, json=payload)
        timeout = httpx.Timeout(self.timeout_seconds)
        async with httpx.AsyncClient(timeout=timeout) as client:
            return await client.post(url, json=payload)

    def _set_detected_dimension(self, dimension: int) -> None:
        if dimension <= 0:
            raise ValueError("embedding dimension must be positive")
        if self._detected_dimension is not None and self._detected_dimension != dimension:
            raise ValueError(
                "embedding dimension changed: "
                f"existing={self._detected_dimension}, received={dimension}"
            )
        self._detected_dimension = dimension

    @staticmethod
    def _score(query_embedding: list[float], document_embedding: list[float]) -> float:
        if len(query_embedding) != len(document_embedding):
            raise ValueError("embedding dimensions do not match")
        dot = sum(left * right for left, right in zip(query_embedding, document_embedding, strict=True))
        query_norm = math.sqrt(sum(value * value for value in query_embedding))
        document_norm = math.sqrt(sum(value * value for value in document_embedding))
        if query_norm <= 0 or document_norm <= 0:
            return 0.0
        cosine = dot / (query_norm * document_norm)
        return max(0.0, min(1.0, (cosine + 1.0) / 2.0))
