"""Output Artifact API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.output_artifact import OutputArtifact


ArtifactSourceLiteral = Literal[
    "conversation",
    "playbook",
    "tool",
    "browser_runtime",
    "rag",
    "content_agent",
    "planning",
    "openclaw_mock",
]
ArtifactTypeLiteral = Literal[
    "text",
    "markdown",
    "json",
    "screenshot",
    "html_snapshot",
    "report",
    "plan",
    "rag_answer",
    "content_draft",
]


class OutputArtifactCreateRequest(BaseModel):
    """Create one artifact manually."""

    source_type: ArtifactSourceLiteral
    artifact_type: ArtifactTypeLiteral
    title: str = Field(min_length=1, max_length=255)
    summary: str | None = None
    content: str | None = None
    file_path: str | None = None
    mime_type: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    thread_id: UUID | None = None
    playbook_run_id: UUID | None = None


class OutputArtifactUpdateRequest(BaseModel):
    """Patch editable artifact fields."""

    title: str | None = Field(default=None, max_length=255)
    summary: str | None = None
    content: str | None = None
    file_path: str | None = None
    mime_type: str | None = None
    metadata: dict[str, Any] | None = None


class OutputArtifactResponse(BaseModel):
    """Output artifact response."""

    id: UUID
    workspace_id: str
    thread_id: UUID | None
    playbook_run_id: UUID | None
    source_type: str
    artifact_type: str
    title: str
    summary: str | None
    content: str | None
    file_path: str | None
    mime_type: str | None
    status: str
    metadata: dict[str, Any]
    created_by: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, artifact: OutputArtifact) -> "OutputArtifactResponse":
        return cls(
            id=artifact.id,
            workspace_id=artifact.workspace_id,
            thread_id=artifact.thread_id,
            playbook_run_id=artifact.playbook_run_id,
            source_type=artifact.source_type,
            artifact_type=artifact.artifact_type,
            title=artifact.title,
            summary=artifact.summary,
            content=artifact.content,
            file_path=artifact.file_path,
            mime_type=artifact.mime_type,
            status=artifact.status,
            metadata=artifact.artifact_metadata or {},
            created_by=artifact.created_by,
            created_at=artifact.created_at,
            updated_at=artifact.updated_at,
        )


class OutputArtifactListResponse(BaseModel):
    """Artifact list response."""

    items: list[OutputArtifactResponse]


class OutputArtifactExportResponse(BaseModel):
    """Export response for markdown/json/txt export."""

    artifact: OutputArtifactResponse
    format: str
    export_path: str
    content: str
