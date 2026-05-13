"""Conversation message 测试模块。

验证 conversation_messages 写入、角色校验和最近消息读取。
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.memory.services import MemoryService


@pytest.mark.asyncio
async def test_memory_messages_append_and_list_in_workspace(session: AsyncSession) -> None:
    """消息追加后应可按 session 正序读取，并保留 metadata。"""

    service = MemoryService(session)
    conversation = await service.create_session(
        workspace_id="workspace-message",
        user_id="user-message",
        title="Message Session",
    )

    first = await service.append_message(
        workspace_id="workspace-message",
        session_id=conversation.id,
        role="user",
        content="我正在验证 Phase 14 memory messages",
        metadata={"turn": 1},
    )
    second = await service.append_message(
        workspace_id="workspace-message",
        session_id=conversation.id,
        role="assistant",
        content="Phase 14 memory message 已记录",
        metadata={"turn": 2},
    )

    messages = await service.list_messages(
        workspace_id="workspace-message",
        session_id=conversation.id,
        limit=10,
    )
    recent = await service.get_recent_messages(
        workspace_id="workspace-message",
        session_id=conversation.id,
        limit=2,
    )

    assert [message.id for message in messages] == [first.id, second.id]
    assert messages[0].message_metadata == {"turn": 1}
    assert messages[0].token_count > 0
    assert len(recent) == 2
    assert {message.role for message in recent} == {"user", "assistant"}


@pytest.mark.asyncio
async def test_memory_message_rejects_invalid_role(session: AsyncSession) -> None:
    """role 只允许 system/user/assistant/tool。"""

    service = MemoryService(session)
    conversation = await service.create_session(
        workspace_id="workspace-invalid-role",
        user_id=None,
        title="Invalid Role Session",
    )

    with pytest.raises(ValueError, match="role must be system"):
        await service.append_message(
            workspace_id="workspace-invalid-role",
            session_id=conversation.id,
            role="bad-role",
            content="invalid",
        )

