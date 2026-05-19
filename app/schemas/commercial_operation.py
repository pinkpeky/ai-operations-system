"""Commercial operation API schemas."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from app.models.commercial_operation import (
    CommercialOperation,
    CommercialOperationApproval,
    CommercialOperationContentDraft,
    CommercialOperationDryRun,
    CommercialOperationLink,
)


CommercialOperationStatusLiteral = Literal["draft", "planning", "ready", "active", "paused", "completed", "archived"]
CommercialOperationPriorityLiteral = Literal["low", "normal", "high"]
CommercialOperationRiskLiteral = Literal["low", "medium", "high"]
CommercialOperationApprovalStatusLiteral = Literal["pending", "approved", "rejected", "cancelled"]
CommercialOperationContentDraftStatusLiteral = Literal["draft", "ready_for_review", "approved", "rejected", "archived"]
CommercialOperationContentFormatLiteral = Literal["copy", "email", "post", "script", "landing_page", "ad"]
CommercialOperationDryRunStatusLiteral = Literal["created", "completed", "failed", "cancelled"]
CommercialOperationDryRunModeLiteral = Literal["metadata_only", "dry_run"]
CommercialOperationLinkTypeLiteral = Literal[
    "conversation",
    "artifact",
    "task_run",
    "workflow_run",
    "rag_document",
    "knowledge_source",
    "approval",
    "external",
]


class CommercialOperationCreateRequest(BaseModel):
    """Create a commercial automation operation from a business goal."""

    title: str = Field(min_length=1, max_length=255)
    objective: str = Field(min_length=1)
    target_audience: str | None = None
    channels: list[str] = Field(default_factory=list)
    status: CommercialOperationStatusLiteral = "draft"
    priority: CommercialOperationPriorityLiteral = "normal"
    risk_level: CommercialOperationRiskLiteral = "medium"
    budget_amount: Decimal | None = Field(default=None, ge=0)
    budget_currency: str = Field(default="CNY", min_length=1, max_length=16)
    start_at: datetime | None = None
    end_at: datetime | None = None
    knowledge_collection: str | None = Field(default=None, max_length=128)
    success_metrics: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_dates(self) -> "CommercialOperationCreateRequest":
        if self.start_at is not None and self.end_at is not None and self.end_at < self.start_at:
            raise ValueError("end_at must be after start_at")
        return self


class CommercialOperationUpdateRequest(BaseModel):
    """Patch a commercial automation operation."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    objective: str | None = Field(default=None, min_length=1)
    target_audience: str | None = None
    channels: list[str] | None = None
    status: CommercialOperationStatusLiteral | None = None
    priority: CommercialOperationPriorityLiteral | None = None
    risk_level: CommercialOperationRiskLiteral | None = None
    budget_amount: Decimal | None = Field(default=None, ge=0)
    budget_currency: str | None = Field(default=None, min_length=1, max_length=16)
    start_at: datetime | None = None
    end_at: datetime | None = None
    knowledge_collection: str | None = Field(default=None, max_length=128)
    success_metrics: list[str] | None = None
    constraints: list[str] | None = None
    metadata: dict[str, Any] | None = None

    @model_validator(mode="after")
    def validate_dates(self) -> "CommercialOperationUpdateRequest":
        if self.start_at is not None and self.end_at is not None and self.end_at < self.start_at:
            raise ValueError("end_at must be after start_at")
        return self


class CommercialOperationResponse(BaseModel):
    """Commercial operation API response."""

    id: UUID
    workspace_id: str
    user_id: str | None
    title: str
    objective: str
    target_audience: str | None
    channels: list[str]
    status: str
    priority: str
    risk_level: str
    budget_amount: Decimal | None
    budget_currency: str
    start_at: datetime | None
    end_at: datetime | None
    knowledge_collection: str | None
    success_metrics: list[str]
    constraints: list[str]
    plan_outline: list[dict[str, Any]]
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, operation: CommercialOperation) -> "CommercialOperationResponse":
        return cls(
            id=operation.id,
            workspace_id=operation.workspace_id,
            user_id=operation.user_id,
            title=operation.title,
            objective=operation.objective,
            target_audience=operation.target_audience,
            channels=operation.channels,
            status=operation.status,
            priority=operation.priority,
            risk_level=operation.risk_level,
            budget_amount=operation.budget_amount,
            budget_currency=operation.budget_currency,
            start_at=operation.start_at,
            end_at=operation.end_at,
            knowledge_collection=operation.knowledge_collection,
            success_metrics=operation.success_metrics,
            constraints=operation.constraints,
            plan_outline=operation.plan_outline,
            metadata=operation.operation_metadata,
            created_at=operation.created_at,
            updated_at=operation.updated_at,
        )


