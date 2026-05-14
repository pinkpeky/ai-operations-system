"""Output Library ORM models.

Phase 41 stores reusable outputs from conversations, playbooks, tools, browser
runtime snapshots, RAG answers, plans, and content agents. File-heavy artifacts
keep references instead of copying large files.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, IdTimestampMixin
from app.models.enums import OutputArtifactStatus


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
    source_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False, comment="Artifact source type")
    artifact_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False, comment="Artifact type")
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
    artifact_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
        comment="Trimmed structured artifact metadata",
    )
    created_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Creator user/agent ID")
