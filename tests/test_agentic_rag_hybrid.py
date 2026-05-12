"""Agentic RAG Hybrid Search 编排测试模块。"""

from types import SimpleNamespace

import pytest

from app.rag.agentic_orchestrator import AgenticRAGOrchestrator
from app.rag.hybrid_search import HybridSearchBundle
from app.rag.vector_store import VectorSearchResult
from app.reranker.providers.base import RerankedChunk
from app.schemas.agentic_rag import AgenticRAGRequest
from app.schemas.llm import LLMRequest, LLMResponse


class FakeLLMClient:
    """LLM Client 替身。"""

    def __init__(self) -> None:
        self.last_request: LLMRequest | None = None

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """返回固定答案。"""

        self.last_request = request
        return LLMResponse(provider="mock", model="mock-llm", content="hybrid answer")


class FakeHybridSearchPipeline:
    """Hybrid Search Pipeline 替身。"""

    def __init__(self) -> None:
        self.vector_store = SimpleNamespace(collection_name="agentic_hybrid_collection")
        self.embedding_client = SimpleNamespace(provider=SimpleNamespace(provider_name="local", model="bge-m3"))
        self.last_search_mode: str | None = None
        self.last_dense_top_k: int | None = None
        self.last_keyword_top_k: int | None = None
        self.last_workspace_id: str | None = None

    async def search(
        self,
        *,
        query: str,
        search_mode: str,
        dense_top_k: int,
        keyword_top_k: int,
        workspace_id: str,
        source_id: str | None = None,
        status: str = "active",
    ) -> HybridSearchBundle:
        """返回 hybrid 中间结果。"""

        self.last_search_mode = search_mode
        self.last_dense_top_k = dense_top_k
        self.last_keyword_top_k = keyword_top_k
        self.last_workspace_id = workspace_id
        dense = VectorSearchResult(
            id="dense-id",
            text="dense vector candidate",
            similarity_score=0.7,
            raw_score=0.7,
            metadata={"workspace_id": workspace_id},
            chunk_index=0,
            dense_score=0.7,
            hybrid_score=0.7,
        )
        keyword = VectorSearchResult(
            id="keyword-id",
            text="keyword bm25 style candidate",
            similarity_score=0.6,
            raw_score=0.6,
            metadata={"workspace_id": workspace_id},
            chunk_index=1,
            keyword_score=0.6,
            hybrid_score=0.6,
        )
        merged = VectorSearchResult(
            id="merged-id",
            text="hybrid merged candidate for final prompt",
            similarity_score=0.88,
            raw_score=0.88,
            metadata={"workspace_id": workspace_id},
            chunk_index=2,
            dense_score=0.8,
            keyword_score=0.7,
            hybrid_score=0.88,
        )
        return HybridSearchBundle(
            search_mode="hybrid",
            dense_results=[dense],
            keyword_results=[keyword],
            merged_results=[merged],
        )


class FakeRerankerClient:
    """Reranker Client 替身。"""

    def __init__(self) -> None:
        self.provider = SimpleNamespace(provider_name="mock", model="mock-reranker")
        self.last_top_n: int | None = None

    async def rerank(
        self,
        *,
        query: str,
        chunks: list[VectorSearchResult],
        top_n: int | None = None,
    ) -> list[RerankedChunk]:
        """返回固定精排结果。"""

        self.last_top_n = top_n
        return [
            RerankedChunk(
                id=chunk.id,
                text=chunk.text,
                similarity_score=chunk.similarity_score,
                raw_score=chunk.raw_score,
                rerank_score=0.91,
                metadata=chunk.metadata,
                chunk_index=chunk.chunk_index,
                dense_score=chunk.dense_score,
                keyword_score=chunk.keyword_score,
                hybrid_score=chunk.hybrid_score,
            )
            for chunk in chunks[: top_n or len(chunks)]
        ]


@pytest.mark.asyncio
async def test_agentic_rag_hybrid_trace_contains_counts_and_scores() -> None:
    """Agentic RAG debug trace 应包含 Hybrid Search 和 Rerank 的关键字段。"""

    llm_client = FakeLLMClient()
    hybrid_pipeline = FakeHybridSearchPipeline()
    reranker = FakeRerankerClient()
    orchestrator = AgenticRAGOrchestrator(
        llm_client=llm_client,
        hybrid_search_pipeline=hybrid_pipeline,
        reranker_client=reranker,
        retrieval_top_k=20,
        keyword_top_k=20,
        search_mode="hybrid",
        rerank_top_n=5,
    )

    response = await orchestrator.query(
        AgenticRAGRequest(
            query="hybrid search trace",
            collection_name="agentic_hybrid_collection",
            debug=True,
        ),
        workspace_id="workspace-hybrid",
    )

    assert response.debug is not None
    assert hybrid_pipeline.last_search_mode == "hybrid"
    assert hybrid_pipeline.last_dense_top_k == 20
    assert hybrid_pipeline.last_keyword_top_k == 20
    assert hybrid_pipeline.last_workspace_id == "workspace-hybrid"
    assert reranker.last_top_n == 5
    assert response.debug.search_mode == "hybrid"
    assert response.debug.dense_results_count == 1
    assert response.debug.keyword_results_count == 1
    assert response.debug.merged_results_count == 1
    assert response.debug.final_results_count == 1
    assert response.debug.dense_scores == [0.7]
    assert response.debug.keyword_scores == [0.6]
    assert response.debug.hybrid_scores == [0.88]
    assert response.debug.rerank_scores == [0.91]
    assert response.debug.reranked_chunks[0].hybrid_score == 0.88
    assert "hybrid merged candidate for final prompt" in response.debug.final_prompt
