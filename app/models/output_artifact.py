"""Output Library ORM models.

Phase 41 stores reusable outputs from conversations, playbooks, tools, browser
runtime snapshots, RAG answers, plans, and content agents. File-heavy artifacts
keep references instead of copying large files.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, IdTimestampMixin
from app.models.enums import OutputArtifactRetentionPolicy, OutputArtifactStage, OutputArtifactStatus


class OutputArtifact(IdTimestampMixin, Base):
    """Workspace-scoped reusable execution output."""

    __tablename__ = "output_artifacts"

    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Workspace ID")
    thread_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("conversation_threads.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
        comment="Related conversation thread ID",
    )
    playbook_run_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("conversation_playbook_runs.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
        comment="Related playbook run ID",
    )
    task_run_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("task_runs.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
        comment="Related task orchestration run ID",
    )
    parent_artifact_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("output_artifacts.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
        comment="Immediate parent artifact ID for lineage",
    )
    root_artifact_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("output_artifacts.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
        comment="Root artifact ID for lineage",
    )
    source_task_run_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("task_runs.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
        comment="Source task run ID for artifact lineage",
    )
    source_playbook_run_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("conversation_playbook_runs.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
        comment="Source playbook run ID for artifact lineage",
    )
    source_conversation_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("conversation_threads.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
        comment="Source conversation thread ID for artifact lineage",
    )
    source_runtime_session_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("browser_runtime_sessions.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
        comment="Source browser runtime session ID for artifact lineage",
    )
    workflow_run_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("workflow_runs.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
        comment="Workflow run that produced or owns this artifact",
    )
    workflow_step_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("workflow_steps.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
        comment="Workflow step that produced this artifact",
    )
    checkpoint_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("workflow_checkpoints.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
        comment="Checkpoint associated with this artifact",
    )
    memory_snapshot_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("agent_memory_snapshots.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
        comment="Agent memory snapshot associated with this artifact",
    )
    source_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False, comment="Artifact source type")
    artifact_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False, comment="Artifact type")
    artifact_role: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True, comment="Pipeline role")
    artifact_stage: Mapped[str] = mapped_column(
        String(32),
        default=OutputArtifactStage.PROCESSED.value,
        index=True,
        nullable=False,
        comment="raw / processed / packaged / exported / archived",
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="Artifact title")
    summary: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Short human-readable summary")
    content: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Text/markdown/json content when small enough")
    file_path: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Referenced file path for file artifacts")
    mime_type: Mapped[str | None] = mapped_column(String(128), nullable=True, comment="Artifact MIME type")
    status: Mapped[str] = mapped_column(
        String(32),
        default=OutputArtifactStatus.ACTIVE.value,
        index=True,
        nullable=False,
        comment="active / deleted",
    )
    generated_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Generator service/tool")
    exportable: Mapped[bool] = mapped_column(Boolean, default=True, index=True, nullable=False, comment="Whether artifact can be exported")
    retention_policy: Mapped[str] = mapped_column(
        String(32),
        default=OutputArtifactRetentionPolicy.STANDARD.value,
        index=True,
        nullable=False,
        comment="temporary / standard / persistent / compliance_hold",
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True, nullable=True)
    artifact_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
        comment="Trimmed structured artifact metadata",
    )
    created_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Creator user/agent ID")


class ArtifactRelationship(IdTimestampMixin, Base):
    """Relationship edge between output artifacts."""

    __tablename__ = "artifact_relationships"

    parent_artifact_id: Mapped[UUID] = mapped_column(
        ForeignKey("output_artifacts.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="Parent/source artifact ID",
    )
    child_artifact_id: Mapped[UUID] = mapped_column(
        ForeignKey("output_artifacts.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="Child/derived artifact ID",
    )
    relationship_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    relationship_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict, nullable=False)
