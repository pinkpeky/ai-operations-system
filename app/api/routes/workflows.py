"""Workflow State API routes."""

from __future__ import annotations

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.core.workspace_context import WorkspaceContext, get_workspace_context
from app.db.postgres import get_session
from app.schemas.workflow import (
    AgentMemorySnapshotCreateRequest,
    AgentMemorySnapshotListResponse,
    AgentMemorySnapshotResponse,
    WorkflowCheckpointCreateRequest,
    WorkflowCheckpointListResponse,
    WorkflowCheckpointResponse,
    WorkflowControlRequest,
    WorkflowRunListResponse,
    WorkflowRunResponse,
    WorkflowStepListResponse,
    WorkflowStepResponse,
)
from app.workflow.services import WorkflowStateService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/workflow-runs", tags=["workflow-runs"])
memory_router = APIRouter(prefix="/agent-memory-snapshots", tags=["agent-memory-snapshots"])


@router.get("", response_model=WorkflowRunListResponse)
async def list_workflow_runs(
    status: str | None = Query(default=None),
    source_type: str | None = Query(default=None),
    conversation_thread_id: UUID | None = Query(default=None),
    playbook_run_id: UUID | None = Query(default=None),
    task_run_id: UUID | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> WorkflowRunListResponse:
    """List workflow runs in the current workspace."""

    workflows = await WorkflowStateService(session).list_workflow_runs(
        workspace_id=context.workspace_id,
        status=status,
        source_type=source_type,
        conversation_thread_id=conversation_thread_id,
        playbook_run_id=playbook_run_id,
        task_run_id=task_run_id,
        limit=limit,
    )
    return WorkflowRunListResponse(items=[WorkflowRunResponse.from_model(item) for item in workflows])


@router.get("/{workflow_run_id}", response_model=WorkflowRunResponse)
async def get_workflow_run(
    workflow_run_id: UUID,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> WorkflowRunResponse:
    """Get one workflow run."""

    workflow = await WorkflowStateService(session).get_workflow_run(
        workspace_id=context.workspace_id,
        workflow_run_id=workflow_run_id,
    )
    if workflow is None:
        raise AppError("Workflow run not found", status_code=404)
    return WorkflowRunResponse.from_model(workflow)


@router.get("/{workflow_run_id}/steps", response_model=WorkflowStepListResponse)
async def list_workflow_steps(
    workflow_run_id: UUID,
    limit: int = Query(default=300, ge=1, le=1000),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> WorkflowStepListResponse:
    """List workflow steps."""

    try:
        steps = await WorkflowStateService(session).list_steps(
            workspace_id=context.workspace_id,
            workflow_run_id=workflow_run_id,
            limit=limit,
        )
        return WorkflowStepListResponse(workflow_run_id=workflow_run_id, items=[WorkflowStepResponse.from_model(item) for item in steps])
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc


@router.get("/{workflow_run_id}/checkpoints", response_model=WorkflowCheckpointListResponse)
async def list_workflow_checkpoints(
    workflow_run_id: UUID,
    limit: int = Query(default=300, ge=1, le=1000),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> WorkflowCheckpointListResponse:
    """List workflow checkpoints."""

    try:
        checkpoints = await WorkflowStateService(session).list_checkpoints(
            workspace_id=context.workspace_id,
            workflow_run_id=workflow_run_id,
            limit=limit,
        )
        return WorkflowCheckpointListResponse(
            workflow_run_id=workflow_run_id,
            items=[WorkflowCheckpointResponse.from_model(item) for item in checkpoints],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc


@router.post("/{workflow_run_id}/pause", response_model=WorkflowRunResponse)
async def pause_workflow(
    workflow_run_id: UUID,
    request: WorkflowControlRequest | None = None,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> WorkflowRunResponse:
    """Pause a workflow run."""

    try:
        workflow = await WorkflowStateService(session).pause_workflow(
            workspace_id=context.workspace_id,
            workflow_run_id=workflow_run_id,
            reason=(request.reason if request else None) or "manual pause",
        )
        return WorkflowRunResponse.from_model(workflow)
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc


@router.post("/{workflow_run_id}/resume", response_model=WorkflowRunResponse)
async def resume_workflow(
    workflow_run_id: UUID,
    request: WorkflowControlRequest | None = None,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> WorkflowRunResponse:
    """Resume a paused workflow run."""

    try:
        workflow = await WorkflowStateService(session).resume_workflow(
            workspace_id=context.workspace_id,
            workflow_run_id=workflow_run_id,
            reason=(request.reason if request else None) or "manual resume",
        )
        return WorkflowRunResponse.from_model(workflow)
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc


@router.post("/{workflow_run_id}/checkpoints", response_model=WorkflowCheckpointResponse, status_code=201)
async def create_workflow_checkpoint(
    workflow_run_id: UUID,
    request: WorkflowCheckpointCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> WorkflowCheckpointResponse:
    """Create a manual workflow checkpoint."""

    try:
        checkpoint = await WorkflowStateService(session).create_checkpoint(
            workspace_id=context.workspace_id,
            workflow_run_id=workflow_run_id,
            checkpoint_name=request.checkpoint_name,
            checkpoint_type=request.checkpoint_type,
            state_payload=request.state_payload,
            variables_snapshot=request.variables_snapshot,
            context_snapshot=request.context_snapshot,
            created_by=context.user_id,
        )
        return WorkflowCheckpointResponse.from_model(checkpoint)
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc


@router.get("/{workflow_run_id}/memory-snapshots", response_model=AgentMemorySnapshotListResponse)
async def list_workflow_memory_snapshots(
    workflow_run_id: UUID,
    limit: int = Query(default=300, ge=1, le=1000),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> AgentMemorySnapshotListResponse:
    """List memory snapshots for a workflow run."""

    snapshots = await WorkflowStateService(session).list_memory_snapshots(
        workspace_id=context.workspace_id,
        workflow_run_id=workflow_run_id,
        limit=limit,
    )
    return AgentMemorySnapshotListResponse(
        workflow_run_id=workflow_run_id,
        items=[AgentMemorySnapshotResponse.from_model(item) for item in snapshots],
    )


@router.post("/{workflow_run_id}/memory-snapshots", response_model=AgentMemorySnapshotResponse, status_code=201)
async def create_workflow_memory_snapshot(
    workflow_run_id: UUID,
    request: AgentMemorySnapshotCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> AgentMemorySnapshotResponse:
    """Create an agent memory snapshot for a workflow run."""

    try:
        snapshot = await WorkflowStateService(session).create_memory_snapshot(
            workspace_id=context.workspace_id,
            workflow_run_id=workflow_run_id,
            memory_type=request.memory_type,
            summary=request.summary,
            memory_payload=request.memory_payload,
            source_event_ids=request.source_event_ids,
            source_artifact_ids=request.source_artifact_ids,
            metadata=request.metadata,
        )
        return AgentMemorySnapshotResponse.from_model(snapshot)
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc


@memory_router.get("", response_model=AgentMemorySnapshotListResponse)
async def list_agent_memory_snapshots(
    workflow_run_id: UUID | None = Query(default=None),
    conversation_thread_id: UUID | None = Query(default=None),
    task_run_id: UUID | None = Query(default=None),
    memory_type: str | None = Query(default=None),
    limit: int = Query(default=300, ge=1, le=1000),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> AgentMemorySnapshotListResponse:
    """List agent memory snapshots in the current workspace."""

    snapshots = await WorkflowStateService(session).list_memory_snapshots(
        workspace_id=context.workspace_id,
        workflow_run_id=workflow_run_id,
        conversation_thread_id=conversation_thread_id,
        task_run_id=task_run_id,
        memory_type=memory_type,
        limit=limit,
    )
    return AgentMemorySnapshotListResponse(
        workflow_run_id=workflow_run_id,
        items=[AgentMemorySnapshotResponse.from_model(item) for item in snapshots],
    )
