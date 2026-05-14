"""Phase 40 ConversationService playbook approval integration tests."""

from __future__ import annotations

import pytest

from app.conversation.services import ConversationApprovalService, ConversationService
from app.tools.base import ToolExecutionRecord


class FakeBrowserRegistry:
    async def execute_tool(self, tool_name, tool_input, context, agent_name):  # type: ignore[no-untyped-def]
        output = {"action_type": tool_input["action_type"]}
        if tool_input["action_type"] == "create_session":
            output["session"] = {"id": "55555555-5555-5555-5555-555555555555"}
        return ToolExecutionRecord(
            tool_name=tool_name,
            tool_input=tool_input,
            tool_output=output,
            success=True,
            error=None,
            latency_ms=1,
        )


@pytest.mark.asyncio
async def test_conversation_run_with_playbook_creates_approval_then_executes(monkeypatch, session) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(
        "app.conversation.services.conversation_service.build_default_tool_registry",
        lambda: FakeBrowserRegistry(),
    )
    service = ConversationService(session)
    thread = await service.create_thread(workspace_id="workspace-conv-playbook", user_id="user", title="Playbook")

    first = await service.run_conversation_turn(
        workspace_id="workspace-conv-playbook",
        user_id="user",
        thread_id=thread.id,
        run_input={
            "input": {"message": "open https://example.com and screenshot"},
            "playbook_name": "browser_screenshot_report",
            "mode": "review_first",
        },
    )

    assert first.approval_required is True
    assert first.playbook_name == "browser_screenshot_report"
    assert first.playbook_status == "waiting_approval"
    assert first.approval_id is not None

    await ConversationApprovalService(session).approve(
        workspace_id="workspace-conv-playbook",
        approval_id=first.approval_id,
        approved_by="user",
        reviewer_notes="safe",
    )
    second = await service.run_conversation_turn(
        workspace_id="workspace-conv-playbook",
        user_id="user",
        thread_id=thread.id,
        run_input={"input": {"approval_id": str(first.approval_id)}, "mode": "execute_after_approval"},
    )

    assert second.playbook_status == "completed"
    assert second.success is True
    assert second.approval_status == "executed"
    assert "Playbook `browser_screenshot_report` completed" in second.summary
