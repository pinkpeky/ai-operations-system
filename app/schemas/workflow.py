"""Workflow State API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.workflow import AgentMemorySnapshot, WorkflowCheckpoint, WorkflowRun, WorkflowStep


WorkflowStatusLiteral = Literal["pending", "running", "paused", "waiting_approval", "completed", "failed", "cancelled"]
WorkflowCheckpointTypeLiteral = Literal["auto", "manual", "approval", "failure", "resume"]
AgentMemorySnapshotTypeLiteral = Literal[
    "conversation_summary",
    "task_context",
    "tool_result",
    "decision",
    "approval_context",
    "artifact_summary",
]


class WorkflowRunResponse(BaseModel):
    id: UUID
    workspace_id: str
    source_type: str
    source_id: str | None
    conversation_thread_id: UUID | None
    playbook_run_id: UUID | None
    task_run_id: UUID | None
    status: str
    current_step: int
    variables: dict[str, Any]
    context: dict[str, Any]
    checkpoints: list[dict[str, Any]]
    metadata: dict[str, Any]
    started_at: datetime | None
    completed_at: datetime | None
    paused_at: datetime | None
    resumed_at: datetime | None
    failed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, workflow: WorkflowRun) -> "WorkflowRunResponse":
        return cls(
            id=workflow.id,
            workspace_id=workflow.workspace_id,
            source_type=workflow.source_type,
            source_id=workflow.source_id,
            conversation_thread_id=workflow.conversation_thread_id,
            playbook_run_id=workflow.playbook_run_id,
            task_run_id=workflow.task_run_id,
            status=workflow.status,
            current_step=workflow.current_step,
            variables=workflow.variables or {},
            context=workflow.context or {},
            checkpoints=workflow.checkpoints or [],
            metadata=workflow.workflow_metadata or {},
            started_at=workflow.started_at,
            completed_at=workflow.completed_at,
            paused_at=workflow.paused_at,
            resumed_at=workflow.resumed_at,
            failed_at=workflow.failed_at,
            created_at=workflow.created_at,
            updated_at=workflow.updated_at,
        )


class WorkflowRunListResponse(BaseModel):
    items: list[WorkflowRunResponse]


class WorkflowStepResponse(BaseModel):
    id: UUID
    workspace_id: str
    workflow_run_id: UUID
    step_index: int
    step_name: str
    step_type: str
    status: str
    input_payload: dict[str, Any]
    output_payload: dict[str, Any]
    error: str | None
    started_at: datetime | None
    completed_at: datetime | None
    duration_ms: int | None
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, step: WorkflowStep) -> "WorkflowStepResponse":
        return cls(
            id=step.id,
            workspace_id=step.workspace_id,
            workflow_run_id=step.workflow_run_id,
            step_index=step.step_index,
            step_name=step.step_name,
            step_type=step.step_type,
            status=step.status,
            input_payload=step.input_payload or {},
            output_payload=step.output_payload or {},
            error=step.error,
            started_at=step.started_at,
            completed_at=step.completed_at,
            duration_ms=step.duration_ms,
            metadata=step.step_metadata or {},
            created_at=step.created_at,
            updated_at=step.updated_at,
        )


class WorkflowStepListResponse(BaseModel):
    workflow_run_id: UUID
    items: list[WorkflowStepResponse]


class WorkflowCheckpointCreateRequest(BaseModel):
    checkpoint_name: str = Field(default="manual checkpoint", min_length=1, max_length=255)
    checkpoint_type: WorkflowCheckpointTypeLiteral = "manual"
    state_payload: dict[str, Any] = Field(default_factory=dict)
    variables_snapshot: dict[str, Any] | None = None
    context_snapshot: dict[str, Any] | None = None


class WorkflowCheckpointResponse(BaseModel):
    id: UUID
    workspace_id: str
    workflow_run_id: UUID
    checkpoint_name: str
    checkpoint_type: str
    state_payload: dict[str, Any]
    variables_snapshot: dict[str, Any]
    context_snapshot: dict[str, Any]
    created_by: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, checkpoint: WorkflowCheckpoint) -> "WorkflowCheckpointResponse":
        return cls(
            id=checkpoint.id,
            workspace_id=checkpoint.workspace_id,
            workflow_run_id=checkpoint.workflow_run_id,
            checkpoint_name=checkpoint.checkpoint_name,
            checkpoint_type=checkpoint.checkpoint_type,
            state_payload=checkpoint.state_payload or {},
            variables_snapshot=checkpoint.variables_snapshot or {},
            context_snapshot=checkpoint.context_snapshot or {},
            created_by=checkpoint.created_by,
            created_at=checkpoint.created_at,
            updated_at=checkpoint.updated_at,
        )


class WorkflowCheckpointListResponse(BaseModel):
    workflow_run_id: UUID
    items: list[WorkflowCheckpointResponse]


class WorkflowControlRequest(BaseModel):
    reason: str | None = None


class AgentMemorySnapshotCreateRequest(BaseModel):
    memory_type: AgentMemorySnapshotTypeLiteral = "task_context"
    summary: str | None = None
    memory_payload: dict[str, Any] = Field(default_factory=dict)
    source_event_ids: list[str] = Field(default_factory=list)
    source_artifact_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentMemorySnapshotResponse(BaseModel):
    id: UUID
    workspace_id: str
    workflow_run_id: UUID | None
    conversation_thread_id: UUID | None
    task_run_id: UUID | None
    memory_type: str
    summary: str | None
    memory_payload: dict[str, Any]
    source_event_ids: list[str]
    source_artifact_ids: list[str]
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, snapshot: AgentMemorySnapshot) -> "AgentMemorySnapshotResponse":
        return cls(
            id=snapshot.id,
            workspace_id=snapshot.workspace_id,
            workflow_run_id=snapshot.workflow_run_id,
            conversation_thread_id=snapshot.conversation_thread_id,
            task_run_id=snapshot.task_run_id,
            memory_type=snapshot.memory_type,
            summary=snapshot.summary,
            memory_payload=snapshot.memory_payload or {},
            source_event_ids=snapshot.source_event_ids or [],
            source_artifact_ids=snapshot.source_artifact_ids or [],
            metadata=snapshot.snapshot_metadata or {},
            created_at=snapshot.created_at,
            updated_at=snapshot.updated_at,
        )


class AgentMemorySnapshotListResponse(BaseModel):
    workflow_run_id: UUID | None = None
    items: list[AgentMemorySnapshotResponse]
