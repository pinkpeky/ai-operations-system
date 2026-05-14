"""Phase 39 conversation approval model tests."""

from __future__ import annotations

import pytest

from app.conversation.services import ConversationApprovalService, ConversationService
from app.conversation.tool_router import ConversationRouteDecision


@pytest.mark.asyncio
async def test_conversation_approvals_are_workspace_isolated(session) -> None:  # type: ignore[no-untyped-def]
    service = ConversationService(session)
    thread = await service.create_thread(workspace_id="workspace-a", user_id="user-a", title="A")
    message = await service.append_message(
        workspace_id="workspace-a",
        thread_id=thread.id,
        role="user",
        content="open example",
    )
    approval_service = ConversationApprovalService(session)
    approval = await approval_service.create_approval(
        workspace_id="workspace-a",
        thread_id=thread.id,
        message_id=message.id,
        decision=ConversationRouteDecision(
            route_name="browser",
            selected_tool="browser_tool",
            reason="test",
            confidence=0.9,
            tool_input={"action_type": "navigate", "target": "https://example.com"},
            route_type="tool",
        ),
        risk_level="medium",
        source_message=message.content,
    )
    await session.commit()

    assert approval.proposed_action == "browser_tool:navigate"
    assert await approval_service.get_approval(workspace_id="workspace-b", approval_id=approval.id) is None
    assert await approval_service.get_approval(workspace_id="workspace-a", approval_id=approval.id) is not None
