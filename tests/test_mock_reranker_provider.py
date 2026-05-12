"""Mock Reranker Provider 测试模块。"""

import pytest

from app.rag.vector_store import VectorSearchResult
from app.reranker.providers.mock_reranker_provider import MockRerankerProvider


def make_result(text: str, similarity_score: float, chunk_index: int) -> VectorSearchResult:
    """构造检索结果。"""

    return VectorSearchResult(
        id=f"aaaaaaaa-aaaa-4aaa-aaaa-aaaaaaaaaaa{chunk_index}",
        text=text,
        similarity_score=similarity_score,
        raw_score=similarity_score,
        metadata={"chunk_index": chunk_index},
        chunk_index=chunk_index,
    )


@pytest.mark.asyncio
async def test_mock_reranker_sorts_by_query_token_overlap() -> None:
    """Mock reranker 应优先返回与 query token 重叠更多的 chunk。"""

    provider = MockRerankerProvider()
    chunks = [
        make_result("scheduler queue status", 0.95, 0),
        make_result("rag eval trace reranker score", 0.5, 1),
        make_result("agentic rag prompt assembly", 0.8, 2),
    ]

    results = await provider.rerank(query="rag reranker trace", chunks=chunks, top_n=2)

    assert [result.text for result in results] == [
        "rag eval trace reranker score",
        "agentic rag prompt assembly",
    ]
    assert results[0].rerank_score >= results[1].rerank_score
    assert results[0].similarity_score == 0.5


@pytest.mark.asyncio
async def test_mock_reranker_rejects_invalid_top_n() -> None:
    """top_n 必须为正数。"""

    provider = MockRerankerProvider()

    with pytest.raises(ValueError):
        await provider.rerank(query="rag", chunks=[], top_n=0)
