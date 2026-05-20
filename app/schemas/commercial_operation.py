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
    CommercialOperationAssetRequest,
    CommercialOperationContentDraft,
    CommercialOperationDeliverable,
    CommercialOperationDryRun,
    CommercialOperationEvidenceSnapshot,
    CommercialOperationExecutionRequest,
    CommercialOperationExecutionRun,
    CommercialOperationLink,
    CommercialOperationMonitoringObservation,
    CommercialOperationOptimizationDecision,
    CommercialOperationResult,
)
from app.schemas.rag import SearchMode


CommercialOperationStatusLiteral = Literal["draft", "planning", "ready", "active", "paused", "completed", "archived"]
CommercialOperationPriorityLiteral = Literal["low", "normal", "high"]
CommercialOperationRiskLiteral = Literal["low", "medium", "high"]
CommercialOperationApprovalStatusLiteral = Literal["pending", "approved", "rejected", "cancelled"]
CommercialOperationContentDraftStatusLiteral = Literal["draft", "ready_for_review", "approved", "rejected", "archived"]
CommercialOperationContentFormatLiteral = Literal["copy", "email", "post", "script", "landing_page", "ad"]
CommercialOperationAssetRequestStatusLiteral = Literal[
    "draft",
    "ready_for_review",
    "approved",
    "rejected",
    "prepared",
    "failed",
    "archived",
]
CommercialOperationAssetTypeLiteral = Literal["image", "video", "audio", "document", "design", "copy_asset", "other"]
CommercialOperationDeliverableStatusLiteral = Literal[
    "draft",
    "ready_for_review",
    "approved",
    "rejected",
    "packaged",
    "failed",
    "archived",
]
CommercialOperationDeliverableTypeLiteral = Literal[
    "content_package",
    "post",
    "email",
    "landing_page",
    "ad",
    "script",
    "asset_brief",
    "report",
]
CommercialOperationExecutionRequestStatusLiteral = Literal[
    "draft",
    "ready_for_review",
    "approved",
    "rejected",
    "prepared",
    "failed",
    "cancelled",
    "archived",
]
CommercialOperationExecutionTypeLiteral = Literal[
    "manual_handoff",
    "browser_worker",
    "openclaw",
    "platform_post",
    "email_send",
    "other",
]
CommercialOperationExecutionModeLiteral = Literal["metadata_only", "approval_handoff", "future_runtime"]
CommercialOperationExecutionRunStatusLiteral = Literal[
    "queued",
    "running",
    "succeeded",
    "failed",
    "retrying",
    "cancelled",
    "archived",
]
CommercialOperationResultStatusLiteral = Literal["draft", "ready_for_review", "approved", "rejected", "archived"]
CommercialOperationMonitoringObservationStatusLiteral = Literal[
    "draft",
    "ready_for_review",
    "approved",
    "rejected",
    "archived",
]
CommercialOperationOptimizationDecisionStatusLiteral = Literal[
    "draft",
    "ready_for_review",
    "approved",
    "rejected",
    "archived",
]
CommercialOperationEvidenceSnapshotStatusLiteral = Literal[
    "draft",
    "ready_for_review",
    "approved",
    "rejected",
    "archived",
]
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


class CommercialOperationContentDraftGenerateRequest(BaseModel):
    """Generate a non-publishing content draft from existing RAG search results."""

    step_key: str = Field(default="content_production", min_length=1, max_length=128)
    channel: str = Field(min_length=1, max_length=128)
    content_format: CommercialOperationContentFormatLiteral = "copy"
    title: str | None = Field(default=None, min_length=1, max_length=255)
    audience_segment: str | None = None
    query: str | None = Field(default=None, min_length=1)
    knowledge_collection: str | None = Field(default=None, min_length=1, max_length=128)
    source_id: str | None = Field(default=None, min_length=1, max_length=255)
    search_mode: SearchMode | None = None
    dense_top_k: int | None = Field(default=None, ge=1, le=100)
    keyword_top_k: int | None = Field(default=None, ge=1, le=100)
    final_top_k: int | None = Field(default=None, ge=1, le=50)
    summary: str | None = None
    call_to_action: str | None = None
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


