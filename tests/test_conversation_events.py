"""Conversation event feed tests."""

import pytest

from app.conversation.services import ConversationService


@pytest.mark.asyncio
async def test_conversation_event_append_and_poll(session) -> None:  # type: ignore[no-untyped-def]
    """事件 feed 当前使用普通 polling 查询，不伪装 WebSocket/SSE。"""

    service = ConversationService(session)
    thread = await service.create_thread(
        workspace_id="workspace-events",
        user_id="user-events",
        title="Events Thread",
    )

    event = await service.append_event(
        workspace_id="workspace-events",
        thread_id=thread.id,
        event_type="planning_started",
        message="planning started",
        payload={"planner": "simple_planner"},
    )

    assert event.event_type == "planning_started"
    events = await service.list_events(workspace_id="workspace-events", thread_id=thread.id)
    assert any(item.payload.get("planner") == "simple_planner" for item in events)
