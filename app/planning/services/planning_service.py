"""Planning Service。

将 rule-based plan、step 执行、Agent/Tool 调用和 review 串起来。当前不做自主规划、ReAct 或递归循环。
"""

from __future__ import annotations

import logging
import time
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.memory.services import MemoryService
from app.models.enums import PlanStatus, PlanStepStatus
from app.models.planning import Plan, PlanReview, PlanStep
from app.multi_agent.services import MultiAgentService
from app.multi_agent.services.agent_registry import AgentRegistry, build_default_agent_registry
from app.planning.repositories import PlanRepository
from app.planning.services.simple_planner_agent import PlannedStep, SimplePlannerAgent
from app.tools.base import ToolExecutionContext
from app.tools.registry import ToolRegistry, build_default_tool_registry

logger = logging.getLogger(__name__)


class PlanningService:
    """Agent Planning 基础服务。"""

    def __init__(
        self,
        session: AsyncSession,
        *,
        settings: Settings | None = None,
        agent_registry: AgentRegistry | None = None,
        tool_registry: ToolRegistry | None = None,
        planner_agent: SimplePlannerAgent | None = None,
    ) -> None:
        self.session = session
        self.settings = settings or get_settings()
        self.repository = PlanRepository(session)
        self.agent_registry = agent_registry or build_default_agent_registry()
        self.tool_registry = tool_registry or build_default_tool_registry()
        self.planner_agent = planner_agent or SimplePlannerAgent()
        self.multi_agent_service = MultiAgentService(
            session,
            settings=self.settings,
            agent_registry=self.agent_registry,
            tool_registry=self.tool_registry,
        )

    async def create_plan(
        self,
        *,
        workspace_id: str,
        session_id: UUID | None,
        root_goal: str,
        planner_agent: str = "simple_planner",
        metadata: dict[str, Any] | None = None,
        auto_create_steps: bool = True,
    ) -> Plan:
        """创建 plan，并可自动使用 SimplePlannerAgent 生成 steps。"""

        if planner_agent != self.planner_agent.agent_name:
            raise ValueError("Only simple_planner is supported in Phase 16")
        plan = await self.repository.create_plan(
            workspace_id=workspace_id,
            session_id=session_id,
            root_goal=root_goal,
            planner_agent=planner_agent,
            metadata=metadata,
        )
        if auto_create_steps:
            await self.repository.update_plan_status(plan, PlanStatus.PLANNING.value)
            planned_steps = self.planner_agent.plan(root_goal=root_goal, metadata=metadata)
            await self.create_steps(plan=plan, steps=planned_steps)
            await self.repository.update_plan_status(plan, PlanStatus.PENDING.value)
        await self.session.commit()
        await self.session.refresh(plan)
        logger.info("Plan created", extra={"plan_id": str(plan.id), "workspace_id": workspace_id})
        return plan

    async def create_steps(self, *, plan: Plan, steps: list[PlannedStep]) -> list[PlanStep]:
        """批量创建 plan steps。"""

        created: list[PlanStep] = []
        for step in sorted(steps, key=lambda item: item.step_order):
            if not step.agent_name and not step.tool_name:
                raise ValueError("Each step must target either agent_name or tool_name")
            if step.agent_name and step.tool_name:
                raise ValueError("A step cannot target both agent_name and tool_name")
            if step.agent_name:
                self.agent_registry.get_agent(step.agent_name)
            if step.tool_name:
                self.tool_registry.get_tool(step.tool_name, workspace_id=plan.workspace_id)
            created.append(
                await self.repository.create_step(
                    workspace_id=plan.workspace_id,
                    plan_id=plan.id,
                    step_order=step.step_order,
                    agent_name=step.agent_name,
                    tool_name=step.tool_name,
                    title=step.title,
                    description=step.description,
                    input_payload=step.input_payload,
                )
            )
        await self.session.flush()
        return created

    async def execute_plan(
        self,
        *,
        plan: Plan,
        user_id: str | None = None,
        execution_input: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """执行 plan 中的 pending steps，并在结束后生成 review。"""

        if plan.status == PlanStatus.CANCELLED.value:
            raise ValueError("Plan is cancelled")

        started_at = time.perf_counter()
        await self.repository.update_plan_status(plan, PlanStatus.EXECUTING.value)
        await self.session.commit()

        memory_trace = await self._load_memory_trace(plan=plan)
        step_outputs: dict[str, Any] = {}
        failed_step: PlanStep | None = None

        try:
            steps = await self.repository.list_steps(plan_id=plan.id, workspace_id=plan.workspace_id)
            for step in steps:
                if step.status == PlanStepStatus.SKIPPED.value:
                    step_outputs[str(step.step_order)] = {"skipped": True, "reason": step.error}
                    continue
                if step.status not in {PlanStepStatus.PENDING.value, PlanStepStatus.FAILED.value}:
                    continue
                output = await self.execute_step(
                    plan=plan,
                    step=step,
                    user_id=user_id,
                    previous_outputs=step_outputs,
                    memory_trace=memory_trace,
                    execution_input=execution_input,
                    retry=step.status == PlanStepStatus.FAILED.value,
                )
                step_outputs[str(step.step_order)] = output

            review = await self.review_plan(plan=plan, reviewer_agent="review_agent")
            final_status = PlanStatus.COMPLETED.value if review.review_result == "approved" else PlanStatus.FAILED.value
            await self.repository.update_plan_status(plan, final_status)
            await self.session.commit()
            await self.session.refresh(plan)
            duration_ms = int((time.perf_counter() - started_at) * 1000)
            logger.info(
                "Plan execution finished",
                extra={
                    "workspace_id": plan.workspace_id,
                    "plan_id": str(plan.id),
                    "plan_status": final_status,
                    "duration_ms": duration_ms,
                },
            )
            return {
                "plan_id": str(plan.id),
                "status": final_status,
                "step_outputs": step_outputs,
                "review_id": str(review.id),
                "review_result": review.review_result,
                "duration_ms": duration_ms,
                "memory_trace": memory_trace,
            }
        except Exception:
            failed_step = await self._first_failed_step(plan)
            await self.repository.update_plan_status(plan, PlanStatus.FAILED.value)
            await self.session.commit()
            logger.exception(
                "Plan execution failed",
                extra={
                    "workspace_id": plan.workspace_id,
                    "plan_id": str(plan.id),
                    "failed_step_id": str(failed_step.id) if failed_step else None,
                },
            )
            raise

    async def execute_step(
        self,
        *,
        plan: Plan,
        step: PlanStep,
        user_id: str | None = None,
        previous_outputs: dict[str, Any] | None = None,
        memory_trace: list[dict[str, Any]] | None = None,
        execution_input: dict[str, Any] | None = None,
        retry: bool = False,
    ) -> dict[str, Any]:
        """执行一个 plan step。"""

        if step.status == PlanStepStatus.SKIPPED.value:
            return {"skipped": True, "reason": step.error}
        if retry:
            await self.repository.retry_step(step)
        started_at = time.perf_counter()
        await self.repository.mark_step_running(step)
        await self.session.commit()

        try:
            step_input = self._build_step_input(
                plan=plan,
                step=step,
                previous_outputs=previous_outputs or {},
                memory_trace=memory_trace or [],
                execution_input=execution_input or {},
            )
            if step.tool_name:
                output = await self._execute_tool_step(
                    plan=plan,
                    step=step,
                    tool_name=step.tool_name,
                    tool_input=step_input,
                    user_id=user_id,
                )
            elif step.agent_name:
                output = await self._execute_agent_step(
                    plan=plan,
                    step=step,
                    agent_name=step.agent_name,
                    agent_input=step_input,
                    user_id=user_id,
                )
            else:
                raise ValueError("Plan step has no target agent/tool")
            duration_ms = int((time.perf_counter() - started_at) * 1000)
            await self.repository.complete_step(step, output=output, duration_ms=duration_ms)
            await self.session.commit()
            logger.info(
                "Plan step completed",
                extra={
                    "workspace_id": plan.workspace_id,
                    "plan_id": str(plan.id),
                    "step_id": str(step.id),
                    "step_status": step.status,
                    "duration_ms": duration_ms,
                },
            )
            return output
        except Exception as exc:
            duration_ms = int((time.perf_counter() - started_at) * 1000)
            await self.repository.fail_step(step, error=str(exc), duration_ms=duration_ms)
            await self.session.commit()
            logger.exception(
                "Plan step failed",
                extra={
                    "workspace_id": plan.workspace_id,
                    "plan_id": str(plan.id),
                    "step_id": str(step.id),
                    "step_error": str(exc),
                    "duration_ms": duration_ms,
                },
            )
            raise

    async def review_plan(self, *, plan: Plan, reviewer_agent: str = "review_agent") -> PlanReview:
        """对 plan 执行结果做轻量 review。"""

        steps = await self.repository.list_steps(plan_id=plan.id, workspace_id=plan.workspace_id)
        failed = [step for step in steps if step.status == PlanStepStatus.FAILED.value]
        completed_or_skipped = [
            step for step in steps if step.status in {PlanStepStatus.COMPLETED.value, PlanStepStatus.SKIPPED.value}
        ]
        approved = not failed and len(completed_or_skipped) == len(steps)
        review = await self.repository.create_review(
            workspace_id=plan.workspace_id,
            plan_id=plan.id,
            reviewer_agent=reviewer_agent,
            review_result="approved" if approved else "needs_revision",
            score=1.0 if approved else 0.4,
            notes=(
                "Phase 16 rule-based review approved all completed/skipped steps."
                if approved
                else f"Phase 16 review found failed steps: {[str(step.id) for step in failed]}"
            ),
        )
        await self.session.flush()
        return review

    async def cancel_plan(self, *, plan: Plan) -> Plan:
        """取消 plan，并跳过未开始的 steps。"""

        await self.repository.update_plan_status(plan, PlanStatus.CANCELLED.value)
        steps = await self.repository.list_steps(plan_id=plan.id, workspace_id=plan.workspace_id)
        for step in steps:
            if step.status == PlanStepStatus.PENDING.value:
                await self.repository.skip_step(step, reason="Plan cancelled")
        await self.session.commit()
        await self.session.refresh(plan)
        return plan

    async def skip_step(self, *, step: PlanStep, reason: str | None = None) -> PlanStep:
        """跳过 step。"""

        await self.repository.skip_step(step, reason=reason)
        await self.session.commit()
        await self.session.refresh(step)
        return step

    async def retry_step(self, *, step: PlanStep) -> PlanStep:
        """重置 step 为 pending。"""

        await self.repository.retry_step(step)
        await self.session.commit()
        await self.session.refresh(step)
        return step

    async def get_plan(self, *, plan_id: UUID, workspace_id: str) -> Plan | None:
        """查询 plan。"""

        return await self.repository.get_plan(plan_id=plan_id, workspace_id=workspace_id)

    async def list_plans(self, *, workspace_id: str, status: str | None = None, limit: int = 100) -> list[Plan]:
        """列出 plans。"""

        return await self.repository.list_plans(workspace_id=workspace_id, status=status, limit=limit)

    async def list_steps(self, *, plan_id: UUID, workspace_id: str) -> list[PlanStep]:
        """列出 plan steps。"""

        return await self.repository.list_steps(plan_id=plan_id, workspace_id=workspace_id)

    async def list_reviews(self, *, plan_id: UUID, workspace_id: str) -> list[PlanReview]:
        """列出 plan reviews。"""

        return await self.repository.list_reviews(plan_id=plan_id, workspace_id=workspace_id)

    async def _execute_agent_step(
        self,
        *,
        plan: Plan,
        step: PlanStep,
        agent_name: str,
        agent_input: dict[str, Any],
        user_id: str | None,
    ) -> dict[str, Any]:
        """通过 AgentRegistry / MultiAgentService 执行 agent step。"""

        return await self.multi_agent_service.execute_single_agent(
            agent_name=agent_name,
            agent_input=agent_input,
            workspace_id=plan.workspace_id,
            user_id=user_id,
            session_id=plan.session_id,
            current_plan_id=plan.id,
            current_step_id=step.id,
        )

    async def _execute_tool_step(
        self,
        *,
        plan: Plan,
        step: PlanStep,
        tool_name: str,
        tool_input: dict[str, Any],
        user_id: str | None,
    ) -> dict[str, Any]:
        """通过 ToolRegistry 执行 tool step。"""

        record = await self.tool_registry.execute_tool(
            tool_name=tool_name,
            tool_input=tool_input,
            context=ToolExecutionContext(
                workspace_id=plan.workspace_id,
                user_id=user_id,
                session=self.session,
                settings=self.settings,
                agent_name=plan.planner_agent,
                task_id=str(step.id),
            ),
            agent_name=plan.planner_agent,
        )
        output = record.model_dump(mode="json")
        if not record.success:
            raise RuntimeError(record.error or f"Tool step failed: {tool_name}")
        return output

    def _build_step_input(
        self,
        *,
        plan: Plan,
        step: PlanStep,
        previous_outputs: dict[str, Any],
        memory_trace: list[dict[str, Any]],
        execution_input: dict[str, Any],
    ) -> dict[str, Any]:
        """组装 step 执行上下文。"""

        payload = {**plan.plan_metadata, **execution_input, **step.input_payload}
        payload.update(
            {
                "root_goal": plan.root_goal,
                "workspace_id": plan.workspace_id,
                "session_id": plan.session_id,
                "current_plan_id": plan.id,
                "current_step_id": step.id,
                "plan_context": {
                    "plan_id": str(plan.id),
                    "step_id": str(step.id),
                    "step_order": step.step_order,
                    "planner_agent": plan.planner_agent,
                },
                "previous_steps": previous_outputs,
                "memory_trace": memory_trace,
            }
        )
        if step.agent_name == "content_agent" and "1" in previous_outputs:
            payload["rag_context"] = previous_outputs["1"]
        if step.agent_name == "review_agent":
            payload["content"] = previous_outputs.get("2") or previous_outputs.get("content_agent") or {}
            payload["rag"] = previous_outputs.get("1") or {}
        return payload

    async def _load_memory_trace(self, *, plan: Plan) -> list[dict[str, Any]]:
        """读取轻量 memory context 并返回 trace，不把 memory 规划复杂化。"""

        started_at = time.perf_counter()
        memory_service = MemoryService(self.session)
        recent_count = 0
        memory_count = 0
        try:
            if plan.session_id is not None:
                recent = await memory_service.get_recent_messages(
                    workspace_id=plan.workspace_id,
                    session_id=plan.session_id,
                    limit=5,
                )
                recent_count = len(recent)
            memories = await memory_service.search_memory(
                workspace_id=plan.workspace_id,
                query=plan.root_goal,
                agent_name=None,
                limit=5,
            )
            memory_count = len(memories)
            return [
                {
                    "operation": "planning_load_memory",
                    "session_id": str(plan.session_id) if plan.session_id else None,
                    "recent_messages_count": recent_count,
                    "retrieved_memories_count": memory_count,
                    "latency_ms": int((time.perf_counter() - started_at) * 1000),
                    "success": True,
                    "error": None,
                }
            ]
        except Exception as exc:
            return [
                {
                    "operation": "planning_load_memory",
                    "session_id": str(plan.session_id) if plan.session_id else None,
                    "recent_messages_count": recent_count,
                    "retrieved_memories_count": memory_count,
                    "latency_ms": int((time.perf_counter() - started_at) * 1000),
                    "success": False,
                    "error": str(exc),
                }
            ]

    async def _first_failed_step(self, plan: Plan) -> PlanStep | None:
        """返回第一个失败 step，用于日志。"""

        steps = await self.repository.list_steps(plan_id=plan.id, workspace_id=plan.workspace_id)
        for step in steps:
            if step.status == PlanStepStatus.FAILED.value:
                return step
        return None