class CommercialOperationAssetRequestCreateRequest(BaseModel):
    """Create a first-class, non-executing commercial operation asset request."""

    step_key: str = Field(default="content_production", min_length=1, max_length=128)
    content_draft_id: UUID | None = None
    channel: str = Field(min_length=1, max_length=128)
    asset_type: CommercialOperationAssetTypeLiteral = "image"
    title: str = Field(min_length=1, max_length=255)
    purpose: str | None = None
    dimensions: str | None = Field(default=None, max_length=128)
    style_constraints: str | None = None
    generation_prompt: str | None = None
    negative_prompt: str | None = None
    source_materials: list[str] = Field(default_factory=list)
    readiness_checks: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationAssetRequestUpdateRequest(BaseModel):
    """Patch a commercial operation asset request without executing generation."""

    content_draft_id: UUID | None = None
    channel: str | None = Field(default=None, min_length=1, max_length=128)
    asset_type: CommercialOperationAssetTypeLiteral | None = None
    title: str | None = Field(default=None, min_length=1, max_length=255)
    purpose: str | None = None
    dimensions: str | None = Field(default=None, max_length=128)
    style_constraints: str | None = None
    generation_prompt: str | None = None
    negative_prompt: str | None = None
    source_materials: list[str] | None = None
    readiness_checks: list[str] | None = None
    metadata: dict[str, Any] | None = None


class CommercialOperationAssetRequestDecisionRequest(BaseModel):
    """Review, prepare, fail, or archive a commercial operation asset request."""

    reviewer_notes: str | None = None
    result_summary: str | None = None
    failure_reason: str | None = None


class CommercialOperationAssetRequestResponse(BaseModel):
    """Commercial operation asset request response."""

    id: UUID
    workspace_id: str
    operation_id: UUID
    content_draft_id: UUID | None
    step_key: str
    channel: str
    asset_type: str
    title: str
    request_status: str
    purpose: str | None
    dimensions: str | None
    style_constraints: str | None
    generation_prompt: str | None
    negative_prompt: str | None
    source_materials: list[str]
    readiness_checks: list[str]
    handoff_payload: dict[str, Any]
    result_summary: str | None
    failure_reason: str | None
    reviewer_notes: str | None
    requested_by: str | None
    updated_by: str | None
    approved_by: str | None
    prepared_by: str | None
    approved_at: datetime | None
    rejected_at: datetime | None
    prepared_at: datetime | None
    failed_at: datetime | None
    archived_at: datetime | None
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, asset_request: CommercialOperationAssetRequest) -> "CommercialOperationAssetRequestResponse":
        return cls(
            id=asset_request.id,
            workspace_id=asset_request.workspace_id,
            operation_id=asset_request.operation_id,
            content_draft_id=asset_request.content_draft_id,
            step_key=asset_request.step_key,
            channel=asset_request.channel,
            asset_type=asset_request.asset_type,
            title=asset_request.title,
            request_status=asset_request.request_status,
            purpose=asset_request.purpose,
            dimensions=asset_request.dimensions,
            style_constraints=asset_request.style_constraints,
            generation_prompt=asset_request.generation_prompt,
            negative_prompt=asset_request.negative_prompt,
            source_materials=asset_request.source_materials,
            readiness_checks=asset_request.readiness_checks,
            handoff_payload=asset_request.handoff_payload,
            result_summary=asset_request.result_summary,
            failure_reason=asset_request.failure_reason,
            reviewer_notes=asset_request.reviewer_notes,
            requested_by=asset_request.requested_by,
            updated_by=asset_request.updated_by,
            approved_by=asset_request.approved_by,
            prepared_by=asset_request.prepared_by,
            approved_at=asset_request.approved_at,
            rejected_at=asset_request.rejected_at,
            prepared_at=asset_request.prepared_at,
            failed_at=asset_request.failed_at,
            archived_at=asset_request.archived_at,
            metadata=asset_request.asset_metadata,
            created_at=asset_request.created_at,
            updated_at=asset_request.updated_at,
        )


class CommercialOperationAssetRequestListResponse(BaseModel):
    """Commercial operation asset request list response."""

    operation_id: UUID
    items: list[CommercialOperationAssetRequestResponse]


class CommercialOperationDeliverableCreateRequest(BaseModel):
    """Create a reviewable commercial deliverable and Output Library artifact."""

    step_key: str = Field(default="content_production", min_length=1, max_length=128)
    content_draft_id: UUID
    asset_request_ids: list[UUID] = Field(default_factory=list)
    deliverable_type: CommercialOperationDeliverableTypeLiteral = "content_package"
    title: str = Field(min_length=1, max_length=255)
    summary: str | None = None
    delivery_notes: str | None = None
    quality_checks: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationDeliverableUpdateRequest(BaseModel):
    """Patch a commercial deliverable before final packaging."""

    asset_request_ids: list[UUID] | None = None
    deliverable_type: CommercialOperationDeliverableTypeLiteral | None = None
    title: str | None = Field(default=None, min_length=1, max_length=255)
    summary: str | None = None
    delivery_notes: str | None = None
    quality_checks: list[str] | None = None
    metadata: dict[str, Any] | None = None


