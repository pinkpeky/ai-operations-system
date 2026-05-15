"""Conversation thread service tests."""

import pytest

from app.conversation.services import ConversationService
from app.models.enums import ConversationThreadStatus


@pytest.mark.asyncio
async def test_conversation_thread_create_list_get_archive(session) -> None:  # type: ignore[no-untyped-def]
    """ConversationService 应支持 thread 生命周期基础操作。"""

    service = ConversationService(session)
    thread = await service.create_thread(
        workspace_id="workspace-conversation",
        user_id="user-conversation",
        title="Phase 33 thread",
        metadata={"phase": "33"},
    )

    assert thread.workspace_id == "workspace-conversation"
    assert thread.status == ConversationThreadStatus.ACTIVE.value

    fetched = await service.get_thread(workspace_id="workspace-conversation", thread_id=thread.id)
    assert fetched is not None
    assert fetched.id == thread.id

    threads = await service.list_threads(workspace_id="workspace-conversation")
    assert [item.id for item in threads] == [thread.id]

    archived = await service.archive_thread(workspace_id="workspace-conversation", thread_id=thread.id)
    assert archived.status == ConversationThreadStatus.ARCHIVED.value
