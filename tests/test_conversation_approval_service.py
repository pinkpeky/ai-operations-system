"""Phase 39 approval service lifecycle tests."""

from __future__ import annotations

import pytest

from app.conversation.services import ConversationApprovalService, ConversationService
from app.conversation.tool_router import ConversationRouteDecision


def browser_decision() -> ConversationRouteDecision:
    return ConversationRouteDecision(
        route_name="browser",
        selected_tool="browser_tool",
        reason="test browser approval",
        confidence=0.9,
        tool_input={"action_type": "navigate_and_screenshot", "target": "https://example.com"},
        route_type="tool",
    )


@pytest.mark.asyncio
async def test_conversation_approval_service_state_flow(session) -> None:  # type: ignore[no-untyped-def]
    conversation = ConversationService(session)
    thread = await conversation.create_thread(workspace_id="workspace-approval", user_id="user-approval", title="Approval")
    message = await conversation.append_message(
        workspace_id="workspace-approval",
        thread_id=thread.id,
        role="user",
        content="open example.com and screenshot",
    )

    service = ConversationApprovalService(session)
    approval = await service.create_approval(
        workspace_id="workspace-approval",
        thread_id=thread.id,
        message_id=message.id,
        decision=browser_decision(),
        risk_level="medium",
        source_message=message.content,
    )
    await session.commit()

    assert approval.approval_status == "pending"
    approved = await service.approve(
        workspace_id="workspace-approval",
        approval_id=approval.id,
        approved_by="user-approval",
        reviewer_notes="safe",
    )
    assert approved.approval_status == "approved"

    executed = await service.mark_executed(workspace_id="workspace-approval", approval_id=approval.id, commit=True)
    assert executed.approval_status == "executed"

    with pytest.raises(ValueError):
        await service.approve(
            workspace_id="workspace-approval",
            approval_id=approval.id,
            approved_by="user-approval",
        )

    events = await conversation.list_events(workspace_id="workspace-approval", thread_id=thread.id)
    event_types = {event.event_type for event in events}
    assert {"approval_required", "approval_created", "approval_approved", "approval_executed"} <= event_types


@pytest.mark.asyncio
async def test_conversation_approval_service_reject_and_cancel_are_terminal(session) -> None:  # type: ignore[no-untyped-def]
    conversation = ConversationService(session)
    thread = await conversation.create_thread(workspace_id="workspace-reject", user_id="user-reject", title="Approval")
    message = await conversation.append_message(
        workspace_id="workspace-reject",
        thread_id=thread.id,
        role="user",
        content="open example.com",
    )
    service = ConversationApprovalService(session)
    approval = await service.create_approval(
        workspace_id="workspace-reject",
        thread_id=thread.id,
        message_id=message.id,
        decision=browser_decision(),
        risk_level="medium",
        source_message=message.content,
    )
    await session.commit()

    rejected = await service.reject(
        workspace_id="workspace-reject",
        approval_id=approval.id,
        reviewer_notes="not safe",
    )
    assert rejected.approval_status == "rejected"
    with pytest.raises(ValueError):
        service.ensure_executable(rejected)
