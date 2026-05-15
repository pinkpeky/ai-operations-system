"""Task scheduler health and recovery API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.core.workspace_context import WorkspaceContext, get_workspace_context
from app.db.postgres import get_session
from app.schemas.task_run import TaskSchedulerScanResponse, TaskSchedulerStateResponse
from app.task_orchestration.recovery_service import TaskRecoveryService


router = APIRouter(prefix="/task-scheduler", tags=["task-scheduler"])


def _state_response(state) -> TaskSchedulerStateResponse:  # type: ignore[no-untyped-def]
    return TaskSchedulerStateResponse(
        id=state.id,
        workspace_id=state.workspace_id,
        scheduler_name=state.scheduler_name,
        status=state.status,
        heartbeat_at=state.heartbeat_at,
        last_scan_at=state.last_scan_at,
        active_task_count=state.active_task_count,
        recovered_task_count=state.recovered_task_count,
        metadata=state.scheduler_metadata or {},
        created_at=state.created_at,
        updated_at=state.updated_at,
    )


@router.get("/health", response_model=TaskSchedulerStateResponse)
async def get_task_scheduler_health(
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> TaskSchedulerStateResponse:
    """Return workspace task scheduler health."""

    service = TaskRecoveryService(session)
    state = await service.get_scheduler_state(workspace_id=context.workspace_id, create=True)
    if state is None:
        raise AppError("Task scheduler state unavailable", status_code=404)
    await session.commit()
    await session.refresh(state)
    return _state_response(state)


@router.post("/scan", response_model=TaskSchedulerScanResponse)
async def scan_task_scheduler(
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> TaskSchedulerScanResponse:
    """Run one manual task recovery scan for the current workspace."""

    service = TaskRecoveryService(session)
    details = await service.scan_once(workspace_id=context.workspace_id)
    state = await service.get_scheduler_state(workspace_id=context.workspace_id, create=True)
    if state is None:
        raise AppError("Task scheduler state unavailable", status_code=404)
    return TaskSchedulerScanResponse(
        scheduler=_state_response(state),
        recovered_count=sum(details.values()),
        details=details,
    )
