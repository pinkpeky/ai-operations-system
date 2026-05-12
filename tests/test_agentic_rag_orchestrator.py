"""Agentic RAG Orchestrator 测试模块。

验证 query -> retrieval -> prompt assembly -> llm_client -> response 的单一编排流程。
"""

from types import SimpleNamespace

import pytest

from app.rag.agentic_orchestrator import AgenticRAGOrchestrator
from app.rag.vector_store import VectorSearchResult
from app.reranker.providers.base import RerankedChunk
from app.schemas.agentic_rag import AgenticRAGRequest
from app.schemas.llm import LLMRequest, LLMResponse


class FakeLLMClient:
    """LLM Client 替身，记录收到的 Prompt。"""

    def __init__(self) -> None:
        self.last_request: LLMRequest | None = None

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """返回固定 LLM 响应。"""

        self.last_request = request
        return LLMResponse(
            provider="mock",
            model="mock-llm",
            content="fake agentic rag answer",
        )


class FakeRetrievalPipeline:
    """Retrieval Pipeline 替身。"""

    def __init__(self) -> None:
        self.vector_store = SimpleNamespace(collection_name="agentic_test_collection")
        self.embedding_client = SimpleNamespace(
            provider=SimpleNamespace(provider_name="mock", model="mock-embedding-model")
        )
        self.last_query: str | None = None
        self.last_top_k: int | None = None
        self.last_workspace_id: str | None = None

    async def search(
        self,
        query: str,
        top_k: int = 5,
        source_id: str | None = None,
        workspace_id: str | None = None,
        status: str = "active",
    ) -> list[VectorSearchResult]:
        """返回固定检索结果。"""

        self.last_query = query
        self.last_top_k = top_k
        self.last_workspace_id = workspace_id
        return [
            VectorSearchResult(
                id="aaaaaaaa-aaaa-4aaa-aaaa-aaaaaaaaaaaa",
                text="Phase 3.5 added normalized scores and RAG debug APIs.",
                similarity_score=0.88,
                raw_score=0.8799,
                metadata={"source_id": "phase35"},
                chunk_index=0,
            )
        ]


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
        """返回固定 rerank 分数。"""

        self.last_top_n = top_n
        return [
            RerankedChunk(
                id=chunk.id,
                text=chunk.text,
                similarity_score=chunk.similarity_score,
                raw_score=chunk.raw_score,
                rerank_score=0.66,
                metadata=chunk.metadata,
                chunk_index=chunk.chunk_index,
            )
            for chunk in chunks[: top_n or len(chunks)]
        ]


@pytest.mark.asyncio
async def test_agentic_rag_orchestrator_runs_retrieval_and_llm() -> None:
    """知识型 query 应触发 retrieval，并把上下文组装进 LLM Prompt。"""

    llm_client = FakeLLMClient()
    retrieval_pipeline = FakeRetrievalPipeline()
    orchestrator = AgenticRAGOrchestrator(
        llm_client=llm_client,
        retrieval_pipeline=retrieval_pipeline,
        reranker_client=FakeRerankerClient(),
    )

    request = AgenticRAGRequest(
        query="Phase 3.5 做了哪些 RAG 增强？",
        collection_name="agentic_test_collection",
        top_k=3,
        debug=True,
    )
    response = await orchestrator.query(request, workspace_id="workspace-trace")

    assert response.answer == "fake agentic rag answer"
    assert response.used_retrieval is True
    assert response.provider == "mock"
    assert response.model == "mock-llm"
    assert len(response.retrieved_chunks) == 1
    assert response.debug is not None
    assert response.debug.query == request.query
    assert response.debug.workspace_id == "workspace-trace"
    assert response.debug.retrieved_count == 1
    assert response.debug.retrieved_chunks[0].text == "Phase 3.5 added normalized scores and RAG debug APIs."
    assert response.debug.similarity_scores == [0.88]
    assert response.debug.reranker_provider == "mock"
    assert response.debug.reranker_model == "mock-reranker"
    assert response.debug.rerank_scores == [0.66]
    assert len(response.debug.retrieval_before_rerank) == 1
    assert len(response.debug.retrieval_after_rerank) == 1
    assert response.debug.retrieval_after_rerank[0].rerank_score is not None
    assert response.debug.final_prompt == llm_client.last_request.user_prompt
    assert response.debug.final_answer == "fake agentic rag answer"
    assert response.debug.llm_provider == "mock"
    assert response.debug.llm_model == "mock-llm"
    assert response.debug.embedding_provider == "mock"
    assert response.debug.embedding_model_name == "mock-embedding-model"
    assert response.debug.latency_ms >= 0
    assert retrieval_pipeline.last_query == "Phase 3.5 做了哪些 RAG 增强？"
    assert retrieval_pipeline.last_top_k == 20
    assert retrieval_pipeline.last_workspace_id == "workspace-trace"
    assert llm_client.last_request is not None
    assert "检索上下文" in llm_client.last_request.user_prompt
    assert "normalized scores" in llm_client.last_request.user_prompt


@pytest.mark.asyncio
async def test_agentic_rag_orchestrator_can_skip_retrieval_for_ping() -> None:
    """简单 ping 不需要检索，但仍会调用 LLM 返回答案。"""

    llm_client = FakeLLMClient()
    retrieval_pipeline = FakeRetrievalPipeline()
    orchestrator = AgenticRAGOrchestrator(
        llm_client=llm_client,
        retrieval_pipeline=retrieval_pipeline,
        reranker_client=FakeRerankerClient(),
    )

    response = await orchestrator.query(
        AgenticRAGRequest(
            query="ping",
            collection_name="agentic_test_collection",
            debug=True,
        )
    )

    assert response.used_retrieval is False
    assert response.retrieved_chunks == []
    assert retrieval_pipeline.last_query is None
    assert response.debug is not None
    assert response.debug.retrieved_count == 0
    assert llm_client.last_request is not None
    assert "请直接简洁回答" in llm_client.last_request.user_prompt
