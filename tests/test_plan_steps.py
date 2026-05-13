"""Plan step 状态测试。"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.planning.services import PlanningService


@pytest.mark.asyncio
async def test_plan_step_skip_and_retry(session: AsyncSession) -> None:
    """step 应支持 skip 与 retry。"""

    service = PlanningService(session)
    plan = await service.create_plan(
        workspace_id="workspace-plan-steps",
        session_id=None,
        root_goal="生成 AI 自动化运营 TikTok 内容",
        metadata={"query": "ping"},
    )
    steps = await service.list_steps(plan_id=plan.id, workspace_id="workspace-plan-steps")
    first = steps[0]

    skipped = await service.skip_step(step=first, reason="manual skip")
    assert skipped.status == "skipped"
    assert skipped.error == "manual skip"

    retried = await service.retry_step(step=first)
    assert retried.status == "pending"
    assert retried.error is None
