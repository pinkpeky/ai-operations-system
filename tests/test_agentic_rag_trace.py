"""Agentic RAG Trace 测试模块。"""

from types import SimpleNamespace

import pytest

from app.rag.agentic_orchestrator import AgenticRAGOrchestrator
from app.rag.vector_store import VectorSearchResult
from app.reranker.providers.base import RerankedChunk
from app.schemas.agentic_rag import AgenticRAGRequest
from app.schemas.llm import LLMRequest, LLMResponse


class TraceLLMClient:
    """Trace 测试用 LLM Client 替身。"""

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """返回固定答案，并让 trace 能保存最终回答。"""

        return LLMResponse(
            provider="local",
            model="mistral",
            content=f"answer based on: {request.user_prompt[:30]}",
        )


class TraceRetrievalPipeline:
    """Trace 测试用 Retrieval Pipeline 替身。"""

    def __init__(self) -> None:
        self.vector_store = SimpleNamespace(collection_name="trace_collection")
        self.embedding_client = SimpleNamespace(provider=SimpleNamespace(provider_name="local", model="bge-m3"))
        self.last_workspace_id: str | None = None

    async def search(
        self,
        query: str,
        top_k: int = 5,
        source_id: str | None = None,
        workspace_id: str | None = None,
        status: str = "active",
    ) -> list[VectorSearchResult]:
        """返回固定检索结果，并记录 workspace 过滤条件。"""

        self.last_workspace_id = workspace_id
        return [
            VectorSearchResult(
                id="cccccccc-cccc-4ccc-cccc-cccccccccccc",
                text="Phase 8 adds RAG eval runs, eval items and debug trace.",
                similarity_score=0.93,
                raw_score=0.928,
                metadata={"source_id": "phase8", "workspace_id": workspace_id, "status": status},
                chunk_index=0,
            )
        ][:top_k]


class TraceRerankerClient:
    """Trace 测试用 Reranker Client 替身。"""

    def __init__(self) -> None:
        self.provider = SimpleNamespace(provider_name="mock", model="mock-reranker")

    async def rerank(
        self,
        *,
        query: str,
        chunks: list[VectorSearchResult],
        top_n: int | None = None,
    ) -> list[RerankedChunk]:
        """返回带 rerank_score 的固定精排结果。"""

        limit = top_n or len(chunks)
        return [
            RerankedChunk(
                id=chunk.id,
                text=chunk.text,
                similarity_score=chunk.similarity_score,
                raw_score=chunk.raw_score,
                rerank_score=0.81,
                metadata=chunk.metadata,
                chunk_index=chunk.chunk_index,
            )
            for chunk in chunks[:limit]
        ]


@pytest.mark.asyncio
async def test_agentic_rag_debug_trace_contains_required_fields() -> None:
    """debug=true 时应返回完整 trace，便于后续对比 reranker 前后效果。"""

    retrieval_pipeline = TraceRetrievalPipeline()
    orchestrator = AgenticRAGOrchestrator(
        llm_client=TraceLLMClient(),
        retrieval_pipeline=retrieval_pipeline,
        reranker_client=TraceRerankerClient(),
    )

    response = await orchestrator.query(
        AgenticRAGRequest(
            query="Phase 8 做了什么？",
            collection_name="trace_collection",
            top_k=1,
            debug=True,
        ),
        workspace_id="workspace-trace",
    )

    assert response.debug is not None
    assert response.debug.query == "Phase 8 做了什么？"
    assert response.debug.workspace_id == "workspace-trace"
    assert response.debug.collection_name == "trace_collection"
    assert response.debug.retrieved_chunks[0].metadata["workspace_id"] == "workspace-trace"
    assert response.debug.similarity_scores == [0.93]
    assert response.debug.reranker_provider == "mock"
    assert response.debug.reranker_model == "mock-reranker"
    assert response.debug.rerank_scores == [0.81]
    assert len(response.debug.retrieval_before_rerank) == 1
    assert len(response.debug.retrieval_after_rerank) == 1
    assert response.debug.reranked_chunks[0].rerank_score == 0.81
    assert "检索上下文" in response.debug.final_prompt
    assert response.debug.final_answer == response.answer
    assert response.debug.llm_provider == "local"
    assert response.debug.llm_model == "mistral"
    assert response.debug.embedding_provider == "local"
    assert response.debug.embedding_model_name == "bge-m3"
    assert response.debug.latency_ms >= 0
    assert retrieval_pipeline.last_workspace_id == "workspace-trace"


@pytest.mark.asyncio
async def test_agentic_rag_trace_is_omitted_when_debug_false() -> None:
    """debug=false 时保持原有轻量响应结构。"""

    orchestrator = AgenticRAGOrchestrator(
        llm_client=TraceLLMClient(),
        retrieval_pipeline=TraceRetrievalPipeline(),
        reranker_client=TraceRerankerClient(),
    )

    response = await orchestrator.query(
        AgenticRAGRequest(
            query="Phase 8 做了什么？",
            collection_name="trace_collection",
            top_k=1,
            debug=False,
        ),
        workspace_id="workspace-trace",
    )

    assert response.debug is None
    assert response.provider == "local"
    assert response.model == "mistral"
