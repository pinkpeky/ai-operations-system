"""Agentic RAG Rerank 编排测试模块。"""

from types import SimpleNamespace

import pytest

from app.rag.agentic_orchestrator import AgenticRAGOrchestrator
from app.rag.vector_store import VectorSearchResult
from app.reranker.providers.base import RerankedChunk
from app.schemas.agentic_rag import AgenticRAGRequest
from app.schemas.llm import LLMRequest, LLMResponse


class RecordingLLMClient:
    """记录最终 prompt 的 LLM Client 替身。"""

    def __init__(self) -> None:
        self.last_request: LLMRequest | None = None

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """返回固定答案。"""

        self.last_request = request
        return LLMResponse(provider="mock", model="mock-llm", content="reranked answer")


class ManyChunkRetrievalPipeline:
    """返回多条候选结果的 Retrieval Pipeline 替身。"""

    def __init__(self) -> None:
        self.vector_store = SimpleNamespace(collection_name="rerank_collection")
        self.embedding_client = SimpleNamespace(provider=SimpleNamespace(provider_name="local", model="bge-m3"))
        self.last_top_k: int | None = None

    async def search(
        self,
        query: str,
        top_k: int = 5,
        source_id: str | None = None,
        workspace_id: str | None = None,
        status: str = "active",
    ) -> list[VectorSearchResult]:
        """返回候选 chunks，验证编排器会拉取 top_k=20。"""

        self.last_top_k = top_k
        return [
            VectorSearchResult(
                id="11111111-1111-4111-8111-111111111111",
                text="low value scheduler chunk",
                similarity_score=0.95,
                raw_score=0.95,
                metadata={"rank": "before"},
                chunk_index=0,
            ),
            VectorSearchResult(
                id="22222222-2222-4222-8222-222222222222",
                text="high value reranker trace chunk",
                similarity_score=0.55,
                raw_score=0.55,
                metadata={"rank": "after"},
                chunk_index=1,
            ),
        ]


class ReorderingRerankerClient:
    """把第二条候选排到第一位的 Reranker Client 替身。"""

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
        """返回精排后的 top_n chunks。"""

        self.last_top_n = top_n
        ordered = [chunks[1], chunks[0]]
        return [
            RerankedChunk(
                id=chunk.id,
                text=chunk.text,
                similarity_score=chunk.similarity_score,
                raw_score=chunk.raw_score,
                rerank_score=0.99 if index == 0 else 0.1,
                metadata=chunk.metadata,
                chunk_index=chunk.chunk_index,
            )
            for index, chunk in enumerate(ordered[: top_n or len(ordered)])
        ]


@pytest.mark.asyncio
async def test_agentic_rag_uses_reranked_top_n_for_prompt() -> None:
    """Agentic RAG 应用 embedding topK -> reranker topN -> prompt 的顺序编排。"""

    llm_client = RecordingLLMClient()
    retrieval_pipeline = ManyChunkRetrievalPipeline()
    reranker_client = ReorderingRerankerClient()
    orchestrator = AgenticRAGOrchestrator(
        llm_client=llm_client,
        retrieval_pipeline=retrieval_pipeline,
        reranker_client=reranker_client,
        retrieval_top_k=20,
        rerank_top_n=1,
    )

    response = await orchestrator.query(
        AgenticRAGRequest(
            query="reranker trace",
            collection_name="rerank_collection",
            top_k=3,
            debug=True,
        ),
        workspace_id="workspace-rerank",
    )

    assert response.answer == "reranked answer"
    assert retrieval_pipeline.last_top_k == 20
    assert reranker_client.last_top_n == 1
    assert len(response.retrieved_chunks) == 1
    assert response.retrieved_chunks[0].text == "high value reranker trace chunk"
    assert response.debug is not None
    assert len(response.debug.retrieval_before_rerank) == 2
    assert len(response.debug.retrieval_after_rerank) == 1
    assert response.debug.rerank_scores == [0.99]
    assert "high value reranker trace chunk" in response.debug.final_prompt
    assert "low value scheduler chunk" not in response.debug.final_prompt
