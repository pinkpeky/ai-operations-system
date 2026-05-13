"""Planning API 路由。"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.errors import AppError
from app.core.workspace_context import WorkspaceContext, get_workspace_context
from app.db.postgres import get_session as get_db_session
from app.planning.services import PlanningService
from app.schemas.planning import (
    PlanCreateRequest,
    PlanExecuteRequest,
    PlanExecutionResponse,
    PlanListResponse,
    PlanResponse,
    PlanReviewListResponse,
    PlanReviewResponse,
    PlanStepListResponse,
    PlanStepResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/plans", tags=["planning"])


@router.post("", response_model=PlanResponse, status_code=201)
async def create_plan(
    request: PlanCreateRequest,
    session: AsyncSession = Depends(get_db_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> PlanResponse:
    """创建 plan，并默认生成 rule-based steps。"""

    try:
        service = PlanningService(session, settings=get_settings())
        plan = await service.create_plan(
            workspace_id=context.workspace_id,
            session_id=request.session_id,
            root_goal=request.root_goal,
            planner_agent=request.planner_agent,
            metadata=request.metadata,
            auto_create_steps=request.auto_create_steps,
        )
        return PlanResponse.from_model(plan)
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc
    except Exception as exc:
        logger.exception("Create plan API failed")
        raise AppError("Create plan failed", status_code=500) from exc


@router.get("", response_model=PlanListResponse)
async def list_plans(
    status: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_db_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> PlanListResponse:
    """列出当前 workspace 的 plans。"""

    service = PlanningService(session, settings=get_settings())
    plans = await service.list_plans(workspace_id=context.workspace_id, status=status, limit=limit)
    return PlanListResponse(items=[PlanResponse.from_model(plan) for plan in plans])


@router.get("/{plan_id}", response_model=PlanResponse)
async def get_plan(
    plan_id: UUID,
    session: AsyncSession = Depends(get_db_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> PlanResponse:
    """查询单个 plan。"""

    service = PlanningService(session, settings=get_settings())
    plan = await service.get_plan(plan_id=plan_id, workspace_id=context.workspace_id)
    if plan is None:
        raise AppError("Plan not found", status_code=404)
    return PlanResponse.from_model(plan)


@router.post("/{plan_id}/execute", response_model=PlanExecutionResponse)
async def execute_plan(
    plan_id: UUID,
    request: PlanExecuteRequest,
    session: AsyncSession = Depends(get_db_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> PlanExecutionResponse:
    """执行 plan。"""

    try:
        service = PlanningService(session, settings=get_settings())
        plan = await service.get_plan(plan_id=plan_id, workspace_id=context.workspace_id)
        if plan is None:
            raise AppError("Plan not found", status_code=404)
        result = await service.execute_plan(plan=plan, user_id=context.user_id, execution_input=request.input)
        steps = await service.list_steps(plan_id=plan.id, workspace_id=context.workspace_id)
        reviews = await service.list_reviews(plan_id=plan.id, workspace_id=context.workspace_id)
        return PlanExecutionResponse(
            plan=PlanResponse.from_model(plan),
            success=plan.status == "completed",
            status=plan.status,
            step_outputs=result["step_outputs"],
            review_result=result.get("review_result"),
            duration_ms=int(result.get("duration_ms") or 0),
            memory_trace=list(result.get("memory_trace") or []),
            steps=[PlanStepResponse.from_model(step) for step in steps],
            reviews=[PlanReviewResponse.from_model(review) for review in reviews],
        )
    except AppError:
        raise
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc
    except Exception as exc:
        logger.exception("Execute plan API failed", extra={"plan_id": str(plan_id)})
        raise AppError(str(exc) or "Execute plan failed", status_code=500) from exc


@router.post("/{plan_id}/cancel", response_model=PlanResponse)
async def cancel_plan(
    plan_id: UUID,
    session: AsyncSession = Depends(get_db_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> PlanResponse:
    """取消 plan。"""

    service = PlanningService(session, settings=get_settings())
    plan = await service.get_plan(plan_id=plan_id, workspace_id=context.workspace_id)
    if plan is None:
        raise AppError("Plan not found", status_code=404)
    cancelled = await service.cancel_plan(plan=plan)
    return PlanResponse.from_model(cancelled)


@router.get("/{plan_id}/steps", response_model=PlanStepListResponse)
async def list_steps(
    plan_id: UUID,
    session: AsyncSession = Depends(get_db_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> PlanStepListResponse:
    """列出 plan steps。"""

    service = PlanningService(session, settings=get_settings())
    plan = await service.get_plan(plan_id=plan_id, workspace_id=context.workspace_id)
    if plan is None:
        raise AppError("Plan not found", status_code=404)
    steps = await service.list_steps(plan_id=plan_id, workspace_id=context.workspace_id)
    return PlanStepListResponse(plan_id=plan_id, items=[PlanStepResponse.from_model(step) for step in steps])


@router.get("/{plan_id}/reviews", response_model=PlanReviewListResponse)
async def list_reviews(
    plan_id: UUID,
    session: AsyncSession = Depends(get_db_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> PlanReviewListResponse:
    """列出 plan reviews。"""

    service = PlanningService(session, settings=get_settings())
    plan = await service.get_plan(plan_id=plan_id, workspace_id=context.workspace_id)
    if plan is None:
        raise AppError("Plan not found", status_code=404)
    reviews = await service.list_reviews(plan_id=plan_id, workspace_id=context.workspace_id)
    return PlanReviewListResponse(plan_id=plan_id, items=[PlanReviewResponse.from_model(review) for review in reviews])
