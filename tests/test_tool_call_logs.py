"""工具调用日志测试。"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.tool_call_repository import ToolCallLogRepository


@pytest.mark.asyncio
async def test_tool_call_logs_are_workspace_scoped(session: AsyncSession) -> None:
    """工具调用日志查询必须按 workspace 隔离。"""

    repository = ToolCallLogRepository(session)
    await repository.create_log(
        workspace_id="workspace-a",
        agent_name="AgentA",
        tool_name="current_runtime_tool",
        tool_input={"include_document": False},
        tool_output={"runtime": {"LLM_PROVIDER": "mock"}},
        success=True,
        error=None,
        latency_ms=5,
    )
    await repository.create_log(
        workspace_id="workspace-b",
        agent_name="AgentB",
        tool_name="current_runtime_tool",
        tool_input={},
        tool_output={},
        success=False,
        error="boom",
        latency_ms=1,
    )
    await session.commit()

    logs = await repository.list_logs(workspace_id="workspace-a")

    assert len(logs) == 1
    assert logs[0].workspace_id == "workspace-a"
    assert logs[0].success is True
