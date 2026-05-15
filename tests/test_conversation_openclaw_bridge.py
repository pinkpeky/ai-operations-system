"""Phase 38 OpenClaw mock bridge tests."""

from __future__ import annotations

import pytest

from app.conversation.services import ConversationApprovalService, ConversationService
from app.tools.base import ToolExecutionRecord


class FakeOpenClawRegistry:
    async def execute_tool(self, tool_name, tool_input, context, agent_name):  # type: ignore[no-untyped-def]
        assert tool_name == "openclaw_tool"
        assert tool_input["openclaw_action_type"] == "mock_inspect"
        return ToolExecutionRecord(
            tool_name=tool_name,
            tool_input=tool_input,
            tool_output={"mock": True, "provider": "mock", "success": True},
            success=True,
            error=None,
            latency_ms=1,
        )


@pytest.mark.asyncio
async def test_conversation_openclaw_bridge_uses_mock_tool(session, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(
        "app.conversation.services.conversation_service.build_default_tool_registry",
        lambda: FakeOpenClawRegistry(),
    )
    service = ConversationService(session)
    thread = await service.create_thread(workspace_id="workspace-openclaw", user_id="user-openclaw", title="OpenClaw")

    result = await service.run_conversation_turn(
        workspace_id="workspace-openclaw",
        user_id="user-openclaw",
        thread_id=thread.id,
        run_input={"input": {"message": "请用 OpenClaw 检查设备状态"}},
    )

    assert result.success is True
    assert result.route_name == "openclaw"
    assert result.selected_tool == "openclaw_tool"
    assert result.approval_required is True
    assert result.risk_level == "medium"
    assert result.approval_id is not None

    await ConversationApprovalService(session).approve(
        workspace_id="workspace-openclaw",
        approval_id=result.approval_id,
        approved_by="user-openclaw",
        reviewer_notes="OpenClaw mock inspect is safe.",
    )
    executed = await service.run_conversation_turn(
        workspace_id="workspace-openclaw",
        user_id="user-openclaw",
        thread_id=thread.id,
        run_input={"input": {"approval_id": str(result.approval_id)}, "mode": "execute_after_approval"},
    )
    assert executed.success is True
    assert "mock=True" in executed.summary
    assert executed.approval_status == "executed"
