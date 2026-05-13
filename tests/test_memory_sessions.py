"""Memory session 测试模块。

验证 conversation_sessions 的创建、查询和 workspace 隔离。
"""

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.memory.services import MemoryService
from app.models.memory import MemoryOperationLog


@pytest.mark.asyncio
async def test_memory_sessions_are_workspace_scoped(session: AsyncSession) -> None:
    """会话查询必须限定在当前 workspace，不能跨 workspace 泄露。"""

    service = MemoryService(session)
    created = await service.create_session(
        workspace_id="workspace-memory-a",
        user_id="user-a",
        title="Phase 14 Session",
        metadata={"phase": "14"},
    )

    own_sessions = await service.list_sessions(workspace_id="workspace-memory-a")
    other_sessions = await service.list_sessions(workspace_id="workspace-memory-b")
    own_session = await service.get_session(workspace_id="workspace-memory-a", session_id=created.id)
    hidden_session = await service.get_session(workspace_id="workspace-memory-b", session_id=created.id)

    assert len(own_sessions) == 1
    assert own_sessions[0].id == created.id
    assert other_sessions == []
    assert own_session is not None
    assert own_session.workspace_id == "workspace-memory-a"
    assert hidden_session is None

    result = await session.execute(
        select(MemoryOperationLog).where(MemoryOperationLog.workspace_id == "workspace-memory-a")
    )
    operations = {item.operation for item in result.scalars().all()}
    assert {"create_session", "list_sessions", "get_session"}.issubset(operations)