class CommercialOperationListResponse(BaseModel):
    """Commercial operation list response."""

    items: list[CommercialOperationResponse]


class CommercialOperationPlanPreviewResponse(BaseModel):
    """Plan preview response."""

    operation_id: UUID
    plan_outline: list[dict[str, Any]]


class CommercialOperationApprovalCreateRequest(BaseModel):
    """Request human approval for a commercial operation plan step."""

    step_key: str = Field(min_length=1, max_length=128)
    title: str = Field(min_length=1, max_length=255)
    requested_action: str | None = None
    risk_level: CommercialOperationRiskLiteral = "medium"
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationApprovalDecisionRequest(BaseModel):
    """Approve, reject, or cancel a commercial operation step approval."""

    reviewer_notes: str | None = None


class CommercialOperationApprovalResponse(BaseModel):
    """Commercial operation plan-step approval response."""

    id: UUID
    workspace_id: str
    operation_id: UUID
    step_key: str
    title: str
    requested_action: str | None
    approval_status: str
    risk_level: str
    requested_by: str | None
    reviewer_user_id: str | None
    reviewer_notes: str | None
    approved_at: datetime | None
    rejected_at: datetime | None
    cancelled_at: datetime | None
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, approval: CommercialOperationApproval) -> "CommercialOperationApprovalResponse":
        return cls(
            id=approval.id,
            workspace_id=approval.workspace_id,
            operation_id=approval.operation_id,
            step_key=approval.step_key,
            title=approval.title,
            requested_action=approval.requested_action,
            approval_status=approval.approval_status,
            risk_level=approval.risk_level,
            requested_by=approval.requested_by,
            reviewer_user_id=approval.reviewer_user_id,
            reviewer_notes=approval.reviewer_notes,
            approved_at=approval.approved_at,
            rejected_at=approval.rejected_at,
            cancelled_at=approval.cancelled_at,
            metadata=approval.approval_metadata,
            created_at=approval.created_at,
            updated_at=approval.updated_at,
        )


class CommercialOperationApprovalListResponse(BaseModel):
    """Commercial operation approval list response."""

    operation_id: UUID
    items: list[CommercialOperationApprovalResponse]


class CommercialOperationDryRunCreateRequest(BaseModel):
    """Create a safe dry-run record from an approved operation approval."""

    approval_id: UUID
    step_key: str = Field(default="execution_dry_run", min_length=1, max_length=128)
    title: str = Field(min_length=1, max_length=255)
    execution_mode: CommercialOperationDryRunModeLiteral = "metadata_only"
    execution_target: str | None = Field(default=None, max_length=128)
    input_summary: str | None = None
    expected_outputs: list[str] = Field(default_factory=list)
    readiness_checks: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationDryRunDecisionRequest(BaseModel):
    """Complete, fail, or cancel a commercial operation dry-run record."""

    result_summary: str | None = None
    failure_reason: str | None = None


class CommercialOperationDryRunResponse(BaseModel):
    """Commercial operation dry-run response."""

    id: UUID
    workspace_id: str
    operation_id: UUID
    approval_id: UUID
    step_key: str
    title: str
    dry_run_status: str
    execution_mode: str
    execution_target: str | None
    input_summary: str | None
    runbook: list[dict[str, Any]]
    expected_outputs: list[str]
    readiness_checks: list[str]
    result_summary: str | None
    failure_reason: str | None
    requested_by: str | None
    completed_by: str | None
    completed_at: datetime | None
    failed_at: datetime | None
    cancelled_at: datetime | None
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, dry_run: CommercialOperationDryRun) -> "CommercialOperationDryRunResponse":
        return cls(
            id=dry_run.id,
            workspace_id=dry_run.workspace_id,
            operation_id=dry_run.operation_id,
            approval_id=dry_run.approval_id,
            step_key=dry_run.step_key,
            title=dry_run.title,
            dry_run_status=dry_run.dry_run_status,
            execution_mode=dry_run.execution_mode,
            execution_target=dry_run.execution_target,
            input_summary=dry_run.input_summary,
            runbook=dry_run.runbook,
            expected_outputs=dry_run.expected_outputs,
            readiness_checks=dry_run.readiness_checks,
            result_summary=dry_run.result_summary,
            failure_reason=dry_run.failure_reason,
            requested_by=dry_run.requested_by,
            completed_by=dry_run.completed_by,
            completed_at=dry_run.completed_at,
            failed_at=dry_run.failed_at,
            cancelled_at=dry_run.cancelled_at,
            metadata=dry_run.dry_run_metadata,
            created_at=dry_run.created_at,
            updated_at=dry_run.updated_at,
        )


