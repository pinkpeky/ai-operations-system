"""Plan 执行测试。"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.planning.services import PlanningService


@pytest.mark.asyncio
async def test_execute_plan_runs_steps_and_creates_review(session: AsyncSession) -> None:
    """执行 plan 后 steps 应完成，并生成 review。"""

    service = PlanningService(session)
    plan = await service.create_plan(
        workspace_id="workspace-plan-exec",
        session_id=None,
        root_goal="生成 AI 自动化运营 TikTok 内容",
        metadata={"query": "ping", "platform": "tiktok", "style": "专业简洁"},
    )

    result = await service.execute_plan(plan=plan, user_id="user-plan")
    steps = await service.list_steps(plan_id=plan.id, workspace_id="workspace-plan-exec")
    reviews = await service.list_reviews(plan_id=plan.id, workspace_id="workspace-plan-exec")

    assert result["status"] == "completed"
    assert plan.status == "completed"
    assert all(step.status == "completed" for step in steps)
    assert all(step.duration_ms is not None for step in steps)
    assert reviews[0].review_result == "approved"
    assert result["memory_trace"][0]["operation"] == "planning_load_memory"
