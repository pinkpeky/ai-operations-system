"""Workflow template registry API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.workflow import WorkflowTemplate, WorkflowTemplateRun, WorkflowTemplateVersion


WorkflowTemplateStatusLiteral = Literal["draft", "review", "approved", "active", "disabled", "deprecated", "archived"]
WorkflowTemplateValidationStatusLiteral = Literal["pending", "valid", "invalid"]
WorkflowTemplateRunStatusLiteral = Literal["pending", "running", "completed", "failed", "cancelled"]
WorkflowTemplateRiskLiteral = Literal["low", "medium", "high"]


class WorkflowTemplateCreateRequest(BaseModel):
    template_key: str = Field(min_length=1, max_length=128)
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    category: str | None = Field(default=None, max_length=128)
    status: WorkflowTemplateStatusLiteral = "draft"
    risk_level: WorkflowTemplateRiskLiteral = "low"
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    version: str = Field(default="1", max_length=64)
    graph_definition: dict[str, Any] = Field(default_factory=dict)
    entry_node: str = Field(default="start", min_length=1, max_length=128)
    input_schema: dict[str, Any] = Field(default_factory=dict)
    output_schema: dict[str, Any] = Field(default_factory=dict)
    changelog: str | None = None


class WorkflowTemplateUpdateRequest(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    description: str | None = None
    category: str | None = Field(default=None, max_length=128)
    status: WorkflowTemplateStatusLiteral | None = None
    risk_level: WorkflowTemplateRiskLiteral | None = None
    tags: list[str] | None = None
    metadata: dict[str, Any] | None = None


class WorkflowTemplateVersionCreateRequest(BaseModel):
    version: str = Field(min_length=1, max_length=64)
    graph_definition: dict[str, Any] = Field(default_factory=dict)
    entry_node: str = Field(min_length=1, max_length=128)
    input_schema: dict[str, Any] = Field(default_factory=dict)
    output_schema: dict[str, Any] = Field(default_factory=dict)
    changelog: str | None = None


class WorkflowTemplateCompatibilityResponse(BaseModel):
    compatible: bool
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    missing_capabilities: list[str] = Field(default_factory=list)
    validation_status: WorkflowTemplateValidationStatusLiteral = "pending"


class WorkflowTemplateVersionResponse(BaseModel):
    id: UUID
    workspace_id: str
    template_id: UUID
    version: str
    graph_definition: dict[str, Any]
    entry_node: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    compatibility: dict[str, Any]
    validation_status: str
    validation_errors: list[str]
    changelog: str | None
    created_by: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, version: WorkflowTemplateVersion) -> "WorkflowTemplateVersionResponse":
        return cls(
            id=version.id,
            workspace_id=version.workspace_id,
            template_id=version.template_id,
            version=version.version,
            graph_definition=version.graph_definition or {},
            entry_node=version.entry_node,
            input_schema=version.input_schema or {},
            output_schema=version.output_schema or {},
            compatibility=version.compatibility or {},
            validation_status=version.validation_status,
            validation_errors=version.validation_errors or [],
            changelog=version.changelog,
            created_by=version.created_by,
            created_at=version.created_at,
            updated_at=version.updated_at,
        )


class WorkflowTemplateResponse(BaseModel):
    id: UUID
    workspace_id: str
    template_key: str
    name: str
    description: str | None
    category: str | None
    status: str
    current_version: str | None
    latest_version: str | None
    risk_level: str
    tags: list[str]
    featured: bool = False
    verified: bool = False
    recommended: bool = False
    usage_count: int = 0
    success_rate: float = 0.0
    average_runtime_ms: float = 0.0
    average_step_count: float = 0.0
    metadata: dict[str, Any]
    versions: list[WorkflowTemplateVersionResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, template: WorkflowTemplate) -> "WorkflowTemplateResponse":
        versions = sorted(template.versions or [], key=lambda item: item.created_at)
        return cls(
            id=template.id,
            workspace_id=template.workspace_id,
            template_key=template.template_key,
            name=template.name,
            description=template.description,
            category=template.category,
            status=template.status,
            current_version=template.current_version,
            latest_version=template.latest_version,
            risk_level=template.risk_level,
            tags=template.tags or [],
            featured=template.featured,
            verified=template.verified,
            recommended=template.recommended,
            usage_count=template.usage_count,
            success_rate=template.success_rate,
            average_runtime_ms=template.average_runtime_ms,
            average_step_count=template.average_step_count,
            metadata=template.template_metadata or {},
            versions=[WorkflowTemplateVersionResponse.from_model(item) for item in versions],
            created_at=template.created_at,
            updated_at=template.updated_at,
        )


class WorkflowTemplateListResponse(BaseModel):
    items: list[WorkflowTemplateResponse]


class WorkflowTemplateRunRequest(BaseModel):
    input: dict[str, Any] = Field(default_factory=dict)
    version_id: UUID | None = None
    source_type: str | None = None
    source_id: str | None = None
    mode: Literal["auto_safe", "review_first", "execute_after_approval"] = "auto_safe"
    execution_mode: Literal["immediate", "background", "scheduled"] = "immediate"
    metadata: dict[str, Any] = Field(default_factory=dict)


class WorkflowTemplateRunResponse(BaseModel):
    id: UUID
    workspace_id: str
    template_id: UUID
    template_version_id: UUID
    workflow_run_id: UUID | None
    source_type: str | None
    source_id: str | None
    status: str
    input_payload: dict[str, Any]
    output_payload: dict[str, Any]
    metadata: dict[str, Any]
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, run: WorkflowTemplateRun) -> "WorkflowTemplateRunResponse":
        return cls(
            id=run.id,
            workspace_id=run.workspace_id,
            template_id=run.template_id,
            template_version_id=run.template_version_id,
            workflow_run_id=run.workflow_run_id,
            source_type=run.source_type,
            source_id=run.source_id,
            status=run.status,
            input_payload=run.input_payload or {},
            output_payload=run.output_payload or {},
            metadata=run.run_metadata or {},
            started_at=run.started_at,
            completed_at=run.completed_at,
            created_at=run.created_at,
            updated_at=run.updated_at,
        )


class WorkflowTemplateRunListResponse(BaseModel):
    items: list[WorkflowTemplateRunResponse]


class WorkflowTemplateImportRequest(BaseModel):
    template: dict[str, Any] = Field(default_factory=dict)
    dry_run: bool = True
    conflict_strategy: Literal["new_version", "new_template", "error"] = "new_version"


class WorkflowTemplateImportResponse(BaseModel):
    dry_run: bool
    valid: bool
    action: str
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    template: WorkflowTemplateResponse | None = None
    version: WorkflowTemplateVersionResponse | None = None


class WorkflowTemplateExportResponse(BaseModel):
    template_key: str
    name: str
    description: str | None
    category: str | None
    version: str
    graph_definition: dict[str, Any]
    entry_node: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    metadata: dict[str, Any]
    compatibility: dict[str, Any]
