"""Workflow state and agent memory snapshot models."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, IdTimestampMixin
from app.models.enums import (
    AgentMemorySnapshotType,
    WorkflowCheckpointType,
    WorkflowRunStatus,
    WorkflowStepStatus,
)


class WorkflowRun(IdTimestampMixin, Base):
    """Recoverable workflow state linked to a conversation, playbook, or task."""

    __tablename__ = "workflow_runs"

    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    source_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    source_id: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True)
    conversation_thread_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("conversation_threads.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    playbook_run_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("conversation_playbook_runs.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    task_run_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("task_runs.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(32),
        default=WorkflowRunStatus.PENDING.value,
        index=True,
        nullable=False,
    )
    current_step: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    variables: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    context: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    checkpoints: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    workflow_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    paused_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    failed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    steps: Mapped[list["WorkflowStep"]] = relationship(
        back_populates="workflow_run",
        cascade="save-update, merge, delete, delete-orphan",
    )
    checkpoint_records: Mapped[list["WorkflowCheckpoint"]] = relationship(
        back_populates="workflow_run",
        cascade="save-update, merge, delete, delete-orphan",
    )
    memory_snapshots: Mapped[list["AgentMemorySnapshot"]] = relationship(
        back_populates="workflow_run",
        cascade="save-update, merge, delete, delete-orphan",
    )


class WorkflowStep(IdTimestampMixin, Base):
    """One observable step inside a workflow run."""

    __tablename__ = "workflow_steps"

    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    workflow_run_id: Mapped[UUID] = mapped_column(
        ForeignKey("workflow_runs.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    step_index: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    step_name: Mapped[str] = mapped_column(String(255), nullable=False)
    step_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    status: Mapped[str] = mapped_column(
        String(32),
        default=WorkflowStepStatus.PENDING.value,
        index=True,
        nullable=False,
    )
    input_payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    output_payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    step_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict, nullable=False)

    workflow_run: Mapped[WorkflowRun] = relationship(back_populates="steps")


class WorkflowCheckpoint(IdTimestampMixin, Base):
    """Immutable snapshot of workflow variables and context."""

    __tablename__ = "workflow_checkpoints"

    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    workflow_run_id: Mapped[UUID] = mapped_column(
        ForeignKey("workflow_runs.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    checkpoint_name: Mapped[str] = mapped_column(String(255), nullable=False)
    checkpoint_type: Mapped[str] = mapped_column(
        String(32),
        default=WorkflowCheckpointType.AUTO.value,
        index=True,
        nullable=False,
    )
    state_payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    variables_snapshot: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    context_snapshot: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    created_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True)

    workflow_run: Mapped[WorkflowRun] = relationship(back_populates="checkpoint_records")


class AgentMemorySnapshot(IdTimestampMixin, Base):
    """Point-in-time agent memory derived from workflow events and artifacts."""

    __tablename__ = "agent_memory_snapshots"

    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    workflow_run_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("workflow_runs.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
    )
    conversation_thread_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("conversation_threads.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    task_run_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("task_runs.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    memory_type: Mapped[str] = mapped_column(
        String(64),
        default=AgentMemorySnapshotType.TASK_CONTEXT.value,
        index=True,
        nullable=False,
    )
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    memory_payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    source_event_ids: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    source_artifact_ids: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    snapshot_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict, nullable=False)

    workflow_run: Mapped[WorkflowRun | None] = relationship(back_populates="memory_snapshots")
