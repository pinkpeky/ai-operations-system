"""Multi-Agent run 测试。"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.multi_agent.services import MultiAgentService


@pytest.mark.asyncio
async def test_multi_agent_run_is_workspace_scoped(session: AsyncSession) -> None:
    """run 查询必须按 workspace 隔离。"""

    service = MultiAgentService(session)
    run = await service.create_run(
        workspace_id="workspace-ma-a",
        user_id="user-a",
        session_id=None,
        root_agent="content_planner",
        run_input={"topic": "AI 自动化运营"},
    )

    own_run = await service.get_run(run_id=run.id, workspace_id="workspace-ma-a")
    hidden_run = await service.get_run(run_id=run.id, workspace_id="workspace-ma-b")
    own_runs = await service.list_runs(workspace_id="workspace-ma-a")

    assert own_run is not None
    assert hidden_run is None
    assert [item.id for item in own_runs] == [run.id]
    assert own_run.status == "pending"


@pytest.mark.asyncio
async def test_execute_single_runtime_agent_uses_tool_registry(session: AsyncSession) -> None:
    """runtime_agent 应通过现有 ToolRegistry 返回运行配置。"""

    service = MultiAgentService(session)
    output = await service.execute_single_agent(
        agent_name="runtime_agent",
        agent_input={},
        workspace_id="workspace-runtime-agent",
        user_id="user-runtime",
    )

    assert output["tool_result"]["tool_name"] == "current_runtime_tool"
    assert output["tool_result"]["success"] is True
    assert output["tool_result"]["tool_output"]["runtime"]["LLM_PROVIDER"] == "mock"

