"""Agent memory 集成测试模块。"""

from types import SimpleNamespace
from typing import Any

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base_agent import BaseAgent
from app.memory.services import MemoryExecutionContext, MemoryService
from app.rag.agentic_orchestrator import AgenticRAGOrchestrator
from app.rag.vector_store import VectorSearchResult
from app.reranker.providers.base import RerankedChunk
from app.schemas.agentic_rag import AgenticRAGRequest
from app.schemas.llm import LLMRequest, LLMResponse


class FakeLLMClient:
    """记录 prompt 的 LLM 测试替身。"""

    def __init__(self) -> None:
        self.last_request: LLMRequest | None = None

    async def generate(self, request: LLMRequest) -> LLMResponse:
        self.last_request = request
        return LLMResponse(provider="mock", model="mock-llm", content="memory answer")


class MemoryDemoAgent(BaseAgent):
    """用于验证 BaseAgent memory hook 的简单 Agent。"""

    agent_name = "MemoryDemoAgent"
    agent_type = "memory_demo"

    def validate_input(self, agent_input: dict[str, Any]) -> dict[str, Any]:
        return {"value": str(agent_input["value"])}

    def build_prompt(self, validated_input: dict[str, Any]) -> str:
        return f"Value: {validated_input['value']}"

    def format_output(self, validated_input: dict[str, Any], llm_response: LLMResponse) -> dict[str, Any]:
        return {"value": validated_input["value"], "raw_response": llm_response.content}


class FakeRetrievalPipeline:
    """Agentic RAG memory trace 测试用 dense-only 检索替身。"""

    def __init__(self) -> None:
        self.vector_store = SimpleNamespace(collection_name="memory_trace_collection")
        self.embedding_client = SimpleNamespace(
            provider=SimpleNamespace(provider_name="mock", model="mock-embedding-model")
        )

    async def search(
        self,
        query: str,
        top_k: int = 5,
        source_id: str | None = None,
        workspace_id: str | None = None,
        status: str = "active",
    ) -> list[VectorSearchResult]:
        return [
            VectorSearchResult(
                id="cccccccc-cccc-4ccc-8ccc-cccccccccccc",
                text="Memory trace 会把最近消息和长期记忆放入 prompt。",
                similarity_score=0.8,
                raw_score=0.8,
                metadata={"workspace_id": workspace_id},
                chunk_index=0,
            )
        ]


class FakeRerankerClient:
    """Reranker 测试替身。"""

    def __init__(self) -> None:
        self.provider = SimpleNamespace(provider_name="mock", model="mock-reranker")

    async def rerank(
        self,
        *,
        query: str,
        chunks: list[VectorSearchResult],
        top_n: int | None = None,
    ) -> list[RerankedChunk]:
        return [
            RerankedChunk(
                id=chunk.id,
                text=chunk.text,
                similarity_score=chunk.similarity_score,
                raw_score=chunk.raw_score,
                rerank_score=0.7,
                metadata=chunk.metadata,
                chunk_index=chunk.chunk_index,
            )
            for chunk in chunks[: top_n or len(chunks)]
        ]


@pytest.mark.asyncio
async def test_base_agent_loads_and_saves_memory(session: AsyncSession) -> None:
    """BaseAgent 应能加载最近消息和 memory，并按需保存新 memory。"""

    service = MemoryService(session)
    conversation = await service.create_session(
        workspace_id="workspace-agent-memory",
        user_id="user-agent-memory",
        title="Agent Memory Session",
    )
    await service.append_message(
        workspace_id="workspace-agent-memory",
        session_id=conversation.id,
        role="user",
        content="请记住我关注 memory trace。",
    )
    await service.save_memory(
        workspace_id="workspace-agent-memory",
        agent_name="MemoryDemoAgent",
        memory_type="long_term",
        content="用户关注 memory trace 和 prompt assembly。",
    )
    context = MemoryExecutionContext(
        service=service,
        workspace_id="workspace-agent-memory",
        user_id="user-agent-memory",
        session_id=conversation.id,
        agent_name="MemoryDemoAgent",
    )
    llm_client = FakeLLMClient()
    agent = MemoryDemoAgent(llm_client=llm_client)

    output = await agent.run(
        {
            "value": "memory trace",
            "memory_context": context,
            "save_memory": True,
            "memory_to_save": {
                "memory_type": "short_term",
                "content": "本轮验证 BaseAgent memory hook。",
                "importance_score": 0.6,
            },
        }
    )

    assert output["raw_response"] == "memory answer"
    assert output["memory_trace"][0]["operation"] == "load_memory"
    assert output["memory_trace"][0]["recent_messages_count"] == 1
    assert output["memory_trace"][0]["retrieved_memories_count"] == 1
    assert output["memory_trace"][1]["operation"] == "save_memory"
    assert llm_client.last_request is not None
    assert "memory trace" in llm_client.last_request.user_prompt
    assert "prompt assembly" in llm_client.last_request.user_prompt


@pytest.mark.asyncio
async def test_agentic_rag_debug_includes_memory_trace(session: AsyncSession) -> None:
    """Agentic RAG debug=true 时应返回 recent messages、retrieved memories 和 memory_trace。"""

    service = MemoryService(session)
    conversation = await service.create_session(
        workspace_id="workspace-agentic-memory",
        user_id="user-agentic-memory",
        title="Agentic Memory Session",
    )
    await service.append_message(
        workspace_id="workspace-agentic-memory",
        session_id=conversation.id,
        role="user",
        content="上一轮讨论了 Agentic RAG memory trace。",
    )
    await service.save_memory(
        workspace_id="workspace-agentic-memory",
        agent_name="AgenticRAGOrchestrator",
        memory_type="long_term",
        content="用户需要在 debug trace 中观察 memory retrieval。",
    )
    llm_client = FakeLLMClient()
    orchestrator = AgenticRAGOrchestrator(
        llm_client=llm_client,
        retrieval_pipeline=FakeRetrievalPipeline(),
        reranker_client=FakeRerankerClient(),
        memory_service=service,
    )

    response = await orchestrator.query(
        AgenticRAGRequest(
            query="memory trace 如何工作？",
            collection_name="memory_trace_collection",
            debug=True,
            session_id=str(conversation.id),
        ),
        workspace_id="workspace-agentic-memory",
    )

    assert response.debug is not None
    assert response.debug.session_id == str(conversation.id)
    assert response.debug.recent_messages_count == 1
    assert response.debug.retrieved_memories_count == 1
    assert response.debug.memory_trace[0].success is True
    assert "上一轮讨论了 Agentic RAG memory trace" in response.debug.final_prompt
    assert "memory retrieval" in response.debug.final_prompt

