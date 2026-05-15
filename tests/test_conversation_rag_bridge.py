"""Phase 38 RAG bridge tests."""

from __future__ import annotations

import pytest

from app.conversation.services import ConversationService
from app.tools.base import ToolExecutionRecord


class FakeRagRegistry:
    async def execute_tool(self, tool_name, tool_input, context, agent_name):  # type: ignore[no-untyped-def]
        assert tool_name == "rag_search_tool"
        assert tool_input["collection_name"] == "phase35a_docs"
        return ToolExecutionRecord(
            tool_name=tool_name,
            tool_input=tool_input,
            tool_output={"chunks": [{"text": "Phase 35A timeline"}]},
            success=True,
            error=None,
            latency_ms=1,
        )


@pytest.mark.asyncio
async def test_conversation_rag_bridge_requires_collection_name(session) -> None:  # type: ignore[no-untyped-def]
    service = ConversationService(session)
    thread = await service.create_thread(workspace_id="workspace-rag-missing", user_id="user-rag", title="RAG")

    result = await service.run_conversation_turn(
        workspace_id="workspace-rag-missing",
        user_id="user-rag",
        thread_id=thread.id,
        run_input={"input": {"message": "检索知识库里关于 Phase 35A 的内容"}},
    )

    assert result.success is False
    assert result.selected_tool == "rag_search_tool"
    assert "collection_name" in result.summary


@pytest.mark.asyncio
async def test_conversation_rag_bridge_executes_search_tool(session, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(
        "app.conversation.services.conversation_service.build_default_tool_registry",
        lambda: FakeRagRegistry(),
    )
    service = ConversationService(session)
    thread = await service.create_thread(
        workspace_id="workspace-rag",
        user_id="user-rag",
        title="RAG",
        metadata={"collection_name": "phase35a_docs"},
    )

    result = await service.run_conversation_turn(
        workspace_id="workspace-rag",
        user_id="user-rag",
        thread_id=thread.id,
        run_input={"input": {"message": "检索知识库里关于 Phase 35A 的内容"}},
    )

    assert result.success is True
    assert "1 retrieved chunk" in result.summary
