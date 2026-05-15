"""Task orchestration runtime models.

Phase 42 adds task_runs as a new background execution layer. It is separate
from the older tasks/task_events/task_logs tables so existing Scheduler and
TaskExecutor behavior remains untouched.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, IdTimestampMixin
from app.models.enums import TaskRunPriority, TaskRunStatus, TaskSchedulerStatus


class TaskRun(IdTimestampMixin, Base):
    """One background orchestration run."""

    __tablename__ = "task_runs"

    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Workspace ID")
    task_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False, comment="conversation / playbook")
    source_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False, comment="Source system")
    source_id: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Source object ID")
    status: Mapped[str] = mapped_column(
        String(32),
        default=TaskRunStatus.PENDING.value,
        index=True,
        nullable=False,
        comment="Task run status",
    )
    priority: Mapped[str] = mapped_column(
        String(16),
        default=TaskRunPriority.NORMAL.value,
        index=True,
        nullable=False,
        comment="low / normal / high",
    )
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_retries: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    failed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    current_step: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    lease_owner: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True)
    lease_token: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True)
    lease_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True, nullable=True)
    heartbeat_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True, nullable=True)
    recovery_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_recovered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    recovery_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    failure_category: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    recoverable: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    suggested_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_event_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    input_payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    output_payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    task_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict, nullable=False)
    created_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True)

    events: Mapped[list["TaskRunEvent"]] = relationship(
        back_populates="task_run",
        cascade="save-update, merge, delete, delete-orphan",
    )


class TaskRunEvent(Base):
    """Task run timeline event."""

    __tablename__ = "task_run_events"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4, comment="Event ID")
    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Workspace ID")
    task_run_id: Mapped[UUID] = mapped_column(
        ForeignKey("task_runs.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="Task run ID",
    )
    event_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    status: Mapped[str | None] = mapped_column(String(32), index=True, nullable=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    task_run: Mapped[TaskRun] = relationship(back_populates="events")


class TaskSchedulerState(IdTimestampMixin, Base):
    """Workspace-scoped health state for the in-process task scheduler."""

    __tablename__ = "task_scheduler_state"

    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    scheduler_name: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    status: Mapped[str] = mapped_column(
        String(32),
        default=TaskSchedulerStatus.ACTIVE.value,
        index=True,
        nullable=False,
    )
    heartbeat_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True, nullable=True)
    last_scan_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True, nullable=True)
    active_task_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    recovered_task_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    scheduler_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict, nullable=False)
