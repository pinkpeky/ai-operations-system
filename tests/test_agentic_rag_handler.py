"""AgenticRAGHandler 测试模块。

验证 agentic_rag_query payload 可以被转换为 AgenticRAGRequest，并调用编排器返回标准执行结果。
"""

import pytest

from app.schemas.agentic_rag import AgenticRAGRequest, AgenticRAGResponse
from app.schemas.rag import RetrievedChunk
from app.workers.handlers.agentic_rag_handler import AGENTIC_RAG_TASK_TYPE, AgenticRAGHandler


class FakeOrchestrator:
    """Agentic RAG 编排器替身。"""

    def __init__(self) -> None:
        self.last_request: AgenticRAGRequest | None = None

    async def query(self, request: AgenticRAGRequest) -> AgenticRAGResponse:
        """返回固定 Agentic RAG 响应。"""

        self.last_request = request
        return AgenticRAGResponse(
            answer="handler fake answer",
            used_retrieval=True,
            retrieved_chunks=[
                RetrievedChunk(
                    id="aaaaaaaa-aaaa-4aaa-aaaa-aaaaaaaaaaaa",
                    text="handler chunk",
                    similarity_score=0.8,
                    raw_score=0.8,
                    metadata={"source_id": "handler-source"},
                    chunk_index=0,
                )
            ],
            provider="mock",
            model="mock-llm",
            debug=None,
        )


@pytest.mark.asyncio
async def test_agentic_rag_handler_returns_execution_result() -> None:
    """AgenticRAGHandler 应返回标准执行结果。"""

    fake_orchestrator = FakeOrchestrator()
    handler = AgenticRAGHandler(orchestrator_factory=lambda request: fake_orchestrator)  # type: ignore[arg-type]

    result = await handler.handle(
        {
            "query": "Phase 3.5 做了哪些增强？",
            "collection_name": "phase4_agentic_demo",
            "top_k": 3,
            "debug": True,
        }
    )

    assert handler.task_type == AGENTIC_RAG_TASK_TYPE
    assert result.success is True
    assert result.data["answer"] == "handler fake answer"
    assert result.data["provider"] == "mock"
    assert fake_orchestrator.last_request is not None
    assert fake_orchestrator.last_request.top_k == 3


@pytest.mark.asyncio
async def test_agentic_rag_handler_reports_invalid_payload() -> None:
    """payload 缺少 query 时应返回失败结果。"""

    handler = AgenticRAGHandler(orchestrator_factory=lambda request: FakeOrchestrator())  # type: ignore[arg-type]

    result = await handler.handle({"top_k": 3})

    assert result.success is False
    assert result.error is not None
