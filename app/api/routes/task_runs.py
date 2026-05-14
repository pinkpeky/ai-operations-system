"""Task orchestration API routes."""

from __future__ import annotations

from datetime import datetime
import logging
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.core.workspace_context import WorkspaceContext, get_workspace_context
from app.db.postgres import get_session
from app.schemas.task_run import (
    TaskRunControlRequest,
    TaskRunCreateRequest,
    TaskRunEventListResponse,
    TaskRunEventResponse,
    TaskRunListResponse,
    TaskRunResponse,
)
from app.task_orchestration.service import TaskOrchestratorService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/task-runs", tags=["task-runs"])


@router.post("", response_model=TaskRunResponse, status_code=201)
async def create_task_run(
    request: TaskRunCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> TaskRunResponse:
    """Create a task run directly."""

    try:
        task = await TaskOrchestratorService(session).enqueue_task(
            workspace_id=context.workspace_id,
            task_type=request.task_type,
            source_type=request.source_type,
            source_id=request.source_id,
            input_payload=request.input_payload,
            created_by=context.user_id,
            priority=request.priority,
            max_retries=request.max_retries,
            scheduled_at=request.scheduled_at,
            metadata=request.metadata,
        )
        return TaskRunResponse.from_model(task)
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc


@router.get("", response_model=TaskRunListResponse)
async def list_task_runs(
    status: str | None = Query(default=None),
    task_type: str | None = Query(default=None),
    source_type: str | None = Query(default=None),
    created_from: datetime | None = Query(default=None),
    created_to: datetime | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> TaskRunListResponse:
    """List task runs in the current workspace."""

    tasks = await TaskOrchestratorService(session).list_tasks(
        workspace_id=context.workspace_id,
        status=status,
        task_type=task_type,
        source_type=source_type,
        created_from=created_from,
        created_to=created_to,
        limit=limit,
    )
    return TaskRunListResponse(items=[TaskRunResponse.from_model(item) for item in tasks])


@router.get("/{task_run_id}", response_model=TaskRunResponse)
async def get_task_run(
    task_run_id: UUID,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> TaskRunResponse:
    """Get a task run."""

    task = await TaskOrchestratorService(session).get_task(workspace_id=context.workspace_id, task_run_id=task_run_id)
    if task is None:
        raise AppError("Task run not found", status_code=404)
    return TaskRunResponse.from_model(task)


@router.get("/{task_run_id}/events", response_model=TaskRunEventListResponse)
async def list_task_run_events(
    task_run_id: UUID,
    limit: int = Query(default=300, ge=1, le=1000),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> TaskRunEventListResponse:
    """List a task run timeline."""

    try:
        events = await TaskOrchestratorService(session).list_events(
            workspace_id=context.workspace_id,
            task_run_id=task_run_id,
            limit=limit,
        )
        return TaskRunEventListResponse(task_run_id=task_run_id, items=[TaskRunEventResponse.from_model(item) for item in events])
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc


@router.post("/{task_run_id}/retry", response_model=TaskRunResponse)
async def retry_task_run(
    task_run_id: UUID,
    request: TaskRunControlRequest | None = None,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> TaskRunResponse:
    """Schedule a failed task run retry."""

    try:
        task = await TaskOrchestratorService(session).retry_task_by_id(
            workspace_id=context.workspace_id,
            task_run_id=task_run_id,
            reason=(request.reason if request else None) or "manual retry",
        )
        return TaskRunResponse.from_model(task)
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc


@router.post("/{task_run_id}/cancel", response_model=TaskRunResponse)
async def cancel_task_run(
    task_run_id: UUID,
    request: TaskRunControlRequest | None = None,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> TaskRunResponse:
    """Cancel a task run."""

    try:
        task = await TaskOrchestratorService(session).cancel_task(
            workspace_id=context.workspace_id,
            task_run_id=task_run_id,
            reason=request.reason if request else None,
        )
        return TaskRunResponse.from_model(task)
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc


@router.post("/{task_run_id}/resume", response_model=TaskRunResponse)
async def resume_task_run(
    task_run_id: UUID,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> TaskRunResponse:
    """Resume a waiting_approval task run after approval."""

    try:
        task = await TaskOrchestratorService(session).resume_waiting_approval_task(
            workspace_id=context.workspace_id,
            task_run_id=task_run_id,
        )
        return TaskRunResponse.from_model(task)
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc
