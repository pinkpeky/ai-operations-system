"""Standalone reranker worker runtime tests."""

import httpx
import pytest

from worker.reranker_worker.config import RerankerWorkerSettings
from worker.reranker_worker.main import create_app
from worker.reranker_worker.runtime import OllamaEmbeddingRerankerRuntime
from worker.reranker_worker.schemas import RerankRequest


class FakeEmbeddingResponse:
    """Minimal Ollama embedding response."""

    def __init__(self, embedding: list[float]) -> None:
        self.embedding = embedding

    def json(self) -> dict[str, list[float]]:
        return {"embedding": self.embedding}

    def raise_for_status(self) -> None:
        return None


class FakeEmbeddingClient:
    """Return stable embeddings based on the prompt text."""

    async def post(self, url: str, json: dict[str, object]) -> FakeEmbeddingResponse:
        prompt = str(json["prompt"]).lower()
        if "alpha" in prompt:
            return FakeEmbeddingResponse([1.0, 0.0])
        if "beta" in prompt:
            return FakeEmbeddingResponse([0.0, 1.0])
        return FakeEmbeddingResponse([0.5, 0.5])


def make_runtime() -> OllamaEmbeddingRerankerRuntime:
    settings = RerankerWorkerSettings(
        _env_file=None,
        RERANKER_RUNTIME_EMBEDDING_BASE_URL="http://ollama:11434",
        RERANKER_RUNTIME_EMBEDDING_MODEL="bge-m3",
        RERANKER_RUNTIME_MODEL="bge-m3-embedding-reranker",
    )
    return OllamaEmbeddingRerankerRuntime(settings=settings, http_client=FakeEmbeddingClient())


@pytest.mark.asyncio
async def test_reranker_runtime_scores_documents_by_embedding_similarity() -> None:
    runtime = make_runtime()

    response = await runtime.rerank(
        RerankRequest(
            model="bge-m3-embedding-reranker",
            query="alpha customer intent",
            documents=["beta unrelated text", "alpha matching text"],
            top_n=1,
        )
    )

    assert response.scores[1] > response.scores[0]
    assert response.ranked_indices == [1]
    assert response.embedding_model == "bge-m3"


@pytest.mark.asyncio
async def test_reranker_worker_http_contract() -> None:
    app = create_app(runtime=make_runtime())
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://reranker-worker:8002") as client:
        health = await client.get("/health")
        rerank = await client.post(
            "/api/rerank",
            json={
                "model": "bge-m3-embedding-reranker",
                "query": "alpha",
                "documents": ["beta", "alpha"],
                "top_n": 1,
            },
        )

    assert health.status_code == 200
    assert health.json()["reachable"] is True
    assert rerank.status_code == 200
    assert rerank.json()["ranked_indices"] == [1]
    assert len(rerank.json()["scores"]) == 2
