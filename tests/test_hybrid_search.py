"""Hybrid Search 测试模块。"""

from types import SimpleNamespace

import pytest

from app.rag.hybrid_search import HybridSearchPipeline
from app.rag.vector_store import VectorSearchResult


class FakeDenseRetrieval:
    """Dense Retrieval 替身。"""

    def __init__(self) -> None:
        self.vector_store = SimpleNamespace(collection_name="hybrid_collection")
        self.embedding_client = SimpleNamespace(provider=SimpleNamespace(provider_name="mock", model="mock-embedding"))
        self.last_top_k: int | None = None

    async def search(
        self,
        query: str,
        top_k: int = 5,
        source_id: str | None = None,
        workspace_id: str | None = None,
        status: str = "active",
    ) -> list[VectorSearchResult]:
        """返回固定 dense 结果。"""

        self.last_top_k = top_k
        return [
            VectorSearchResult(
                id="shared",
                text="dense and keyword shared chunk",
                similarity_score=0.8,
                raw_score=0.8,
                metadata={"source_id": source_id, "workspace_id": workspace_id},
                chunk_index=0,
                dense_score=0.8,
                hybrid_score=0.8,
            ),
            VectorSearchResult(
                id="dense-only",
                text="dense only chunk",
                similarity_score=0.7,
                raw_score=0.7,
                metadata={"source_id": source_id, "workspace_id": workspace_id},
                chunk_index=1,
                dense_score=0.7,
                hybrid_score=0.7,
            ),
        ]


class FakeKeywordSearch:
    """Keyword Search 替身。"""

    def __init__(self) -> None:
        self.last_top_k: int | None = None

    async def search(
        self,
        *,
        query: str,
        collection_name: str,
        top_k: int,
        workspace_id: str,
        source_id: str | None = None,
        status: str = "active",
    ) -> list[VectorSearchResult]:
        """返回固定 keyword 结果。"""

        self.last_top_k = top_k
        return [
            VectorSearchResult(
                id="shared",
                text="dense and keyword shared chunk",
                similarity_score=0.9,
                raw_score=0.9,
                metadata={"keyword": True, "workspace_id": workspace_id},
                chunk_index=0,
                keyword_score=0.9,
                hybrid_score=0.9,
            ),
            VectorSearchResult(
                id="keyword-only",
                text="keyword only chunk",
                similarity_score=0.6,
                raw_score=0.6,
                metadata={"keyword": True, "workspace_id": workspace_id},
                chunk_index=2,
                keyword_score=0.6,
                hybrid_score=0.6,
            ),
        ]


@pytest.mark.asyncio
async def test_hybrid_search_merges_dense_and_keyword_results() -> None:
    """Hybrid Search 应执行 dense + keyword 并按 chunk id 去重合并。"""

    dense = FakeDenseRetrieval()
    keyword = FakeKeywordSearch()
    pipeline = HybridSearchPipeline(retrieval_pipeline=dense, keyword_search=keyword)  # type: ignore[arg-type]

    bundle = await pipeline.search(
        query="hybrid search",
        search_mode="hybrid",
        dense_top_k=20,
        keyword_top_k=10,
        workspace_id="workspace-hybrid",
        source_id="source-hybrid",
    )

    ids = [result.id for result in bundle.merged_results]
    shared = next(result for result in bundle.merged_results if result.id == "shared")

    assert dense.last_top_k == 20
    assert keyword.last_top_k == 10
    assert len(bundle.dense_results) == 2
    assert len(bundle.keyword_results) == 2
    assert set(ids) == {"shared", "dense-only", "keyword-only"}
    assert shared.dense_score == 0.8
    assert shared.keyword_score == 0.9
    assert shared.hybrid_score == 0.89
    assert bundle.merged_results[0].id == "shared"


@pytest.mark.asyncio
async def test_hybrid_search_supports_dense_only_mode() -> None:
    """dense 模式应只调用 dense retrieval。"""

    dense = FakeDenseRetrieval()
    keyword = FakeKeywordSearch()
    pipeline = HybridSearchPipeline(retrieval_pipeline=dense, keyword_search=keyword)  # type: ignore[arg-type]

    bundle = await pipeline.search(
        query="dense search",
        search_mode="dense",
        dense_top_k=7,
        keyword_top_k=9,
        workspace_id="workspace-hybrid",
    )

    assert dense.last_top_k == 7
    assert keyword.last_top_k is None
    assert len(bundle.keyword_results) == 0
    assert len(bundle.merged_results) == 2
