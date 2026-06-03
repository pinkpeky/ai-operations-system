"""Reranker Client 测试模块。"""

import pytest

from app.core.config import Settings
from app.rag.vector_store import VectorSearchResult
from app.reranker.providers.local_reranker_provider import LocalRerankerProvider
from app.reranker.reranker_client import RerankerClient


class FakeHTTPResponse:
    """Minimal JSON response object for local provider tests."""

    def __init__(self, payload: dict[str, object]) -> None:
        self.payload = payload

    def json(self) -> dict[str, object]:
        return self.payload

    def raise_for_status(self) -> None:
        return None


class FakeHTTPErrorClient:
    """始终失败的 HTTP Client，用于验证 graceful fallback。"""

    async def get(self, url: str):  # type: ignore[no-untyped-def]
        """模拟本地服务不可达。"""

        raise RuntimeError("service unavailable")

    async def post(self, url: str, json: dict[str, object]):  # type: ignore[no-untyped-def]
        """模拟 rerank 接口不可用。"""

        raise RuntimeError("rerank endpoint unavailable")


class FakeHTTPSuccessClient:
    """Fake reranker runtime that returns explicit scores."""

    def __init__(self) -> None:
        self.last_payload: dict[str, object] | None = None

    async def get(self, url: str) -> FakeHTTPResponse:
        return FakeHTTPResponse(
            {
                "provider": "local",
                "model": "bge-m3-embedding-reranker",
                "reachable": True,
                "enabled": True,
            }
        )

    async def post(self, url: str, json: dict[str, object]) -> FakeHTTPResponse:
        self.last_payload = json
        return FakeHTTPResponse({"scores": [0.2, 0.95]})


def make_result(text: str, similarity_score: float) -> VectorSearchResult:
    """构造检索结果。"""

    return VectorSearchResult(
        id="dddddddd-dddd-4ddd-dddd-dddddddddddd",
        text=text,
        similarity_score=similarity_score,
        raw_score=similarity_score,
        metadata={"source_id": "reranker"},
        chunk_index=0,
    )


@pytest.mark.asyncio
async def test_reranker_client_uses_mock_provider_from_config() -> None:
    """RerankerClient 应根据配置创建 mock provider 并返回精排结果。"""

    client = RerankerClient(settings=Settings(RERANKER_PROVIDER="mock", RERANK_TOP_N=1))
    results = await client.rerank(
        query="rag trace",
        chunks=[
            make_result("unrelated scheduler queue", 0.9),
            make_result("rag debug trace", 0.4),
        ],
    )
    health = await client.health_check()

    assert client.provider.provider_name == "mock"
    assert len(results) == 1
    assert results[0].text == "rag debug trace"
    assert health.provider == "mock"
    assert health.enabled is True
    assert health.reachable is True


@pytest.mark.asyncio
async def test_local_reranker_falls_back_to_mock_when_endpoint_unavailable() -> None:
    """local reranker 接口不可用时不应阻塞系统，应回退 mock rerank。"""

    provider = LocalRerankerProvider(
        base_url="http://localhost:11434",
        model="local-reranker-model",
        timeout_seconds=1,
        http_client=FakeHTTPErrorClient(),
    )
    client = RerankerClient(settings=Settings(RERANKER_PROVIDER="local"), provider=provider)

    results = await client.rerank(
        query="reranker trace",
        chunks=[
            make_result("reranker trace chunk", 0.3),
            make_result("other text", 0.99),
        ],
        top_n=1,
    )
    health = await client.health_check()

    assert results[0].text == "reranker trace chunk"
    assert results[0].rerank_score > 0
    assert health.provider == "local"
    assert health.enabled is True
    assert health.reachable is False
    assert "fallback" in (health.error or "")


@pytest.mark.asyncio
async def test_local_reranker_uses_runtime_scores() -> None:
    """local provider should call /api/rerank and sort by returned runtime scores."""

    http_client = FakeHTTPSuccessClient()
    provider = LocalRerankerProvider(
        base_url="http://localhost:8002",
        model="bge-m3-embedding-reranker",
        timeout_seconds=1,
        http_client=http_client,
    )

    results = await provider.rerank(
        query="reranker trace",
        chunks=[
            make_result("low value text", 0.99),
            make_result("high value text", 0.1),
        ],
        top_n=1,
    )
    health = await provider.health_check()

    assert results[0].text == "high value text"
    assert results[0].rerank_score == 0.95
    assert http_client.last_payload is not None
    assert http_client.last_payload["top_n"] == 1
    assert health.reachable is True


@pytest.mark.asyncio
async def test_local_reranker_can_fail_closed_without_mock_fallback() -> None:
    """production local reranker should be able to fail closed instead of hiding errors."""

    provider = LocalRerankerProvider(
        base_url="http://localhost:8002",
        model="bge-m3-embedding-reranker",
        timeout_seconds=1,
        allow_fallback=False,
        http_client=FakeHTTPErrorClient(),
    )

    with pytest.raises(RuntimeError, match="Local reranker unavailable"):
        await provider.rerank(query="reranker trace", chunks=[make_result("text", 0.5)], top_n=1)

    health = await provider.health_check()
    assert health.reachable is False
    assert "fallback disabled" in (health.error or "")