class CommercialOperationDeliverableDecisionRequest(BaseModel):
    """Review, package, fail, or archive a commercial deliverable."""

    reviewer_notes: str | None = None
    result_summary: str | None = None
    failure_reason: str | None = None


class CommercialOperationDeliverableResponse(BaseModel):
    """Commercial operation deliverable response."""

    id: UUID
    workspace_id: str
    operation_id: UUID
    content_draft_id: UUID
    output_artifact_id: UUID | None
    step_key: str
    channel: str
    deliverable_type: str
    title: str
    deliverable_status: str
    summary: str | None
    delivery_notes: str | None
    asset_request_ids: list[str]
    quality_checks: list[str]
    package_payload: dict[str, Any]
    result_summary: str | None
    failure_reason: str | None
    reviewer_notes: str | None
    created_by: str | None
    updated_by: str | None
    approved_by: str | None
    packaged_by: str | None
    approved_at: datetime | None
    rejected_at: datetime | None
    packaged_at: datetime | None
    failed_at: datetime | None
    archived_at: datetime | None
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, deliverable: CommercialOperationDeliverable) -> "CommercialOperationDeliverableResponse":
        return cls(
            id=deliverable.id,
            workspace_id=deliverable.workspace_id,
            operation_id=deliverable.operation_id,
            content_draft_id=deliverable.content_draft_id,
            output_artifact_id=deliverable.output_artifact_id,
            step_key=deliverable.step_key,
            channel=deliverable.channel,
            deliverable_type=deliverable.deliverable_type,
            title=deliverable.title,
            deliverable_status=deliverable.deliverable_status,
            summary=deliverable.summary,
            delivery_notes=deliverable.delivery_notes,
            asset_request_ids=deliverable.asset_request_ids,
            quality_checks=deliverable.quality_checks,
            package_payload=deliverable.package_payload,
            result_summary=deliverable.result_summary,
            failure_reason=deliverable.failure_reason,
            reviewer_notes=deliverable.reviewer_notes,
            created_by=deliverable.created_by,
            updated_by=deliverable.updated_by,
            approved_by=deliverable.approved_by,
            packaged_by=deliverable.packaged_by,
            approved_at=deliverable.approved_at,
            rejected_at=deliverable.rejected_at,
            packaged_at=deliverable.packaged_at,
            failed_at=deliverable.failed_at,
            archived_at=deliverable.archived_at,
            metadata=deliverable.deliverable_metadata,
            created_at=deliverable.created_at,
            updated_at=deliverable.updated_at,
        )


class CommercialOperationDeliverableListResponse(BaseModel):
    """Commercial operation deliverable list response."""

    operation_id: UUID
    items: list[CommercialOperationDeliverableResponse]


class CommercialOperationEvidenceSnapshotCreateRequest(BaseModel):
    """Create a reviewable evidence snapshot from a packaged commercial deliverable."""

    deliverable_id: UUID
    evidence_type: str = Field(default="rag_snapshot", min_length=1, max_length=64)
    title: str | None = Field(default=None, min_length=1, max_length=255)
    knowledge_collection: str | None = Field(default=None, max_length=128)
    query: str | None = None
    evidence_summary: str | None = None
    relevance_notes: str | None = None
    source_document_ids: list[str] = Field(default_factory=list)
    source_links: list[dict[str, Any]] = Field(default_factory=list)
    evidence_items: list[dict[str, Any]] = Field(default_factory=list)
    coverage_checks: list[str] = Field(default_factory=list)
    snapshot_payload: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationEvidenceSnapshotGenerateRequest(BaseModel):
    """Generate a draft evidence snapshot from existing RAG search results."""

    deliverable_id: UUID
    title: str | None = Field(default=None, min_length=1, max_length=255)
    knowledge_collection: str | None = Field(default=None, min_length=1, max_length=128)
    query: str | None = Field(default=None, min_length=1)
    source_id: str | None = Field(default=None, min_length=1, max_length=255)
    search_mode: SearchMode | None = None
    dense_top_k: int | None = Field(default=None, ge=1, le=100)
    keyword_top_k: int | None = Field(default=None, ge=1, le=100)
    final_top_k: int | None = Field(default=None, ge=1, le=50)
    evidence_summary: str | None = None
    relevance_notes: str | None = None
    coverage_checks: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationEvidenceSnapshotUpdateRequest(BaseModel):
    """Patch a draft or rejected commercial evidence snapshot."""

    evidence_type: str | None = Field(default=None, min_length=1, max_length=64)
    title: str | None = Field(default=None, min_length=1, max_length=255)
    knowledge_collection: str | None = Field(default=None, max_length=128)
    query: str | None = None
    evidence_summary: str | None = None
    relevance_notes: str | None = None
    source_document_ids: list[str] | None = None
    source_links: list[dict[str, Any]] | None = None
    evidence_items: list[dict[str, Any]] | None = None
    coverage_checks: list[str] | None = None
    snapshot_payload: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None


