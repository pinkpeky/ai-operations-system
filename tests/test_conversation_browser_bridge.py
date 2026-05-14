"""Phase 38 browser bridge tests."""

from __future__ import annotations

import pytest

from app.conversation.services import ConversationApprovalService, ConversationService
from app.tools.base import ToolExecutionRecord


class FakeBrowserRegistry:
    async def execute_tool(self, tool_name, tool_input, context, agent_name):  # type: ignore[no-untyped-def]
        assert tool_name == "browser_tool"
        action = tool_input["action_type"]
        output = {"action_type": action}
        if action == "create_session":
            output["session"] = {"id": "11111111-1111-1111-1111-111111111111"}
        if action == "screenshot":
            output["session"] = {"runtime_metadata": {"last_screenshot_path": "storage/browser_screenshots/test.png"}}
            output["screenshot_path"] = "storage/browser_screenshots/test.png"
        if action == "get_page":
            output["title"] = "Example Domain"
            output["content"] = "Example Domain"
        return ToolExecutionRecord(
            tool_name=tool_name,
            tool_input=tool_input,
            tool_output=output,
            success=True,
            error=None,
            latency_ms=1,
        )


@pytest.mark.asyncio
async def test_conversation_browser_bridge_composes_runtime_actions(session, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(
        "app.conversation.services.conversation_service.build_default_tool_registry",
        lambda: FakeBrowserRegistry(),
    )
    service = ConversationService(session)
    thread = await service.create_thread(workspace_id="workspace-browser", user_id="user-browser", title="Browser")

    result = await service.run_conversation_turn(
        workspace_id="workspace-browser",
        user_id="user-browser",
        thread_id=thread.id,
        run_input={"input": {"message": "请打开 https://example.com 并截图"}},
    )

    assert result.success is True
    assert result.route_name == "browser"
    assert result.selected_tool == "browser_tool"
    assert result.approval_required is True
    assert result.risk_level == "medium"
    assert result.approval_id is not None

    await ConversationApprovalService(session).approve(
        workspace_id="workspace-browser",
        approval_id=result.approval_id,
        approved_by="user-browser",
        reviewer_notes="Example.com screenshot is safe.",
    )
    executed = await service.run_conversation_turn(
        workspace_id="workspace-browser",
        user_id="user-browser",
        thread_id=thread.id,
        run_input={"input": {"approval_id": str(result.approval_id)}, "mode": "execute_after_approval"},
    )
    assert executed.success is True
    assert executed.result_metadata["runtime_session_id"] == "11111111-1111-1111-1111-111111111111"
    event_types = {event.event_type for event in result.events}
    assert {"route_selected", "approval_created", "execution_blocked_pending_approval"} <= event_types
    executed_event_types = {event.event_type for event in executed.events}
    assert {"tool_execution_started", "tool_execution_completed", "worker_action_started", "approval_executed"} <= executed_event_types
