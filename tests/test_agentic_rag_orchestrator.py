"""Agentic RAG Orchestrator 测试模块。

验证 query -> retrieval -> prompt assembly -> llm_client -> response 的单一编排流程。
"""

from types import SimpleNamespace

import pytest

from app.rag.agentic_orchestrator import AgenticRAGOrchestrator
from app.rag.vector_store import VectorSearchResult
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
        self.last_query: str | None = None
        self.last_top_k: int | None = None

    async def search(self, query: str, top_k: int = 5) -> list[VectorSearchResult]:
        """返回固定检索结果。"""

        self.last_query = query
        self.last_top_k = top_k
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


@pytest.mark.asyncio
async def test_agentic_rag_orchestrator_runs_retrieval_and_llm() -> None:
    """知识型 query 应触发 retrieval，并把上下文组装进 LLM Prompt。"""

    llm_client = FakeLLMClient()
    retrieval_pipeline = FakeRetrievalPipeline()
    orchestrator = AgenticRAGOrchestrator(
        llm_client=llm_client,
        retrieval_pipeline=retrieval_pipeline,
    )

    response = await orchestrator.query(
        AgenticRAGRequest(
            query="Phase 3.5 做了哪些 RAG 增强？",
            collection_name="agentic_test_collection",
            top_k=3,
            debug=True,
        )
    )

    assert response.answer == "fake agentic rag answer"
    assert response.used_retrieval is True
    assert response.provider == "mock"
    assert response.model == "mock-llm"
    assert len(response.retrieved_chunks) == 1
    assert response.debug is not None
    assert response.debug.retrieved_count == 1
    assert retrieval_pipeline.last_query == "Phase 3.5 做了哪些 RAG 增强？"
    assert retrieval_pipeline.last_top_k == 3
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
