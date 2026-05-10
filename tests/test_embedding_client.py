"""Embedding Client 测试模块。

验证 MockEmbeddingProvider 不依赖真实模型服务，并返回稳定、归一化、固定维度向量。
"""

import math

import pytest

from app.core.config import Settings
from app.rag.embedding_client import EmbeddingClient
from app.rag.providers.mock_embedding_provider import MockEmbeddingProvider


@pytest.mark.asyncio
async def test_embedding_client_mock_provider_returns_expected_dimension() -> None:
    """Mock provider 应返回配置指定维度的向量。"""

    provider = MockEmbeddingProvider(dimension=8)
    client = EmbeddingClient(provider=provider)

    embeddings = await client.embed_texts(["AI operations system", "knowledge base"])

    assert len(embeddings) == 2
    assert all(len(embedding) == 8 for embedding in embeddings)
    assert embeddings[0] == await provider.embed_query("AI operations system")


@pytest.mark.asyncio
async def test_embedding_dimension_matches_settings() -> None:
    """Embedding 维度必须等于 EMBEDDING_DIMENSION 对应配置。"""

    settings = Settings(EMBEDDING_DIMENSION=16)
    client = EmbeddingClient(settings=settings)

    embedding = await client.embed_query("embedding dimension check")

    assert len(embedding) == settings.embedding_dimension


@pytest.mark.asyncio
async def test_mock_embedding_is_normalized_and_non_negative() -> None:
    """Mock embedding 应归一化，并避免明显异常的负向量分数。"""

    provider = MockEmbeddingProvider(dimension=32)

    embedding = await provider.embed_query("embedding pipeline qdrant retrieval")
    norm = math.sqrt(sum(value * value for value in embedding))

    assert norm == pytest.approx(1.0)
    assert min(embedding) >= 0.0


@pytest.mark.asyncio
async def test_embedding_client_rejects_empty_text() -> None:
    """空文本不应进入 embedding provider。"""

    client = EmbeddingClient(provider=MockEmbeddingProvider(dimension=8))

    with pytest.raises(ValueError, match="Embedding text cannot be empty"):
        await client.embed_texts(["normal text", " "])
