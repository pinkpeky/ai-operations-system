"""Planning repository。

Repository 只负责数据读写，业务执行留给 PlanningService。
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import PlanStatus, PlanStepStatus
from app.models.planning import Plan, PlanReview, PlanStep


class PlanRepository:
    """Plan / PlanStep / PlanReview 数据访问层。"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_plan(
        self,
        *,
        workspace_id: str,
        session_id: UUID | None,
        root_goal: str,
        planner_agent: str,
        metadata: dict[str, Any] | None = None,
    ) -> Plan:
        """创建 plan。"""

        plan = Plan(
            workspace_id=workspace_id,
            session_id=session_id,
            root_goal=root_goal,
            planner_agent=planner_agent,
            status=PlanStatus.PENDING.value,
            plan_metadata=metadata or {},
        )
        self.session.add(plan)
        await self.session.flush()
        return plan

    async def get_plan(self, *, plan_id: UUID, workspace_id: str) -> Plan | None:
        """按 workspace 查询 plan。"""

        result = await self.session.execute(select(Plan).where(Plan.id == plan_id, Plan.workspace_id == workspace_id))
        return result.scalar_one_or_none()

    async def list_plans(self, *, workspace_id: str, status: str | None = None, limit: int = 100) -> list[Plan]:
        """列出当前 workspace 下的 plans。"""

        statement = select(Plan).where(Plan.workspace_id == workspace_id)
        if status is not None:
            statement = statement.where(Plan.status == status)
        result = await self.session.execute(statement.order_by(Plan.created_at.desc()).limit(limit))
        return list(result.scalars().all())

    async def update_plan_status(self, plan: Plan, status: str) -> Plan:
        """更新 plan 状态。"""

        plan.status = status
        await self.session.flush()
        return plan

    async def create_step(
        self,
        *,
        workspace_id: str,
        plan_id: UUID,
        step_order: int,
        agent_name: str | None,
        tool_name: str | None,
        title: str,
        description: str,
        input_payload: dict[str, Any] | None = None,
    ) -> PlanStep:
        """创建单个 plan step。"""

        step = PlanStep(
            workspace_id=workspace_id,
            plan_id=plan_id,
            step_order=step_order,
            agent_name=agent_name,
            tool_name=tool_name,
            title=title,
            description=description,
            input_payload=input_payload or {},
            status=PlanStepStatus.PENDING.value,
        )
        self.session.add(step)
        await self.session.flush()
        return step

    async def list_steps(self, *, plan_id: UUID, workspace_id: str) -> list[PlanStep]:
        """按顺序列出 plan steps。"""

        result = await self.session.execute(
            select(PlanStep)
            .where(PlanStep.plan_id == plan_id, PlanStep.workspace_id == workspace_id)
            .order_by(PlanStep.step_order.asc())
        )
        return list(result.scalars().all())

    async def get_step(self, *, step_id: UUID, workspace_id: str) -> PlanStep | None:
        """按 workspace 查询单个 step。"""

        result = await self.session.execute(
            select(PlanStep).where(PlanStep.id == step_id, PlanStep.workspace_id == workspace_id)
        )
        return result.scalar_one_or_none()

    async def mark_step_running(self, step: PlanStep) -> PlanStep:
        """标记 step 正在执行。"""

        step.status = PlanStepStatus.RUNNING.value
        step.started_at = datetime.now(timezone.utc)
        step.error = None
        await self.session.flush()
        return step

    async def complete_step(self, step: PlanStep, *, output: dict[str, Any], duration_ms: int) -> PlanStep:
        """标记 step 成功。"""

        step.status = PlanStepStatus.COMPLETED.value
        step.output_payload = output
        step.error = None
        step.completed_at = datetime.now(timezone.utc)
        step.duration_ms = duration_ms
        await self.session.flush()
        return step

    async def fail_step(self, step: PlanStep, *, error: str, duration_ms: int) -> PlanStep:
        """标记 step 失败。"""

        step.status = PlanStepStatus.FAILED.value
        step.error = error
        step.completed_at = datetime.now(timezone.utc)
        step.duration_ms = duration_ms
        await self.session.flush()
        return step

    async def skip_step(self, step: PlanStep, *, reason: str | None = None) -> PlanStep:
        """跳过 step。"""

        step.status = PlanStepStatus.SKIPPED.value
        step.error = reason
        step.completed_at = datetime.now(timezone.utc)
        await self.session.flush()
        return step

    async def retry_step(self, step: PlanStep) -> PlanStep:
        """重置 step，允许再次执行。"""

        step.status = PlanStepStatus.PENDING.value
        step.error = None
        step.started_at = None
        step.completed_at = None
        step.duration_ms = None
        await self.session.flush()
        return step

    async def create_review(
        self,
        *,
        workspace_id: str,
        plan_id: UUID,
        reviewer_agent: str,
        review_result: str,
        score: float | None,
        notes: str | None,
    ) -> PlanReview:
        """创建 plan review。"""

        review = PlanReview(
            workspace_id=workspace_id,
            plan_id=plan_id,
            reviewer_agent=reviewer_agent,
            review_result=review_result,
            score=score,
            notes=notes,
        )
        self.session.add(review)
        await self.session.flush()
        return review

    async def list_reviews(self, *, plan_id: UUID, workspace_id: str) -> list[PlanReview]:
        """列出 plan reviews。"""

        result = await self.session.execute(
            select(PlanReview)
            .where(PlanReview.plan_id == plan_id, PlanReview.workspace_id == workspace_id)
            .order_by(PlanReview.created_at.asc())
        )
        return list(result.scalars().all())