class CommercialOperationEvidenceSnapshotDecisionRequest(BaseModel):
    """Send, approve, reject, or archive an evidence snapshot."""

    reviewer_notes: str | None = None


class CommercialOperationEvidenceSnapshotResponse(BaseModel):
    """Commercial operation evidence snapshot response."""

    id: UUID
    workspace_id: str
    operation_id: UUID
    deliverable_id: UUID
    content_draft_id: UUID
    output_artifact_id: UUID | None
    step_key: str
    channel: str
    evidence_type: str
    title: str
    snapshot_status: str
    knowledge_collection: str | None
    query: str | None
    evidence_summary: str | None
    relevance_notes: str | None
    source_document_ids: list[str]
    source_links: list[dict[str, Any]]
    evidence_items: list[dict[str, Any]]
    coverage_checks: list[str]
    snapshot_payload: dict[str, Any]
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
    def from_model(cls, snapshot: CommercialOperationEvidenceSnapshot) -> "CommercialOperationEvidenceSnapshotResponse":
        return cls(
            id=snapshot.id,
            workspace_id=snapshot.workspace_id,
            operation_id=snapshot.operation_id,
            deliverable_id=snapshot.deliverable_id,
            content_draft_id=snapshot.content_draft_id,
            output_artifact_id=snapshot.output_artifact_id,
            step_key=snapshot.step_key,
            channel=snapshot.channel,
            evidence_type=snapshot.evidence_type,
            title=snapshot.title,
            snapshot_status=snapshot.snapshot_status,
            knowledge_collection=snapshot.knowledge_collection,
            query=snapshot.query,
            evidence_summary=snapshot.evidence_summary,
            relevance_notes=snapshot.relevance_notes,
            source_document_ids=snapshot.source_document_ids,
            source_links=snapshot.source_links,
            evidence_items=snapshot.evidence_items,
            coverage_checks=snapshot.coverage_checks,
            snapshot_payload=snapshot.snapshot_payload,
            reviewer_notes=snapshot.reviewer_notes,
            created_by=snapshot.created_by,
            updated_by=snapshot.updated_by,
            approved_by=snapshot.approved_by,
            approved_at=snapshot.approved_at,
            rejected_at=snapshot.rejected_at,
            archived_at=snapshot.archived_at,
            metadata=snapshot.snapshot_metadata,
            created_at=snapshot.created_at,
            updated_at=snapshot.updated_at,
        )


class CommercialOperationEvidenceSnapshotListResponse(BaseModel):
    """Commercial operation evidence snapshot list response."""

    operation_id: UUID
    items: list[CommercialOperationEvidenceSnapshotResponse]


class CommercialOperationExecutionRequestCreateRequest(BaseModel):
    """Create a metadata-only monitored execution request from a packaged deliverable."""

    deliverable_id: UUID
    execution_type: CommercialOperationExecutionTypeLiteral = "manual_handoff"
    execution_mode: CommercialOperationExecutionModeLiteral = "metadata_only"
    title: str = Field(min_length=1, max_length=255)
    execution_target: str | None = Field(default=None, max_length=128)
    input_summary: str | None = None
    runbook: list[dict[str, Any]] = Field(default_factory=list)
    readiness_checks: list[str] = Field(default_factory=list)
    expected_outputs: list[str] = Field(default_factory=list)
    evidence_snapshot_ids: list[UUID] = Field(default_factory=list)
    operator_checklist: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationExecutionRequestUpdateRequest(BaseModel):
    """Patch a metadata-only execution request before final preparation."""

    execution_type: CommercialOperationExecutionTypeLiteral | None = None
    execution_mode: CommercialOperationExecutionModeLiteral | None = None
    title: str | None = Field(default=None, min_length=1, max_length=255)
    execution_target: str | None = Field(default=None, max_length=128)
    input_summary: str | None = None
    runbook: list[dict[str, Any]] | None = None
    readiness_checks: list[str] | None = None
    expected_outputs: list[str] | None = None
    evidence_snapshot_ids: list[UUID] | None = None
    operator_checklist: list[dict[str, Any]] | None = None
    metadata: dict[str, Any] | None = None


class CommercialOperationExecutionRequestDecisionRequest(BaseModel):
    """Review, prepare, fail, cancel, or archive an execution request."""

    reviewer_notes: str | None = None
    result_summary: str | None = None
    failure_reason: str | None = None