class CommercialOperationDryRunListResponse(BaseModel):
    """Commercial operation dry-run list response."""

    operation_id: UUID
    items: list[CommercialOperationDryRunResponse]


class CommercialOperationContentDraftCreateRequest(BaseModel):
    """Create a non-publishing content draft for a commercial operation channel."""

    step_key: str = Field(default="content_production", min_length=1, max_length=128)
    channel: str = Field(min_length=1, max_length=128)
    content_format: CommercialOperationContentFormatLiteral = "copy"
    title: str = Field(min_length=1, max_length=255)
    audience_segment: str | None = None
    content_body: str | None = None
    summary: str | None = None
    call_to_action: str | None = None
    source_materials: list[str] = Field(default_factory=list)
    asset_requests: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationContentDraftUpdateRequest(BaseModel):
    """Patch a commercial operation content draft without publishing it."""

    channel: str | None = Field(default=None, min_length=1, max_length=128)
    content_format: CommercialOperationContentFormatLiteral | None = None
    title: str | None = Field(default=None, min_length=1, max_length=255)
    audience_segment: str | None = None
    content_body: str | None = Field(default=None, min_length=1)
    summary: str | None = None
    call_to_action: str | None = None
    source_materials: list[str] | None = None
    asset_requests: list[dict[str, Any]] | None = None
    metadata: dict[str, Any] | None = None


class CommercialOperationContentDraftDecisionRequest(BaseModel):
    """Review or archive a commercial operation content draft."""

    reviewer_notes: str | None = None


class CommercialOperationContentDraftResponse(BaseModel):
    """Commercial operation content draft response."""

    id: UUID
    workspace_id: str
    operation_id: UUID
    step_key: str
    channel: str
    content_format: str
    title: str
    draft_status: str
    audience_segment: str | None
    content_body: str
    summary: str | None
    call_to_action: str | None
    source_materials: list[str]
    asset_requests: list[dict[str, Any]]
    reviewer_notes: str | None
    created_by: str | None
    updated_by: str | None
    approved_by: str | None
    approved_at: datetime | None
    rejected_at: datetime | None
    archived_at: datetime | None
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, draft: CommercialOperationContentDraft) -> "CommercialOperationContentDraftResponse":
        return cls(
            id=draft.id,
            workspace_id=draft.workspace_id,
            operation_id=draft.operation_id,
            step_key=draft.step_key,
            channel=draft.channel,
            content_format=draft.content_format,
            title=draft.title,
            draft_status=draft.draft_status,
            audience_segment=draft.audience_segment,
            content_body=draft.content_body,
            summary=draft.summary,
            call_to_action=draft.call_to_action,
            source_materials=draft.source_materials,
            asset_requests=draft.asset_requests,
            reviewer_notes=draft.reviewer_notes,
            created_by=draft.created_by,
            updated_by=draft.updated_by,
            approved_by=draft.approved_by,
            approved_at=draft.approved_at,
            rejected_at=draft.rejected_at,
            archived_at=draft.archived_at,
            metadata=draft.content_metadata,
            created_at=draft.created_at,
            updated_at=draft.updated_at,
        )


class CommercialOperationContentDraftListResponse(BaseModel):
    """Commercial operation content draft list response."""

    operation_id: UUID
    items: list[CommercialOperationContentDraftResponse]


class CommercialOperationLinkCreateRequest(BaseModel):
    """Attach evidence or handoff context to a commercial operation."""

    link_type: CommercialOperationLinkTypeLiteral = "external"
    target_type: str = Field(min_length=1, max_length=64)
    target_id: str = Field(min_length=1, max_length=128)
    title: str = Field(min_length=1, max_length=255)
    summary: str | None = None
    source_name: str | None = Field(default=None, max_length=128)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationLinkResponse(BaseModel):
    """Commercial operation evidence or handoff link response."""

    id: UUID
    workspace_id: str
    operation_id: UUID
    link_type: str
    target_type: str
    target_id: str
    title: str
    summary: str | None
    source_name: str | None
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, link: CommercialOperationLink) -> "CommercialOperationLinkResponse":
        return cls(
            id=link.id,
            workspace_id=link.workspace_id,
            operation_id=link.operation_id,
            link_type=link.link_type,
            target_type=link.target_type,
            target_id=link.target_id,
            title=link.title,
            summary=link.summary,
            source_name=link.source_name,
            metadata=link.link_metadata,
            created_at=link.created_at,
            updated_at=link.updated_at,
        )


class CommercialOperationLinkListResponse(BaseModel):
    """Commercial operation link list response."""

    operation_id: UUID
    items: list[CommercialOperationLinkResponse]
