"""Plan 创建测试。"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.planning.services import PlanningService


@pytest.mark.asyncio
async def test_create_plan_generates_steps_and_is_workspace_scoped(session: AsyncSession) -> None:
    """创建 plan 时默认生成 steps，并保持 workspace 隔离。"""

    service = PlanningService(session)
    plan = await service.create_plan(
        workspace_id="workspace-plan-a",
        session_id=None,
        root_goal="生成 AI 自动化运营 TikTok 内容",
        metadata={"query": "ping", "platform": "tiktok"},
    )

    own_plan = await service.get_plan(plan_id=plan.id, workspace_id="workspace-plan-a")
    hidden_plan = await service.get_plan(plan_id=plan.id, workspace_id="workspace-plan-b")
    steps = await service.list_steps(plan_id=plan.id, workspace_id="workspace-plan-a")

    assert own_plan is not None
    assert hidden_plan is None
    assert own_plan.status == "pending"
    assert len(steps) == 3
    assert [step.agent_name for step in steps] == ["rag_agent", "content_agent", "review_agent"]
