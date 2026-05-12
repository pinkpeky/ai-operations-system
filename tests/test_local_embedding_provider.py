"""LocalEmbeddingProvider 测试模块。

使用 fake HTTP client 验证 Ollama /api/embeddings 兼容性，不依赖真实 Ollama。
"""

from typing import Any

import pytest

from app.rag.providers.local_embedding_provider import LocalEmbeddingProvider


class FakeResponse:
    """最小 HTTP 响应替身。"""

    def __init__(self, data: dict[str, Any], status_error: Exception | None = None) -> None:
        self.data = data
        self.status_error = status_error

    def raise_for_status(self) -> None:
        """模拟 httpx raise_for_status。"""

        if self.status_error is not None:
            raise self.status_error

    def json(self) -> dict[str, Any]:
        """返回 JSON 数据。"""

        return self.data


class FakeHTTPClient:
    """最小异步 HTTP client 替身。"""

    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []

    async def post(self, url: str, json: dict[str, Any]) -> FakeResponse:
        """模拟 Ollama /api/embeddings。"""

        self.calls.append((url, json))
        return FakeResponse({"embedding": [0.1, 0.2, 0.3, 0.4]})


@pytest.mark.asyncio
async def test_local_embedding_provider_calls_ollama_embeddings() -> None:
    """LocalEmbeddingProvider 应调用 Ollama /api/embeddings。"""

    http_client = FakeHTTPClient()
    provider = LocalEmbeddingProvider(
        base_url="http://localhost:11434/",
        model="bge-m3",
        dimension=384,
        timeout_seconds=120,
        http_client=http_client,
    )

    embeddings = await provider.embed_texts(["hello", "world"])

    assert embeddings == [[0.1, 0.2, 0.3, 0.4], [0.1, 0.2, 0.3, 0.4]]
    assert provider.dimension == 4
    assert http_client.calls[0] == (
        "http://localhost:11434/api/embeddings",
        {"model": "bge-m3", "prompt": "hello"},
    )
    assert http_client.calls[1][1]["prompt"] == "world"


@pytest.mark.asyncio
async def test_local_embedding_health_returns_detected_dimension() -> None:
    """health check 应返回真实 embedding 维度。"""

    provider = LocalEmbeddingProvider(
        base_url="http://localhost:11434",
        model="bge-m3",
        dimension=384,
        timeout_seconds=120,
        http_client=FakeHTTPClient(),
    )

    health = await provider.health_check()

    assert health.provider == "local"
    assert health.model == "bge-m3"
    assert health.reachable is True
    assert health.dimension == 4
    assert health.error is None


@pytest.mark.asyncio
async def test_local_embedding_health_handles_connection_error() -> None:
    """Ollama 不可用时 health check 应返回清晰错误，不导致系统崩溃。"""

    class FailingHTTPClient(FakeHTTPClient):
        async def post(self, url: str, json: dict[str, Any]) -> FakeResponse:
            raise RuntimeError("connection refused")

    provider = LocalEmbeddingProvider(
        base_url="http://localhost:11434",
        model="bge-m3",
        dimension=384,
        timeout_seconds=120,
        http_client=FailingHTTPClient(),
    )

    health = await provider.health_check()

    assert health.reachable is False
    assert health.dimension is None
    assert health.error == "connection refused"
