"""Planning API Schema。"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.planning import Plan, PlanReview, PlanStep


class PlanCreateRequest(BaseModel):
    """创建 plan 请求。"""

    root_goal: str = Field(min_length=1, max_length=4000)
    session_id: UUID | None = Field(default=None)
    planner_agent: str = Field(default="simple_planner")
    metadata: dict[str, Any] = Field(default_factory=dict)
    auto_create_steps: bool = Field(default=True)


class PlanExecuteRequest(BaseModel):
    """执行 plan 请求。"""

    input: dict[str, Any] | None = Field(default=None)


class PlanResponse(BaseModel):
    """Plan 响应。"""

    id: UUID
    workspace_id: str
    session_id: UUID | None
    root_goal: str
    planner_agent: str
    status: str
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, plan: Plan) -> "PlanResponse":
        """从 ORM 构造响应。"""

        return cls(
            id=plan.id,
            workspace_id=plan.workspace_id,
            session_id=plan.session_id,
            root_goal=plan.root_goal,
            planner_agent=plan.planner_agent,
            status=plan.status,
            metadata=plan.plan_metadata,
            created_at=plan.created_at,
            updated_at=plan.updated_at,
        )


class PlanListResponse(BaseModel):
    """Plan 列表响应。"""

    items: list[PlanResponse]


class PlanStepResponse(BaseModel):
    """Plan step 响应。"""

    id: UUID
    workspace_id: str
    plan_id: UUID
    step_order: int
    agent_name: str | None
    tool_name: str | None
    title: str
    description: str
    input_payload: dict[str, Any]
    output_payload: dict[str, Any] | None
    status: str
    error: str | None
    started_at: datetime | None
    completed_at: datetime | None
    duration_ms: int | None
    created_at: datetime

    @classmethod
    def from_model(cls, step: PlanStep) -> "PlanStepResponse":
        """从 ORM 构造响应。"""

        return cls(
            id=step.id,
            workspace_id=step.workspace_id,
            plan_id=step.plan_id,
            step_order=step.step_order,
            agent_name=step.agent_name,
            tool_name=step.tool_name,
            title=step.title,
            description=step.description,
            input_payload=step.input_payload,
            output_payload=step.output_payload,
            status=step.status,
            error=step.error,
            started_at=step.started_at,
            completed_at=step.completed_at,
            duration_ms=step.duration_ms,
            created_at=step.created_at,
        )


class PlanStepListResponse(BaseModel):
    """Plan step 列表响应。"""

    plan_id: UUID
    items: list[PlanStepResponse]


class PlanReviewResponse(BaseModel):
    """Plan review 响应。"""

    id: UUID
    workspace_id: str
    plan_id: UUID
    reviewer_agent: str
    review_result: str
    score: float | None
    notes: str | None
    created_at: datetime

    @classmethod
    def from_model(cls, review: PlanReview) -> "PlanReviewResponse":
        """从 ORM 构造响应。"""

        return cls(
            id=review.id,
            workspace_id=review.workspace_id,
            plan_id=review.plan_id,
            reviewer_agent=review.reviewer_agent,
            review_result=review.review_result,
            score=review.score,
            notes=review.notes,
            created_at=review.created_at,
        )


class PlanReviewListResponse(BaseModel):
    """Plan review 列表响应。"""

    plan_id: UUID
    items: list[PlanReviewResponse]


class PlanExecutionResponse(BaseModel):
    """Plan 执行响应。"""

    plan: PlanResponse
    success: bool
    status: str
    step_outputs: dict[str, Any]
    review_result: str | None = None
    duration_ms: int
    memory_trace: list[dict[str, Any]] = Field(default_factory=list)
    steps: list[PlanStepResponse]
    reviews: list[PlanReviewResponse]
