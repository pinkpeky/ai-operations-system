"""Output Artifact API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.output_artifact import ArtifactRelationship, OutputArtifact


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
    "html",
    "report",
    "plan",
    "rag_answer",
    "content_draft",
    "bundle",
    "debug",
    "replay",
    "dataset",
]
ArtifactRoleLiteral = Literal[
    "screenshot",
    "report",
    "transcript",
    "markdown",
    "html",
    "json",
    "bundle",
    "debug",
    "replay",
    "dataset",
]
ArtifactStageLiteral = Literal["raw", "processed", "packaged", "exported", "archived"]
RetentionPolicyLiteral = Literal["temporary", "standard", "persistent", "compliance_hold"]
RelationshipTypeLiteral = Literal["derived_from", "packaged_into", "summarized_from", "exported_from", "replay_of"]


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
    task_run_id: UUID | None = None
    parent_artifact_id: UUID | None = None
    root_artifact_id: UUID | None = None
    source_task_run_id: UUID | None = None
    source_playbook_run_id: UUID | None = None
    source_conversation_id: UUID | None = None
    source_runtime_session_id: UUID | None = None
    workflow_run_id: UUID | None = None
    workflow_step_id: UUID | None = None
    checkpoint_id: UUID | None = None
    memory_snapshot_id: UUID | None = None
    workflow_template_id: UUID | None = None
    workflow_template_version_id: UUID | None = None
    workflow_template_run_id: UUID | None = None
    producing_node_key: str | None = Field(default=None, max_length=128)
    replay_source: str | None = Field(default=None, max_length=255)
    graph_lineage: dict[str, Any] = Field(default_factory=dict)
    artifact_role: ArtifactRoleLiteral | None = None
    artifact_stage: ArtifactStageLiteral = "processed"
    generated_by: str | None = None
    exportable: bool = True
    retention_policy: RetentionPolicyLiteral = "standard"
    expires_at: datetime | None = None


class OutputArtifactUpdateRequest(BaseModel):
    """Patch editable artifact fields."""

    title: str | None = Field(default=None, max_length=255)
    summary: str | None = None
    content: str | None = None
    file_path: str | None = None
    mime_type: str | None = None
    metadata: dict[str, Any] | None = None
    artifact_role: ArtifactRoleLiteral | None = None
    artifact_stage: ArtifactStageLiteral | None = None
    generated_by: str | None = None
    exportable: bool | None = None
    retention_policy: RetentionPolicyLiteral | None = None
    expires_at: datetime | None = None


class OutputArtifactResponse(BaseModel):
    """Output artifact response."""

    id: UUID
    workspace_id: str
    thread_id: UUID | None
    playbook_run_id: UUID | None
    task_run_id: UUID | None
    parent_artifact_id: UUID | None
    root_artifact_id: UUID | None
    source_task_run_id: UUID | None
    source_playbook_run_id: UUID | None
    source_conversation_id: UUID | None
    source_runtime_session_id: UUID | None
    workflow_run_id: UUID | None
    workflow_step_id: UUID | None
    checkpoint_id: UUID | None
    memory_snapshot_id: UUID | None
    workflow_template_id: UUID | None
    workflow_template_version_id: UUID | None
    workflow_template_run_id: UUID | None
    producing_node_key: str | None
    replay_source: str | None
    graph_lineage: dict[str, Any]
    source_type: str
    artifact_type: str
    artifact_role: str | None
    artifact_stage: str
    title: str
    summary: str | None
    content: str | None
    file_path: str | None
    mime_type: str | None
    status: str
    generated_by: str | None
    exportable: bool
    retention_policy: str
    expires_at: datetime | None
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
            task_run_id=artifact.task_run_id,
            parent_artifact_id=artifact.parent_artifact_id,
            root_artifact_id=artifact.root_artifact_id,
            source_task_run_id=artifact.source_task_run_id,
            source_playbook_run_id=artifact.source_playbook_run_id,
            source_conversation_id=artifact.source_conversation_id,
            source_runtime_session_id=artifact.source_runtime_session_id,
            workflow_run_id=artifact.workflow_run_id,
            workflow_step_id=artifact.workflow_step_id,
            checkpoint_id=artifact.checkpoint_id,
            memory_snapshot_id=artifact.memory_snapshot_id,
            workflow_template_id=artifact.workflow_template_id,
            workflow_template_version_id=artifact.workflow_template_version_id,
            workflow_template_run_id=artifact.workflow_template_run_id,
            producing_node_key=artifact.producing_node_key,
            replay_source=artifact.replay_source,
            graph_lineage=artifact.graph_lineage or {},
            source_type=artifact.source_type,
            artifact_type=artifact.artifact_type,
            artifact_role=artifact.artifact_role,
            artifact_stage=artifact.artifact_stage,
            title=artifact.title,
            summary=artifact.summary,
            content=artifact.content,
            file_path=artifact.file_path,
            mime_type=artifact.mime_type,
            status=artifact.status,
            generated_by=artifact.generated_by,
            exportable=artifact.exportable,
            retention_policy=artifact.retention_policy,
            expires_at=artifact.expires_at,
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


class ArtifactRelationshipResponse(BaseModel):
    """Output artifact relationship edge."""

    id: UUID
    parent_artifact_id: UUID
    child_artifact_id: UUID
    relationship_type: str
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, relationship: ArtifactRelationship) -> "ArtifactRelationshipResponse":
        return cls(
            id=relationship.id,
            parent_artifact_id=relationship.parent_artifact_id,
            child_artifact_id=relationship.child_artifact_id,
            relationship_type=relationship.relationship_type,
            metadata=relationship.relationship_metadata or {},
            created_at=relationship.created_at,
            updated_at=relationship.updated_at,
        )


class ArtifactRelationshipListResponse(BaseModel):
    """Relationship list response."""

    items: list[ArtifactRelationshipResponse]


class ArtifactLineageResponse(BaseModel):
    """Lineage graph centered around one artifact."""

    artifact: OutputArtifactResponse
    root_artifact_id: UUID | None
    ancestors: list[OutputArtifactResponse]
    descendants: list[OutputArtifactResponse]
    relationships: list[ArtifactRelationshipResponse]


class OutputArtifactExportRequest(BaseModel):
    """Export one artifact without re-running its source runtime."""

    format: Literal["markdown", "html", "json", "txt", "bundle_zip", "report_package"] = "markdown"
    metadata: dict[str, Any] = Field(default_factory=dict)


class OutputArtifactActionResponse(BaseModel):
    """Mutation response for export/package actions."""

    artifact: OutputArtifactResponse
    generated_artifact: OutputArtifactResponse | None = None
    format: str | None = None
    output_path: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    content: str | None = None


class OutputArtifactPackageRequest(BaseModel):
    """Package artifacts related to one artifact."""

    package_type: Literal["bundle_zip", "report_package"] = "bundle_zip"
    include_related: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)


class ArtifactCleanupPreviewRequest(BaseModel):
    """Preview retention cleanup without deleting files."""

    retention_policy: RetentionPolicyLiteral | None = None
    limit: int = Field(default=100, ge=1, le=1000)


class ArtifactCleanupPreviewItem(BaseModel):
    """One artifact that would be archived by retention cleanup."""

    artifact_id: UUID
    title: str
    retention_policy: str
    expires_at: datetime | None
    reason: str


class ArtifactCleanupPreviewResponse(BaseModel):
    """Retention cleanup preview response."""

    workspace_id: str
    count: int
    items: list[ArtifactCleanupPreviewItem]
    execution_mode: str = "preview_only"
