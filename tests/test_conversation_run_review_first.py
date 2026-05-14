"""Phase 39 review_first run mode tests."""

from __future__ import annotations

import pytest

from app.conversation.services import ConversationService


@pytest.mark.asyncio
async def test_conversation_review_first_creates_approval_without_execution(session, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    called = False

    class ShouldNotRunRegistry:
        async def execute_tool(self, *args, **kwargs):  # type: ignore[no-untyped-def]
            nonlocal called
            called = True
            raise AssertionError("tool should not run before approval")

    monkeypatch.setattr(
        "app.conversation.services.conversation_service.build_default_tool_registry",
        lambda: ShouldNotRunRegistry(),
    )
    service = ConversationService(session)
    thread = await service.create_thread(workspace_id="workspace-review-first", user_id="user", title="Review")

    result = await service.run_conversation_turn(
        workspace_id="workspace-review-first",
        user_id="user",
        thread_id=thread.id,
        run_input={"input": {"message": "open https://example.com and screenshot"}, "mode": "review_first"},
    )

    assert result.success is True
    assert called is False
    assert result.approval_required is True
    assert result.approval_status == "pending"
    assert result.risk_level == "medium"
    event_types = {event.event_type for event in result.events}
    assert {"approval_created", "execution_blocked_pending_approval", "assistant_response"} <= event_types


@pytest.mark.asyncio
async def test_conversation_auto_safe_executes_low_risk_content(session, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    async def fake_run(self, agent_input):  # type: ignore[no-untyped-def]
        return {
            "title": "Safe content",
            "description": agent_input["topic"],
            "tags": ["safe"],
            "cta": "Review before publishing.",
            "raw_response": "mock",
        }

    monkeypatch.setattr("app.conversation.services.conversation_service.ContentAgent.run", fake_run)
    service = ConversationService(session)
    thread = await service.create_thread(workspace_id="workspace-auto-safe", user_id="user", title="Auto safe")

    result = await service.run_conversation_turn(
        workspace_id="workspace-auto-safe",
        user_id="user",
        thread_id=thread.id,
        run_input={"input": {"message": "generate a short video content title"}},
    )

    assert result.success is True
    assert result.approval_required is False
    assert result.risk_level == "low"
    assert "Safe content" in result.summary
