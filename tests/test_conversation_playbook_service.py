"""Phase 40 playbook service execution tests."""

from __future__ import annotations

import pytest

from app.conversation.services import ConversationPlaybookService, ConversationService


@pytest.mark.asyncio
async def test_content_generation_playbook_completes(session, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    async def fake_run(self, agent_input):  # type: ignore[no-untyped-def]
        return {
            "title": "Playbook title",
            "description": agent_input["topic"],
            "tags": ["playbook"],
            "cta": "Review before publishing.",
            "raw_response": "mock",
        }

    monkeypatch.setattr("app.conversation.services.conversation_service.ContentAgent.run", fake_run)
    conversation = ConversationService(session)
    thread = await conversation.create_thread(workspace_id="workspace-playbook-content", user_id="user", title="Content")
    service = ConversationPlaybookService(session)

    result = await service.run_playbook_by_name(
        workspace_id="workspace-playbook-content",
        user_id="user",
        thread=thread,
        playbook_name="content_generation",
        input_payload={"topic": "AI operations", "platform": "short_video", "style": "concise"},
        mode="auto_safe",
        message_id=None,
        source_message="Generate content",
    )

    assert result.success is True
    assert result.run.status == "completed"
    assert result.approval is None
    assert result.output["steps"][0]["status"] == "completed"


@pytest.mark.asyncio
async def test_browser_playbook_waits_for_approval(session, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    called = False

    class ShouldNotRunRegistry:
        async def execute_tool(self, *args, **kwargs):  # type: ignore[no-untyped-def]
            nonlocal called
            called = True
            raise AssertionError("browser tool should not run before approval")

    monkeypatch.setattr(
        "app.conversation.services.conversation_service.build_default_tool_registry",
        lambda: ShouldNotRunRegistry(),
    )
    conversation = ConversationService(session)
    thread = await conversation.create_thread(workspace_id="workspace-playbook-approval", user_id="user", title="Browser")
    service = ConversationPlaybookService(session)

    result = await service.run_playbook_by_name(
        workspace_id="workspace-playbook-approval",
        user_id="user",
        thread=thread,
        playbook_name="browser_screenshot_report",
        input_payload={"url": "https://example.com"},
        mode="review_first",
        message_id=None,
        source_message="Open example and screenshot",
    )

    assert called is False
    assert result.success is True
    assert result.run.status == "waiting_approval"
    assert result.approval is not None
    assert result.approval.approval_status == "pending"
