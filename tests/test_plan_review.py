"""Plan review 测试。"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.planning.services import PlanningService


@pytest.mark.asyncio
async def test_plan_review_detects_failed_step(session: AsyncSession) -> None:
    """review 应能识别失败 step。"""

    service = PlanningService(session)
    plan = await service.create_plan(
        workspace_id="workspace-plan-review",
        session_id=None,
        root_goal="生成 AI 自动化运营 TikTok 内容",
        metadata={"query": "ping"},
    )
    steps = await service.list_steps(plan_id=plan.id, workspace_id="workspace-plan-review")
    await service.repository.fail_step(steps[0], error="forced failure", duration_ms=1)
    review = await service.review_plan(plan=plan)

    assert review.review_result == "needs_revision"
    assert review.score == 0.4
    assert "failed steps" in (review.notes or "")
