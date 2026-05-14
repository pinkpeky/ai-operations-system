"""Conversation message tests."""

import pytest

from app.conversation.services import ConversationService


@pytest.mark.asyncio
async def test_conversation_message_append_and_list(session) -> None:  # type: ignore[no-untyped-def]
    """线程消息应写入 thread_id，并产生 message_received 事件。"""

    service = ConversationService(session)
    thread = await service.create_thread(
        workspace_id="workspace-message",
        user_id="user-message",
        title="Message Thread",
    )

    message = await service.append_message(
        workspace_id="workspace-message",
        thread_id=thread.id,
        role="user",
        content="请生成一条内容。",
        metadata={"source": "test"},
    )

    assert message.session_id is None
    assert message.thread_id == thread.id

    messages = await service.list_messages(workspace_id="workspace-message", thread_id=thread.id)
    assert len(messages) == 1
    assert messages[0].content == "请生成一条内容。"

    events = await service.list_events(workspace_id="workspace-message", thread_id=thread.id)
    assert "message_received" in {event.event_type for event in events}
