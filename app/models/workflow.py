"""Workflow state and agent memory snapshot models."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, IdTimestampMixin
from app.models.enums import (
    AgentMemorySnapshotType,
    WorkflowCheckpointType,
    WorkflowGraphEdgeType,
    WorkflowDiagnosticSeverity,
    WorkflowNodeExecutionMode,
    WorkflowNodeType,
    WorkflowReplayMode,
    WorkflowReplaySessionStatus,
    WorkflowReplayStatus,
    WorkflowRunStatus,
    WorkflowStepStatus,
    WorkflowTemplateRunStatus,
    WorkflowTemplateStatus,
    WorkflowTemplateVersionValidationStatus,
)


class WorkflowGraph(IdTimestampMixin, Base):
    """Reusable workflow graph definition for conditional execution."""

    __tablename__ = "workflow_graphs"

    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    version: Mapped[str] = mapped_column(String(64), default="1", nullable=False)
    graph_definition: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    entry_node: Mapped[str] = mapped_column(String(128), nullable=False)
    graph_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict, nullable=False)

    nodes: Mapped[list["WorkflowGraphNode"]] = relationship(
        back_populates="workflow_graph",
        cascade="save-update, merge, delete, delete-orphan",
    )
    edges: Mapped[list["WorkflowGraphEdge"]] = relationship(
        back_populates="workflow_graph",
        cascade="save-update, merge, delete, delete-orphan",
    )


class WorkflowGraphNode(IdTimestampMixin, Base):
    """One executable node in a workflow graph."""

    __tablename__ = "workflow_graph_nodes"

    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    workflow_graph_id: Mapped[UUID] = mapped_column(
        ForeignKey("workflow_graphs.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    node_key: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    node_type: Mapped[str] = mapped_column(
        String(64),
        default=WorkflowNodeType.NO_OP.value,
        index=True,
        nullable=False,
    )
    execution_mode: Mapped[str] = mapped_column(
        String(32),
        default=WorkflowNodeExecutionMode.SYNC.value,
        index=True,
        nullable=False,
    )
    configuration: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    retry_policy: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    timeout_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    node_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict, nullable=False)

    workflow_graph: Mapped[WorkflowGraph] = relationship(back_populates="nodes")


class WorkflowGraphEdge(IdTimestampMixin, Base):
    """Directed edge between workflow graph nodes."""

    __tablename__ = "workflow_graph_edges"

    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    workflow_graph_id: Mapped[UUID] = mapped_column(
        ForeignKey("workflow_graphs.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    source_node_key: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    target_node_key: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    edge_type: Mapped[str] = mapped_column(
        String(32),
        default=WorkflowGraphEdgeType.SUCCESS.value,
        index=True,
        nullable=False,
    )
    condition_expression: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[int] = mapped_column(Integer, default=100, index=True, nullable=False)
    edge_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict, nullable=False)

    workflow_graph: Mapped[WorkflowGraph] = relationship(back_populates="edges")


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
    workflow_graph_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("workflow_graphs.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    graph_execution: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    current_node_key: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True)
    planned_next_nodes: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    skipped_nodes: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    retry_state: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    fallback_state: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    template_governance_state: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    compatibility_snapshot: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
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
    replay_records: Mapped[list["WorkflowReplay"]] = relationship(
        back_populates="workflow_run",
        cascade="save-update, merge, delete, delete-orphan",
    )
    execution_traces: Mapped[list["WorkflowExecutionTrace"]] = relationship(
        back_populates="workflow_run",
        cascade="save-update, merge, delete, delete-orphan",
    )
    diagnostics: Mapped[list["WorkflowRuntimeDiagnostic"]] = relationship(
        back_populates="workflow_run",
        cascade="save-update, merge, delete, delete-orphan",
    )
    replay_sessions: Mapped[list["WorkflowReplaySession"]] = relationship(
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
    node_key: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True)
    parent_node_key: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True)
    dependency_state: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
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
    execution_traces: Mapped[list["WorkflowExecutionTrace"]] = relationship(back_populates="workflow_step")


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
    workflow_template_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("workflow_templates.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    workflow_template_version_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("workflow_template_versions.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    workflow_template_run_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("workflow_template_runs.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    replay_session_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("workflow_replay_sessions.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    diagnostic_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("workflow_runtime_diagnostics.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    node_key: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True)
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


class WorkflowReplay(IdTimestampMixin, Base):
    """Replay metadata for a workflow run; does not re-execute runtime actions."""

    __tablename__ = "workflow_replays"

    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    workflow_run_id: Mapped[UUID] = mapped_column(
        ForeignKey("workflow_runs.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    replay_source_checkpoint_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("workflow_checkpoints.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    replay_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    replay_status: Mapped[str] = mapped_column(
        String(32),
        default=WorkflowReplayStatus.CREATED.value,
        index=True,
        nullable=False,
    )
    replay_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict, nullable=False)

    workflow_run: Mapped[WorkflowRun] = relationship(back_populates="replay_records")


class WorkflowExecutionTrace(IdTimestampMixin, Base):
    """Structured execution trace for workflow graph/runtime diagnostics."""

    __tablename__ = "workflow_execution_traces"

    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    workflow_run_id: Mapped[UUID] = mapped_column(
        ForeignKey("workflow_runs.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    workflow_step_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("workflow_steps.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    node_key: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True)
    event_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    execution_phase: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    status: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    input_snapshot: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    output_snapshot: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    planner_snapshot: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    fallback_triggered: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    trace_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict, nullable=False)

    workflow_run: Mapped[WorkflowRun] = relationship(back_populates="execution_traces")
    workflow_step: Mapped[WorkflowStep | None] = relationship(back_populates="execution_traces")


class WorkflowRuntimeDiagnostic(IdTimestampMixin, Base):
    """Workflow runtime diagnostic produced from traces, tasks, artifacts, and checkpoints."""

    __tablename__ = "workflow_runtime_diagnostics"

    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    workflow_run_id: Mapped[UUID] = mapped_column(
        ForeignKey("workflow_runs.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    diagnostic_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    severity: Mapped[str] = mapped_column(
        String(32),
        default=WorkflowDiagnosticSeverity.INFO.value,
        index=True,
        nullable=False,
    )
    summary: Mapped[str] = mapped_column(String(512), nullable=False)
    details: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    suggested_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    diagnostic_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict, nullable=False)

    workflow_run: Mapped[WorkflowRun] = relationship(back_populates="diagnostics")


class WorkflowReplaySession(IdTimestampMixin, Base):
    """Replay Center session metadata. This does not re-execute dangerous actions."""

    __tablename__ = "workflow_replay_sessions"

    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    workflow_run_id: Mapped[UUID] = mapped_column(
        ForeignKey("workflow_runs.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    replay_source_checkpoint_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("workflow_checkpoints.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    replay_source_node_key: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True)
    replay_status: Mapped[str] = mapped_column(
        String(32),
        default=WorkflowReplaySessionStatus.CREATED.value,
        index=True,
        nullable=False,
    )
    replay_mode: Mapped[str] = mapped_column(
        String(32),
        default=WorkflowReplayMode.METADATA_ONLY.value,
        index=True,
        nullable=False,
    )
    initiated_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True)
    replay_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    workflow_run: Mapped[WorkflowRun] = relationship(back_populates="replay_sessions")


class WorkflowTemplate(IdTimestampMixin, Base):
    """Reusable workflow template registry entry."""

    __tablename__ = "workflow_templates"
    __table_args__ = (UniqueConstraint("workspace_id", "template_key", name="uq_workflow_templates_workspace_key"),)

    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    template_key: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True)
    status: Mapped[str] = mapped_column(
        String(32),
        default=WorkflowTemplateStatus.DRAFT.value,
        index=True,
        nullable=False,
    )
    current_version: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    latest_version: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    risk_level: Mapped[str] = mapped_column(String(32), default="low", index=True, nullable=False)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    featured: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    verified: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    recommended: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    usage_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    success_rate: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    average_runtime_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    average_step_count: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    template_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict, nullable=False)

    versions: Mapped[list["WorkflowTemplateVersion"]] = relationship(
        back_populates="template",
        cascade="save-update, merge, delete, delete-orphan",
    )
    runs: Mapped[list["WorkflowTemplateRun"]] = relationship(
        back_populates="template",
        cascade="save-update, merge, delete, delete-orphan",
    )
    reviews: Mapped[list["WorkflowTemplateReview"]] = relationship(
        back_populates="template",
        cascade="save-update, merge, delete, delete-orphan",
    )
    promotions: Mapped[list["WorkflowTemplatePromotion"]] = relationship(
        back_populates="template",
        cascade="save-update, merge, delete, delete-orphan",
    )
    audit_logs: Mapped[list["WorkflowTemplateAuditLog"]] = relationship(
        back_populates="template",
        cascade="save-update, merge, delete, delete-orphan",
    )


class WorkflowTemplateVersion(IdTimestampMixin, Base):
    """Immutable version of a workflow template graph definition."""

    __tablename__ = "workflow_template_versions"
    __table_args__ = (UniqueConstraint("template_id", "version", name="uq_workflow_template_versions_template_version"),)

    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    template_id: Mapped[UUID] = mapped_column(
        ForeignKey("workflow_templates.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    version: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    graph_definition: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    entry_node: Mapped[str] = mapped_column(String(128), nullable=False)
    input_schema: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    output_schema: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    compatibility: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    validation_status: Mapped[str] = mapped_column(
        String(32),
        default=WorkflowTemplateVersionValidationStatus.PENDING.value,
        index=True,
        nullable=False,
    )
    validation_errors: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    changelog: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True)

    template: Mapped[WorkflowTemplate] = relationship(back_populates="versions")
    runs: Mapped[list["WorkflowTemplateRun"]] = relationship(
        back_populates="template_version",
        cascade="save-update, merge, delete, delete-orphan",
    )
    reviews: Mapped[list["WorkflowTemplateReview"]] = relationship(
        back_populates="template_version",
        cascade="save-update, merge, delete, delete-orphan",
    )
    compatibility_matrix: Mapped[list["WorkflowTemplateCompatibilityMatrix"]] = relationship(
        back_populates="template_version",
        cascade="save-update, merge, delete, delete-orphan",
    )


class WorkflowTemplateRun(IdTimestampMixin, Base):
    """One execution of a workflow template version."""

    __tablename__ = "workflow_template_runs"

    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    template_id: Mapped[UUID] = mapped_column(
        ForeignKey("workflow_templates.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    template_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("workflow_template_versions.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    workflow_run_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("workflow_runs.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    source_type: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    source_id: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True)
    status: Mapped[str] = mapped_column(
        String(32),
        default=WorkflowTemplateRunStatus.PENDING.value,
        index=True,
        nullable=False,
    )
    input_payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    output_payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    run_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    template: Mapped[WorkflowTemplate] = relationship(back_populates="runs")
    template_version: Mapped[WorkflowTemplateVersion] = relationship(back_populates="runs")


class WorkflowTemplateReview(IdTimestampMixin, Base):
    """Governance review for one workflow template version."""

    __tablename__ = "workflow_template_reviews"

    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    template_id: Mapped[UUID] = mapped_column(ForeignKey("workflow_templates.id", ondelete="CASCADE"), index=True, nullable=False)
    template_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("workflow_template_versions.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    reviewer_id: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True)
    review_status: Mapped[str] = mapped_column(String(32), default="pending", index=True, nullable=False)
    review_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    risk_assessment: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    compatibility_report: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    template: Mapped[WorkflowTemplate] = relationship(back_populates="reviews")
    template_version: Mapped[WorkflowTemplateVersion] = relationship(back_populates="reviews")


class WorkflowTemplatePromotion(IdTimestampMixin, Base):
    """Lifecycle promotion or rollback event for a workflow template."""

    __tablename__ = "workflow_template_promotions"

    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    template_id: Mapped[UUID] = mapped_column(ForeignKey("workflow_templates.id", ondelete="CASCADE"), index=True, nullable=False)
    from_version_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("workflow_template_versions.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    to_version_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("workflow_template_versions.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    promotion_type: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    promotion_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    promoted_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True)

    template: Mapped[WorkflowTemplate] = relationship(back_populates="promotions")


class WorkflowTemplateAuditLog(IdTimestampMixin, Base):
    """Immutable audit trail entry for template governance."""

    __tablename__ = "workflow_template_audit_logs"

    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    template_id: Mapped[UUID | None] = mapped_column(ForeignKey("workflow_templates.id", ondelete="SET NULL"), index=True, nullable=True)
    template_version_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("workflow_template_versions.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    action: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    actor_id: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True)
    previous_state: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    new_state: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    audit_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict, nullable=False)

    template: Mapped[WorkflowTemplate | None] = relationship(back_populates="audit_logs")


class WorkflowTemplateCompatibilityMatrix(IdTimestampMixin, Base):
    """Compatibility matrix entry for one template version and runtime capability."""

    __tablename__ = "workflow_template_compatibility_matrix"
    __table_args__ = (
        UniqueConstraint("workspace_id", "template_version_id", "runtime_capability", name="uq_workflow_template_matrix_capability"),
    )

    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    template_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("workflow_template_versions.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    runtime_capability: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    supported: Mapped[bool] = mapped_column(Boolean, default=True, index=True, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    matrix_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict, nullable=False)

    template_version: Mapped[WorkflowTemplateVersion] = relationship(back_populates="compatibility_matrix")