class CommercialOperationExecutionRequestResponse(BaseModel):
    """Commercial operation execution request response."""

    id: UUID
    workspace_id: str
    operation_id: UUID
    deliverable_id: UUID
    output_artifact_id: UUID | None
    step_key: str
    channel: str
    execution_type: str
    execution_mode: str
    title: str
    request_status: str
    execution_target: str | None
    input_summary: str | None
    runbook: list[dict[str, Any]]
    readiness_checks: list[str]
    expected_outputs: list[str]
    evidence_snapshot_ids: list[str]
    operator_checklist: list[dict[str, Any]]
    handoff_payload: dict[str, Any]
    result_summary: str | None
    failure_reason: str | None
    reviewer_notes: str | None
    requested_by: str | None
    updated_by: str | None
    approved_by: str | None
    prepared_by: str | None
    cancelled_by: str | None
    approved_at: datetime | None
    rejected_at: datetime | None
    prepared_at: datetime | None
    failed_at: datetime | None
    cancelled_at: datetime | None
    archived_at: datetime | None
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, request: CommercialOperationExecutionRequest) -> "CommercialOperationExecutionRequestResponse":
        return cls(
            id=request.id,
            workspace_id=request.workspace_id,
            operation_id=request.operation_id,
            deliverable_id=request.deliverable_id,
            output_artifact_id=request.output_artifact_id,
            step_key=request.step_key,
            channel=request.channel,
            execution_type=request.execution_type,
            execution_mode=request.execution_mode,
            title=request.title,
            request_status=request.request_status,
            execution_target=request.execution_target,
            input_summary=request.input_summary,
            runbook=request.runbook,
            readiness_checks=request.readiness_checks,
            expected_outputs=request.expected_outputs,
            evidence_snapshot_ids=request.evidence_snapshot_ids,
            operator_checklist=request.operator_checklist,
            handoff_payload=request.handoff_payload,
            result_summary=request.result_summary,
            failure_reason=request.failure_reason,
            reviewer_notes=request.reviewer_notes,
            requested_by=request.requested_by,
            updated_by=request.updated_by,
            approved_by=request.approved_by,
            prepared_by=request.prepared_by,
            cancelled_by=request.cancelled_by,
            approved_at=request.approved_at,
            rejected_at=request.rejected_at,
            prepared_at=request.prepared_at,
            failed_at=request.failed_at,
            cancelled_at=request.cancelled_at,
            archived_at=request.archived_at,
            metadata=request.execution_metadata,
            created_at=request.created_at,
            updated_at=request.updated_at,
        )


class CommercialOperationExecutionRequestListResponse(BaseModel):
    """Commercial operation execution request list response."""

    operation_id: UUID
    items: list[CommercialOperationExecutionRequestResponse]


