"""Phase 40 playbook executor tests."""

from __future__ import annotations

import pytest

from app.conversation.services import ConversationPlaybookService, ConversationService
from app.tools.base import ToolExecutionRecord


class FakeBrowserRegistry:
    async def execute_tool(self, tool_name, tool_input, context, agent_name):  # type: ignore[no-untyped-def]
        output = {"action_type": tool_input["action_type"]}
        if tool_input["action_type"] == "create_session":
            output["session"] = {"id": "44444444-4444-4444-4444-444444444444"}
        if tool_input["action_type"] == "get_page":
            output["title"] = "Example Domain"
        if tool_input["action_type"] == "screenshot":
            output["screenshot_path"] = "storage/browser_screenshots/example.png"
        return ToolExecutionRecord(
            tool_name=tool_name,
            tool_input=tool_input,
            tool_output=output,
            success=True,
            error=None,
            latency_ms=1,
        )


@pytest.mark.asyncio
async def test_approved_browser_playbook_resumes_and_completes(session, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(
        "app.conversation.services.conversation_service.build_default_tool_registry",
        lambda: FakeBrowserRegistry(),
    )
    conversation = ConversationService(session)
    thread = await conversation.create_thread(workspace_id="workspace-playbook-resume", user_id="user", title="Resume")
    service = ConversationPlaybookService(session)
    result = await service.run_playbook_by_name(
        workspace_id="workspace-playbook-resume",
        user_id="user",
        thread=thread,
        playbook_name="browser_screenshot_report",
        input_payload={"url": "https://example.com"},
        mode="review_first",
        message_id=None,
        source_message="Open example and screenshot",
    )
    assert result.approval is not None
    approval = await service.approvals.approve(
        workspace_id="workspace-playbook-resume",
        approval_id=result.approval.id,
        approved_by="user",
        reviewer_notes="safe",
    )

    resumed = await service.resume_after_approval(
        workspace_id="workspace-playbook-resume",
        user_id="user",
        approval=approval,
        source_message="Open example and screenshot",
    )

    assert resumed.run.status == "completed"
    assert resumed.success is True
    assert resumed.run.output_payload["steps"][0]["status"] == "completed"
