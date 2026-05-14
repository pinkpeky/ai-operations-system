"""Phase 38 generic tool execution bridge tests."""

from __future__ import annotations

import pytest

from app.conversation.services import ConversationService
from app.tools.base import ToolExecutionRecord


class FakeTaskRegistry:
    async def execute_tool(self, tool_name, tool_input, context, agent_name):  # type: ignore[no-untyped-def]
        assert tool_name == "create_task_tool"
        assert tool_input["task_type"] == "content_generation"
        return ToolExecutionRecord(
            tool_name=tool_name,
            tool_input=tool_input,
            tool_output={"task": {"id": "task-001", "status": "pending"}},
            success=True,
            error=None,
            latency_ms=1,
        )


@pytest.mark.asyncio
async def test_conversation_create_task_tool_bridge(session, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(
        "app.conversation.services.conversation_service.build_default_tool_registry",
        lambda: FakeTaskRegistry(),
    )
    service = ConversationService(session)
    thread = await service.create_thread(workspace_id="workspace-task", user_id="user-task", title="Task")

    result = await service.run_conversation_turn(
        workspace_id="workspace-task",
        user_id="user-task",
        thread_id=thread.id,
        run_input={"input": {"message": "请创建任务后台执行内容生成。"}},
    )

    assert result.success is True
    assert result.route_name == "create_task"
    assert result.selected_tool == "create_task_tool"
    assert "task-001" in result.summary
    event_types = {event.event_type for event in result.events}
    assert {"tool_execution_started", "tool_execution_completed"} <= event_types