class CommercialOperationExecutionRunCreateRequest(BaseModel):
    """Create a metadata-only execution run monitor record from a prepared request."""

    execution_request_id: UUID
    title: str | None = Field(default=None, min_length=1, max_length=255)
    execution_target: str | None = Field(default=None, max_length=128)
    input_payload: dict[str, Any] = Field(default_factory=dict)
    max_retries: int = Field(default=0, ge=0, le=10)
    operator_notes: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationExecutionRunUpdateRequest(BaseModel):
    """Patch a queued or retrying metadata-only execution run record."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    execution_target: str | None = Field(default=None, max_length=128)
    input_payload: dict[str, Any] | None = None
    max_retries: int | None = Field(default=None, ge=0, le=10)
    operator_notes: str | None = None
    metadata: dict[str, Any] | None = None


class CommercialOperationExecutionRunDecisionRequest(BaseModel):
    """Start, complete, fail, retry, cancel, or archive an execution run."""

    result_summary: str | None = None
    failure_reason: str | None = None
    operator_notes: str | None = None
    result_payload: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationExecutionRunResponse(BaseModel):
    """Commercial operation execution run response."""

    id: UUID
    workspace_id: str
    operation_id: UUID
    execution_request_id: UUID
    deliverable_id: UUID
    output_artifact_id: UUID | None
    step_key: str
    channel: str
    execution_type: str
    execution_mode: str
    execution_target: str | None
    title: str
    run_status: str
    input_payload: dict[str, Any]
    runbook_snapshot: list[dict[str, Any]]
    readiness_checks: list[str]
    expected_outputs: list[str]
    evidence_snapshot_ids: list[str]
    operator_checklist_snapshot: list[dict[str, Any]]
    runtime_payload: dict[str, Any]
    result_payload: dict[str, Any]
    recovery_plan: dict[str, Any]
    retry_count: int
    max_retries: int
    result_summary: str | None
    failure_reason: str | None
    operator_notes: str | None
    queued_by: str | None
    started_by: str | None
    completed_by: str | None
    cancelled_by: str | None
    queued_at: datetime | None
    started_at: datetime | None
    completed_at: datetime | None
    failed_at: datetime | None
    cancelled_at: datetime | None
    archived_at: datetime | None
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, run: CommercialOperationExecutionRun) -> "CommercialOperationExecutionRunResponse":
        return cls(
            id=run.id,
            workspace_id=run.workspace_id,
            operation_id=run.operation_id,
            execution_request_id=run.execution_request_id,
            deliverable_id=run.deliverable_id,
            output_artifact_id=run.output_artifact_id,
            step_key=run.step_key,
            channel=run.channel,
            execution_type=run.execution_type,
            execution_mode=run.execution_mode,
            execution_target=run.execution_target,
            title=run.title,
            run_status=run.run_status,
            input_payload=run.input_payload,
            runbook_snapshot=run.runbook_snapshot,
            readiness_checks=run.readiness_checks,
            expected_outputs=run.expected_outputs,
            evidence_snapshot_ids=run.evidence_snapshot_ids,
            operator_checklist_snapshot=run.operator_checklist_snapshot,
            runtime_payload=run.runtime_payload,
            result_payload=run.result_payload,
            recovery_plan=run.recovery_plan,
            retry_count=run.retry_count,
            max_retries=run.max_retries,
            result_summary=run.result_summary,
            failure_reason=run.failure_reason,
            operator_notes=run.operator_notes,
            queued_by=run.queued_by,
            started_by=run.started_by,
            completed_by=run.completed_by,
            cancelled_by=run.cancelled_by,
            queued_at=run.queued_at,
            started_at=run.started_at,
            completed_at=run.completed_at,
            failed_at=run.failed_at,
            cancelled_at=run.cancelled_at,
            archived_at=run.archived_at,
            metadata=run.run_metadata,
            created_at=run.created_at,
            updated_at=run.updated_at,
        )


class CommercialOperationExecutionRunListResponse(BaseModel):
    """Commercial operation execution run list response."""

    operation_id: UUID
    items: list[CommercialOperationExecutionRunResponse]


class CommercialOperationResultCreateRequest(BaseModel):
    """Create an operator-reviewed commercial result record from a terminal execution run."""

    execution_run_id: UUID
    result_type: str = Field(default="operator_report", min_length=1, max_length=64)
    title: str | None = Field(default=None, min_length=1, max_length=255)
    summary: str | None = None
    outcome_summary: str | None = None
    observed_metrics: list[dict[str, Any]] = Field(default_factory=list)
    commercial_signals: list[str] = Field(default_factory=list)
    evidence_links: list[dict[str, Any]] = Field(default_factory=list)
    follow_up_actions: list[str] = Field(default_factory=list)
    result_payload: dict[str, Any] = Field(default_factory=dict)
    recommendation_payload: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationResultUpdateRequest(BaseModel):
    """Patch a draft or rejected commercial result record."""

    result_type: str | None = Field(default=None, min_length=1, max_length=64)
    title: str | None = Field(default=None, min_length=1, max_length=255)
    summary: str | None = None
    outcome_summary: str | None = None
    observed_metrics: list[dict[str, Any]] | None = None
    commercial_signals: list[str] | None = None
    evidence_links: list[dict[str, Any]] | None = None
    follow_up_actions: list[str] | None = None
    result_payload: dict[str, Any] | None = None
    recommendation_payload: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None


class CommercialOperationResultDecisionRequest(BaseModel):
    """Send, approve, reject, or archive a commercial result record."""

    reviewer_notes: str | None = None


class CommercialOperationResultResponse(BaseModel):
    """Commercial operation result response."""

    id: UUID
    workspace_id: str
    operation_id: UUID
    execution_run_id: UUID
    execution_request_id: UUID
    deliverable_id: UUID
    output_artifact_id: UUID | None
    step_key: str
    channel: str
    result_type: str
    title: str
    result_status: str
    summary: str | None
    outcome_summary: str | None
    observed_metrics: list[dict[str, Any]]
    commercial_signals: list[str]
    evidence_links: list[dict[str, Any]]
    follow_up_actions: list[str]
    result_payload: dict[str, Any]
    recommendation_payload: dict[str, Any]
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
    def from_model(cls, result: CommercialOperationResult) -> "CommercialOperationResultResponse":
        return cls(
            id=result.id,
            workspace_id=result.workspace_id,
            operation_id=result.operation_id,
            execution_run_id=result.execution_run_id,
            execution_request_id=result.execution_request_id,
            deliverable_id=result.deliverable_id,
            output_artifact_id=result.output_artifact_id,
            step_key=result.step_key,
            channel=result.channel,
            result_type=result.result_type,
            title=result.title,
            result_status=result.result_status,
            summary=result.summary,
            outcome_summary=result.outcome_summary,
            observed_metrics=result.observed_metrics,
            commercial_signals=result.commercial_signals,
            evidence_links=result.evidence_links,
            follow_up_actions=result.follow_up_actions,
            result_payload=result.result_payload,
            recommendation_payload=result.recommendation_payload,
            reviewer_notes=result.reviewer_notes,
            created_by=result.created_by,
            updated_by=result.updated_by,
            approved_by=result.approved_by,
            approved_at=result.approved_at,
            rejected_at=result.rejected_at,
            archived_at=result.archived_at,
            metadata=result.result_metadata,
            created_at=result.created_at,
            updated_at=result.updated_at,
        )


class CommercialOperationResultListResponse(BaseModel):
    """Commercial operation result list response."""

    operation_id: UUID
    items: list[CommercialOperationResultResponse]


class CommercialOperationMonitoringObservationCreateRequest(BaseModel):
    """Create an operator-reviewed monitoring observation from an approved commercial result."""

    result_id: UUID
    observation_type: str = Field(default="manual_snapshot", min_length=1, max_length=64)
    title: str | None = Field(default=None, min_length=1, max_length=255)
    observation_window_start: datetime | None = None
    observation_window_end: datetime | None = None
    metric_snapshots: list[dict[str, Any]] = Field(default_factory=list)
    qualitative_signals: list[str] = Field(default_factory=list)
    evidence_links: list[dict[str, Any]] = Field(default_factory=list)
    anomaly_flags: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    observation_payload: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationMonitoringObservationUpdateRequest(BaseModel):
    """Patch a draft or rejected commercial monitoring observation."""

    observation_type: str | None = Field(default=None, min_length=1, max_length=64)
    title: str | None = Field(default=None, min_length=1, max_length=255)
    observation_window_start: datetime | None = None
    observation_window_end: datetime | None = None
    metric_snapshots: list[dict[str, Any]] | None = None
    qualitative_signals: list[str] | None = None
    evidence_links: list[dict[str, Any]] | None = None
    anomaly_flags: list[str] | None = None
    recommended_actions: list[str] | None = None
    observation_payload: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None


class CommercialOperationMonitoringObservationDecisionRequest(BaseModel):
    """Send, approve, reject, or archive a commercial monitoring observation."""

    reviewer_notes: str | None = None


class CommercialOperationMonitoringObservationResponse(BaseModel):
    """Commercial operation monitoring observation response."""

    id: UUID
    workspace_id: str
    operation_id: UUID
    result_id: UUID
    execution_run_id: UUID
    execution_request_id: UUID
    deliverable_id: UUID
    output_artifact_id: UUID | None
    step_key: str
    channel: str
    observation_type: str
    title: str
    observation_status: str
    observation_window_start: datetime | None
    observation_window_end: datetime | None
    metric_snapshots: list[dict[str, Any]]
    qualitative_signals: list[str]
    evidence_links: list[dict[str, Any]]
    anomaly_flags: list[str]
    recommended_actions: list[str]
    observation_payload: dict[str, Any]
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
    def from_model(
        cls,
        observation: CommercialOperationMonitoringObservation,
    ) -> "CommercialOperationMonitoringObservationResponse":
        return cls(
            id=observation.id,
            workspace_id=observation.workspace_id,
            operation_id=observation.operation_id,
            result_id=observation.result_id,
            execution_run_id=observation.execution_run_id,
            execution_request_id=observation.execution_request_id,
            deliverable_id=observation.deliverable_id,
            output_artifact_id=observation.output_artifact_id,
            step_key=observation.step_key,
            channel=observation.channel,
            observation_type=observation.observation_type,
            title=observation.title,
            observation_status=observation.observation_status,
            observation_window_start=observation.observation_window_start,
            observation_window_end=observation.observation_window_end,
            metric_snapshots=observation.metric_snapshots,
            qualitative_signals=observation.qualitative_signals,
            evidence_links=observation.evidence_links,
            anomaly_flags=observation.anomaly_flags,
            recommended_actions=observation.recommended_actions,
            observation_payload=observation.observation_payload,
            reviewer_notes=observation.reviewer_notes,
            created_by=observation.created_by,
            updated_by=observation.updated_by,
            approved_by=observation.approved_by,
            approved_at=observation.approved_at,
            rejected_at=observation.rejected_at,
            archived_at=observation.archived_at,
            metadata=observation.observation_metadata,
            created_at=observation.created_at,
            updated_at=observation.updated_at,
        )


class CommercialOperationMonitoringObservationListResponse(BaseModel):
    """Commercial operation monitoring observation list response."""

    operation_id: UUID
    items: list[CommercialOperationMonitoringObservationResponse]


class CommercialOperationOptimizationDecisionCreateRequest(BaseModel):
    """Create an operator-reviewed optimization decision from an approved monitoring observation."""

    observation_id: UUID
    decision_type: str = Field(default="iterate", min_length=1, max_length=64)
    title: str | None = Field(default=None, min_length=1, max_length=255)
    priority: str = Field(default="normal", min_length=1, max_length=16)
    rationale: str | None = None
    objective_updates: list[str] = Field(default_factory=list)
    content_actions: list[str] = Field(default_factory=list)
    asset_actions: list[str] = Field(default_factory=list)
    audience_actions: list[str] = Field(default_factory=list)
    execution_actions: list[str] = Field(default_factory=list)
    risk_controls: list[str] = Field(default_factory=list)
    decision_payload: dict[str, Any] = Field(default_factory=dict)
    next_review_at: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationOptimizationDecisionUpdateRequest(BaseModel):
    """Patch a draft or rejected commercial optimization decision."""

    decision_type: str | None = Field(default=None, min_length=1, max_length=64)
    title: str | None = Field(default=None, min_length=1, max_length=255)
    priority: str | None = Field(default=None, min_length=1, max_length=16)
    rationale: str | None = None
    objective_updates: list[str] | None = None
    content_actions: list[str] | None = None
    asset_actions: list[str] | None = None
    audience_actions: list[str] | None = None
    execution_actions: list[str] | None = None
    risk_controls: list[str] | None = None
    decision_payload: dict[str, Any] | None = None
    next_review_at: datetime | None = None
    metadata: dict[str, Any] | None = None


class CommercialOperationOptimizationDecisionDecisionRequest(BaseModel):
    """Send, approve, reject, or archive a commercial optimization decision."""

    reviewer_notes: str | None = None


class CommercialOperationOptimizationDecisionResponse(BaseModel):
    """Commercial operation optimization decision response."""

    id: UUID
    workspace_id: str
    operation_id: UUID
    observation_id: UUID
    result_id: UUID
    execution_run_id: UUID
    execution_request_id: UUID
    deliverable_id: UUID
    output_artifact_id: UUID | None
    step_key: str
    channel: str
    decision_type: str
    title: str
    decision_status: str
    priority: str
    rationale: str | None
    objective_updates: list[str]
    content_actions: list[str]
    asset_actions: list[str]
    audience_actions: list[str]
    execution_actions: list[str]
    risk_controls: list[str]
    decision_payload: dict[str, Any]
    next_review_at: datetime | None
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
    def from_model(
        cls,
        decision: CommercialOperationOptimizationDecision,
    ) -> "CommercialOperationOptimizationDecisionResponse":
        return cls(
            id=decision.id,
            workspace_id=decision.workspace_id,
            operation_id=decision.operation_id,
            observation_id=decision.observation_id,
            result_id=decision.result_id,
            execution_run_id=decision.execution_run_id,
            execution_request_id=decision.execution_request_id,
            deliverable_id=decision.deliverable_id,
            output_artifact_id=decision.output_artifact_id,
            step_key=decision.step_key,
            channel=decision.channel,
            decision_type=decision.decision_type,
            title=decision.title,
            decision_status=decision.decision_status,
            priority=decision.priority,
            rationale=decision.rationale,
            objective_updates=decision.objective_updates,
            content_actions=decision.content_actions,
            asset_actions=decision.asset_actions,
            audience_actions=decision.audience_actions,
            execution_actions=decision.execution_actions,
            risk_controls=decision.risk_controls,
            decision_payload=decision.decision_payload,
            next_review_at=decision.next_review_at,
            reviewer_notes=decision.reviewer_notes,
            created_by=decision.created_by,
            updated_by=decision.updated_by,
            approved_by=decision.approved_by,
            approved_at=decision.approved_at,
            rejected_at=decision.rejected_at,
            archived_at=decision.archived_at,
            metadata=decision.decision_metadata,
            created_at=decision.created_at,
            updated_at=decision.updated_at,
        )


class CommercialOperationOptimizationDecisionListResponse(BaseModel):
    """Commercial operation optimization decision list response."""

    operation_id: UUID
    items: list[CommercialOperationOptimizationDecisionResponse]


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
