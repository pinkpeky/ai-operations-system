"""Task orchestration API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.task_run import TaskRun, TaskRunEvent


TaskRunStatusLiteral = Literal[
    "pending",
    "queued",
    "running",
    "waiting_approval",
    "retrying",
    "completed",
    "failed",
    "cancelled",
    "expired",
]
TaskRunPriorityLiteral = Literal["low", "normal", "high"]


class TaskRunCreateRequest(BaseModel):
    """Create/enqueue a task run directly."""

    task_type: Literal["conversation", "playbook"] = "conversation"
    source_type: str = "conversation"
    source_id: str | None = None
    input_payload: dict[str, Any] = Field(default_factory=dict)
    priority: TaskRunPriorityLiteral = "normal"
    max_retries: int = Field(default=3, ge=0, le=20)
    scheduled_at: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class TaskRunControlRequest(BaseModel):
    """Retry/cancel/resume control request."""

    reason: str | None = None


class TaskRunResponse(BaseModel):
    """Task run response."""

    id: UUID
    workspace_id: str
    task_type: str
    source_type: str
    source_id: str | None
    status: str
    priority: str
    retry_count: int
    max_retries: int
    scheduled_at: datetime | None
    started_at: datetime | None
    completed_at: datetime | None
    cancelled_at: datetime | None
    failed_at: datetime | None
    current_step: int
    error: str | None
    lease_owner: str | None
    lease_token: str | None
    lease_expires_at: datetime | None
    heartbeat_at: datetime | None
    recovery_count: int
    last_recovered_at: datetime | None
    recovery_reason: str | None
    failure_category: str | None
    failure_reason: str | None
    recoverable: bool
    suggested_action: str | None
    last_event_summary: str | None
    input_payload: dict[str, Any]
    output_payload: dict[str, Any]
    metadata: dict[str, Any]
    created_by: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, task: TaskRun) -> "TaskRunResponse":
        return cls(
            id=task.id,
            workspace_id=task.workspace_id,
            task_type=task.task_type,
            source_type=task.source_type,
            source_id=task.source_id,
            status=task.status,
            priority=task.priority,
            retry_count=task.retry_count,
            max_retries=task.max_retries,
            scheduled_at=task.scheduled_at,
            started_at=task.started_at,
            completed_at=task.completed_at,
            cancelled_at=task.cancelled_at,
            failed_at=task.failed_at,
            current_step=task.current_step,
            error=task.error,
            lease_owner=task.lease_owner,
            lease_token=task.lease_token,
            lease_expires_at=task.lease_expires_at,
            heartbeat_at=task.heartbeat_at,
            recovery_count=task.recovery_count,
            last_recovered_at=task.last_recovered_at,
            recovery_reason=task.recovery_reason,
            failure_category=task.failure_category,
            failure_reason=task.failure_reason,
            recoverable=task.recoverable,
            suggested_action=task.suggested_action,
            last_event_summary=task.last_event_summary,
            input_payload=task.input_payload or {},
            output_payload=task.output_payload or {},
            metadata=task.task_metadata or {},
            created_by=task.created_by,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )


class TaskRunListResponse(BaseModel):
    """Task run list response."""

    items: list[TaskRunResponse]


class TaskRunEventResponse(BaseModel):
    """Task run event response."""

    id: UUID
    workspace_id: str
    task_run_id: UUID
    event_type: str
    status: str | None
    message: str | None
    payload: dict[str, Any]
    error: str | None
    created_at: datetime

    @classmethod
    def from_model(cls, event: TaskRunEvent) -> "TaskRunEventResponse":
        return cls(
            id=event.id,
            workspace_id=event.workspace_id,
            task_run_id=event.task_run_id,
            event_type=event.event_type,
            status=event.status,
            message=event.message,
            payload=event.payload or {},
            error=event.error,
            created_at=event.created_at,
        )


class TaskRunEventListResponse(BaseModel):
    """Task run event list response."""

    task_run_id: UUID
    items: list[TaskRunEventResponse]


class TaskRunDiagnosticsResponse(BaseModel):
    """Failed/recovery diagnostics for a task run."""

    task_run_id: UUID
    status: str
    failure_category: str | None
    failure_reason: str | None
    recoverable: bool
    suggested_action: str | None
    last_event_summary: str | None
    lease_expired: bool
    scheduled_due: bool
    retry_count: int
    max_retries: int


class TaskRecoverRequest(BaseModel):
    """Manual task recovery request."""

    reason: str | None = "manual recovery"


class TaskSchedulerStateResponse(BaseModel):
    """Task scheduler health response."""

    id: UUID | None = None
    workspace_id: str
    scheduler_name: str
    status: str
    heartbeat_at: datetime | None = None
    last_scan_at: datetime | None = None
    active_task_count: int = 0
    recovered_task_count: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime | None = None
    updated_at: datetime | None = None


class TaskSchedulerScanResponse(BaseModel):
    """Manual scheduler scan result."""

    scheduler: TaskSchedulerStateResponse
    recovered_count: int
    details: dict[str, int] = Field(default_factory=dict)
