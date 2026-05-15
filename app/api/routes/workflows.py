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
    WorkflowGraphCreateRequest,
    WorkflowGraphListResponse,
    WorkflowGraphResponse,
    WorkflowPlannerResultResponse,
    WorkflowReplayCreateRequest,
    WorkflowReplayResponse,
    WorkflowRunListResponse,
    WorkflowRunResponse,
    WorkflowStepListResponse,
    WorkflowStepResponse,
)
from app.workflow.services import WorkflowGraphService, WorkflowStateService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/workflow-runs", tags=["workflow-runs"])
graph_router = APIRouter(prefix="/workflow-graphs", tags=["workflow-graphs"])
memory_router = APIRouter(prefix="/agent-memory-snapshots", tags=["agent-memory-snapshots"])


@graph_router.get("", response_model=WorkflowGraphListResponse)
async def list_workflow_graphs(
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> WorkflowGraphListResponse:
    """List workflow graph definitions in the current workspace."""

    graphs = await WorkflowGraphService(session).list_graphs(
        workspace_id=context.workspace_id,
        limit=limit,
    )
    return WorkflowGraphListResponse(items=[WorkflowGraphResponse.from_model(item) for item in graphs])


@graph_router.post("", response_model=WorkflowGraphResponse, status_code=201)
async def create_workflow_graph(
    request: WorkflowGraphCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> WorkflowGraphResponse:
    """Create a workflow graph definition and validate it before commit."""

    try:
        graph = await WorkflowGraphService(session).create_graph(
            workspace_id=context.workspace_id,
            name=request.name,
            description=request.description,
            version=request.version,
            graph_definition=request.graph_definition,
            entry_node=request.entry_node,
            nodes=[item.model_dump() for item in request.nodes],
            edges=[item.model_dump() for item in request.edges],
            metadata=request.metadata,
        )
        return WorkflowGraphResponse.from_model(graph)
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc


@graph_router.get("/{graph_id}", response_model=WorkflowGraphResponse)
async def get_workflow_graph(
    graph_id: UUID,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> WorkflowGraphResponse:
    """Get one workflow graph definition."""

    graph = await WorkflowGraphService(session).get_graph(
        workspace_id=context.workspace_id,
        graph_id=graph_id,
    )
    if graph is None:
        raise AppError("Workflow graph not found", status_code=404)
    return WorkflowGraphResponse.from_model(graph)


@graph_router.post("/{graph_id}/validate", response_model=WorkflowPlannerResultResponse)
async def validate_workflow_graph(
    graph_id: UUID,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> WorkflowPlannerResultResponse:
    """Validate a graph definition without executing it."""

    try:
        result = await WorkflowGraphService(session).validate_graph(
            workspace_id=context.workspace_id,
            graph_id=graph_id,
        )
        return WorkflowPlannerResultResponse(**result.as_dict())
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc


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
            node_key=request.node_key,
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


@router.post("/{workflow_run_id}/replay", response_model=WorkflowReplayResponse, status_code=201)
async def create_workflow_replay(
    workflow_run_id: UUID,
    request: WorkflowReplayCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> WorkflowReplayResponse:
    """Create replay metadata from a workflow checkpoint without re-executing actions."""

    try:
        replay = await WorkflowStateService(session).create_replay(
            workspace_id=context.workspace_id,
            workflow_run_id=workflow_run_id,
            replay_source_checkpoint_id=request.replay_source_checkpoint_id,
            replay_reason=request.replay_reason,
            metadata=request.metadata,
        )
        return WorkflowReplayResponse.from_model(replay)
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc


@router.get("/{workflow_run_id}/graph", response_model=WorkflowGraphResponse)
async def get_workflow_run_graph(
    workflow_run_id: UUID,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> WorkflowGraphResponse:
    """Return the graph definition linked to a workflow run."""

    try:
        workflow = await WorkflowStateService(session).require_workflow_run(
            workspace_id=context.workspace_id,
            workflow_run_id=workflow_run_id,
        )
        if workflow.workflow_graph_id is None:
            raise AppError("Workflow run is not linked to a workflow graph", status_code=404)
        graph = await WorkflowGraphService(session).require_graph(
            workspace_id=context.workspace_id,
            graph_id=workflow.workflow_graph_id,
        )
        return WorkflowGraphResponse.from_model(graph)
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc


@router.get("/{workflow_run_id}/planner", response_model=WorkflowPlannerResultResponse)
async def get_workflow_run_planner(
    workflow_run_id: UUID,
    status: str = Query(default="success", pattern="^(success|failure|retry)$"),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> WorkflowPlannerResultResponse:
    """Return graph planner state for a workflow run."""

    try:
        result = await WorkflowStateService(session).planner_result(
            workspace_id=context.workspace_id,
            workflow_run_id=workflow_run_id,
            status=status,
        )
        return WorkflowPlannerResultResponse(**result.as_dict())
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
