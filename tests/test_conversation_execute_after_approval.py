"""Phase 39 execute_after_approval tests."""

from __future__ import annotations

import pytest

from app.conversation.services import ConversationApprovalService, ConversationService
from app.tools.base import ToolExecutionRecord


class FakeBrowserRegistry:
    async def execute_tool(self, tool_name, tool_input, context, agent_name):  # type: ignore[no-untyped-def]
        action = tool_input["action_type"]
        output = {"action_type": action}
        if action == "create_session":
            output["session"] = {"id": "22222222-2222-2222-2222-222222222222"}
        if action == "screenshot":
            output["screenshot_path"] = "storage/browser_screenshots/approval.png"
        if action == "get_page":
            output["title"] = "Example Domain"
        return ToolExecutionRecord(
            tool_name=tool_name,
            tool_input=tool_input,
            tool_output=output,
            success=True,
            error=None,
            latency_ms=1,
        )


@pytest.mark.asyncio
async def test_conversation_execute_after_approval_runs_once(session, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(
        "app.conversation.services.conversation_service.build_default_tool_registry",
        lambda: FakeBrowserRegistry(),
    )
    service = ConversationService(session)
    thread = await service.create_thread(workspace_id="workspace-execute-approval", user_id="user", title="Approval")

    pending = await service.run_conversation_turn(
        workspace_id="workspace-execute-approval",
        user_id="user",
        thread_id=thread.id,
        run_input={"input": {"message": "open https://example.com and screenshot"}, "mode": "review_first"},
    )
    assert pending.approval_id is not None

    with pytest.raises(ValueError, match="must be approved"):
        await service.run_conversation_turn(
            workspace_id="workspace-execute-approval",
            user_id="user",
            thread_id=thread.id,
            run_input={"input": {"approval_id": str(pending.approval_id)}, "mode": "execute_after_approval"},
        )

    await ConversationApprovalService(session).approve(
        workspace_id="workspace-execute-approval",
        approval_id=pending.approval_id,
        approved_by="user",
    )
    executed = await service.run_conversation_turn(
        workspace_id="workspace-execute-approval",
        user_id="user",
        thread_id=thread.id,
        run_input={"input": {"approval_id": str(pending.approval_id)}, "mode": "execute_after_approval"},
    )
    assert executed.success is True
    assert executed.approval_status == "executed"
    assert executed.result_metadata["runtime_session_id"] == "22222222-2222-2222-2222-222222222222"

    with pytest.raises(ValueError, match="already been executed"):
        await service.run_conversation_turn(
            workspace_id="workspace-execute-approval",
            user_id="user",
            thread_id=thread.id,
            run_input={"input": {"approval_id": str(pending.approval_id)}, "mode": "execute_after_approval"},
        )
