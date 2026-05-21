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
    CommercialOperationComfyUIAdapterConfig,
    CommercialOperationComfyUIAdapterDispatch,
    CommercialOperationComfyUIConnectionProbe,
    CommercialOperationComfyUIExecutionPlan,
    CommercialOperationComfyUIHandoff,
    CommercialOperationComfyUIJobRequest,
    CommercialOperationComfyUIPreflight,
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
CommercialOperationComfyUIHandoffStatusLiteral = Literal[
    "draft",
    "ready_for_review",
    "approved",
    "rejected",
    "prepared",
    "failed",
    "archived",
]
CommercialOperationComfyUIPreflightStatusLiteral = Literal["draft", "checked", "blocked", "failed", "archived"]
CommercialOperationComfyUIAdapterConfigStatusLiteral = Literal["draft", "ready", "blocked", "failed", "archived"]
CommercialOperationComfyUIAdapterAuthModeLiteral = Literal["none", "token_ref", "basic_ref", "custom_ref"]
CommercialOperationComfyUIJobRequestStatusLiteral = Literal[
    "draft",
    "ready_for_review",
    "approved",
    "rejected",
    "queued",
    "failed",
    "cancelled",
    "archived",
]
CommercialOperationComfyUIExecutionPlanStatusLiteral = Literal[
    "draft",
    "ready_for_review",
    "approved",
    "rejected",
    "simulated",
    "failed",
    "cancelled",
    "archived",
]
CommercialOperationComfyUIConnectionProbeStatusLiteral = Literal[
    "draft",
    "ready_for_review",
    "approved",
    "rejected",
    "probed",
    "failed",
    "cancelled",
    "archived",
]
CommercialOperationComfyUIAdapterDispatchStatusLiteral = Literal[
    "draft",
    "ready_for_review",
    "approved",
    "rejected",
    "dispatched",
    "failed",
    "cancelled",
    "archived",
]
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


class CommercialOperationAssetRequestGenerateRequest(BaseModel):
    """Generate a first-class, non-executing asset request from existing RAG search results."""

    step_key: str = Field(default="content_production", min_length=1, max_length=128)
    content_draft_id: UUID | None = None
    channel: str = Field(min_length=1, max_length=128)
    asset_type: CommercialOperationAssetTypeLiteral = "image"
    title: str | None = Field(default=None, min_length=1, max_length=255)
    purpose: str | None = None
    dimensions: str | None = Field(default=None, max_length=128)
    style_constraints: str | None = None
    query: str | None = Field(default=None, min_length=1)
    knowledge_collection: str | None = Field(default=None, min_length=1, max_length=128)
    source_id: str | None = Field(default=None, min_length=1, max_length=255)
    search_mode: SearchMode | None = None
    dense_top_k: int | None = Field(default=None, ge=1, le=100)
    keyword_top_k: int | None = Field(default=None, ge=1, le=100)
    final_top_k: int | None = Field(default=None, ge=1, le=50)
    readiness_checks: list[str] = Field(default_factory=list)
    negative_prompt: str | None = None
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


class CommercialOperationComfyUIHandoffCreateRequest(BaseModel):
    """Create a metadata-only ComfyUI handoff from an approved asset request."""

    asset_request_id: UUID
    title: str | None = Field(default=None, min_length=1, max_length=255)
    workflow_name: str = Field(default="future_comfyui_handoff", min_length=1, max_length=128)
    dimensions: str | None = Field(default=None, max_length=128)
    generation_prompt: str | None = None
    negative_prompt: str | None = None
    workflow_payload: dict[str, Any] = Field(default_factory=dict)
    prompt_payload: dict[str, Any] = Field(default_factory=dict)
    source_materials: list[str] = Field(default_factory=list)
    readiness_checks: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationComfyUIHandoffUpdateRequest(BaseModel):
    """Patch a metadata-only ComfyUI handoff without submitting jobs."""

    asset_request_id: UUID | None = None
    title: str | None = Field(default=None, min_length=1, max_length=255)
    workflow_name: str | None = Field(default=None, min_length=1, max_length=128)
    dimensions: str | None = Field(default=None, max_length=128)
    generation_prompt: str | None = None
    negative_prompt: str | None = None
    workflow_payload: dict[str, Any] | None = None
    prompt_payload: dict[str, Any] | None = None
    source_materials: list[str] | None = None
    readiness_checks: list[str] | None = None
    metadata: dict[str, Any] | None = None


class CommercialOperationComfyUIHandoffDecisionRequest(BaseModel):
    """Review, prepare, fail, or archive a metadata-only ComfyUI handoff."""

    reviewer_notes: str | None = None
    result_summary: str | None = None
    failure_reason: str | None = None


class CommercialOperationComfyUIHandoffResponse(BaseModel):
    """Commercial operation metadata-only ComfyUI handoff response."""

    id: UUID
    workspace_id: str
    operation_id: UUID
    asset_request_id: UUID
    content_draft_id: UUID | None
    step_key: str
    channel: str
    asset_type: str
    title: str
    handoff_status: str
    workflow_name: str
    dimensions: str | None
    generation_prompt: str | None
    negative_prompt: str | None
    workflow_payload: dict[str, Any]
    prompt_payload: dict[str, Any]
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
    def from_model(cls, handoff: CommercialOperationComfyUIHandoff) -> "CommercialOperationComfyUIHandoffResponse":
        return cls(
            id=handoff.id,
            workspace_id=handoff.workspace_id,
            operation_id=handoff.operation_id,
            asset_request_id=handoff.asset_request_id,
            content_draft_id=handoff.content_draft_id,
            step_key=handoff.step_key,
            channel=handoff.channel,
            asset_type=handoff.asset_type,
            title=handoff.title,
            handoff_status=handoff.handoff_status,
            workflow_name=handoff.workflow_name,
            dimensions=handoff.dimensions,
            generation_prompt=handoff.generation_prompt,
            negative_prompt=handoff.negative_prompt,
            workflow_payload=handoff.workflow_payload,
            prompt_payload=handoff.prompt_payload,
            source_materials=handoff.source_materials,
            readiness_checks=handoff.readiness_checks,
            handoff_payload=handoff.handoff_payload,
            result_summary=handoff.result_summary,
            failure_reason=handoff.failure_reason,
            reviewer_notes=handoff.reviewer_notes,
            requested_by=handoff.requested_by,
            updated_by=handoff.updated_by,
            approved_by=handoff.approved_by,
            prepared_by=handoff.prepared_by,
            approved_at=handoff.approved_at,
            rejected_at=handoff.rejected_at,
            prepared_at=handoff.prepared_at,
            failed_at=handoff.failed_at,
            archived_at=handoff.archived_at,
            metadata=handoff.handoff_metadata,
            created_at=handoff.created_at,
            updated_at=handoff.updated_at,
        )


class CommercialOperationComfyUIHandoffListResponse(BaseModel):
    """Commercial operation metadata-only ComfyUI handoff list response."""

    operation_id: UUID
    items: list[CommercialOperationComfyUIHandoffResponse]


class CommercialOperationComfyUIPreflightCreateRequest(BaseModel):
    """Create a metadata-only ComfyUI adapter readiness preflight."""

    adapter_config_id: UUID | None = None
    title: str | None = Field(default=None, min_length=1, max_length=255)
    target_url: str | None = Field(default=None, max_length=512)
    queue_name: str | None = Field(default=None, max_length=128)
    workflow_name: str | None = Field(default=None, max_length=128)
    model_refs: list[str] = Field(default_factory=list)
    adapter_config: dict[str, Any] = Field(default_factory=dict)
    check_items: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationComfyUIPreflightUpdateRequest(BaseModel):
    """Patch a metadata-only ComfyUI preflight and rerun local readiness evaluation."""

    adapter_config_id: UUID | None = None
    title: str | None = Field(default=None, min_length=1, max_length=255)
    target_url: str | None = Field(default=None, max_length=512)
    queue_name: str | None = Field(default=None, max_length=128)
    workflow_name: str | None = Field(default=None, max_length=128)
    model_refs: list[str] | None = None
    adapter_config: dict[str, Any] | None = None
    check_items: list[dict[str, Any]] | None = None
    result_summary: str | None = None
    failure_reason: str | None = None
    metadata: dict[str, Any] | None = None


class CommercialOperationComfyUIPreflightDecisionRequest(BaseModel):
    """Check, fail, or archive a metadata-only ComfyUI preflight."""

    failure_reason: str | None = None


class CommercialOperationComfyUIPreflightResponse(BaseModel):
    """Commercial operation metadata-only ComfyUI preflight response."""

    id: UUID
    workspace_id: str
    operation_id: UUID
    handoff_id: UUID
    adapter_config_id: UUID | None
    asset_request_id: UUID
    step_key: str
    title: str
    preflight_status: str
    target_url: str | None
    connection_mode: str
    queue_name: str | None
    workflow_name: str
    model_refs: list[str]
    adapter_config: dict[str, Any]
    check_items: list[dict[str, Any]]
    preflight_payload: dict[str, Any]
    result_summary: str | None
    failure_reason: str | None
    checked_by: str | None
    updated_by: str | None
    archived_by: str | None
    checked_at: datetime | None
    failed_at: datetime | None
    archived_at: datetime | None
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, preflight: CommercialOperationComfyUIPreflight) -> "CommercialOperationComfyUIPreflightResponse":
        return cls(
            id=preflight.id,
            workspace_id=preflight.workspace_id,
            operation_id=preflight.operation_id,
            handoff_id=preflight.handoff_id,
            adapter_config_id=preflight.adapter_config_id,
            asset_request_id=preflight.asset_request_id,
            step_key=preflight.step_key,
            title=preflight.title,
            preflight_status=preflight.preflight_status,
            target_url=preflight.target_url,
            connection_mode=preflight.connection_mode,
            queue_name=preflight.queue_name,
            workflow_name=preflight.workflow_name,
            model_refs=preflight.model_refs,
            adapter_config=preflight.adapter_config,
            check_items=preflight.check_items,
            preflight_payload=preflight.preflight_payload,
            result_summary=preflight.result_summary,
            failure_reason=preflight.failure_reason,
            checked_by=preflight.checked_by,
            updated_by=preflight.updated_by,
            archived_by=preflight.archived_by,
            checked_at=preflight.checked_at,
            failed_at=preflight.failed_at,
            archived_at=preflight.archived_at,
            metadata=preflight.preflight_metadata,
            created_at=preflight.created_at,
            updated_at=preflight.updated_at,
        )


class CommercialOperationComfyUIPreflightListResponse(BaseModel):
    """Commercial operation metadata-only ComfyUI preflight list response."""

    operation_id: UUID
    items: list[CommercialOperationComfyUIPreflightResponse]


class CommercialOperationComfyUIAdapterConfigCreateRequest(BaseModel):
    """Create a metadata-only ComfyUI adapter config for server maintainers."""

    title: str = Field(default="ComfyUI guarded adapter config", min_length=1, max_length=255)
    target_url: str | None = Field(default=None, max_length=512)
    auth_mode: CommercialOperationComfyUIAdapterAuthModeLiteral = "none"
    secret_ref: str | None = Field(default=None, max_length=255)
    queue_name: str | None = Field(default=None, max_length=128)
    default_workflow_name: str | None = Field(default=None, max_length=128)
    allowed_workflows: list[str] = Field(default_factory=list)
    model_inventory: list[dict[str, Any]] = Field(default_factory=list)
    runtime_limits: dict[str, Any] = Field(default_factory=dict)
    maintenance_notes: str | None = None
    validation_checks: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationComfyUIAdapterConfigUpdateRequest(BaseModel):
    """Patch a metadata-only ComfyUI adapter config and rerun local validation."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    target_url: str | None = Field(default=None, max_length=512)
    auth_mode: CommercialOperationComfyUIAdapterAuthModeLiteral | None = None
    secret_ref: str | None = Field(default=None, max_length=255)
    queue_name: str | None = Field(default=None, max_length=128)
    default_workflow_name: str | None = Field(default=None, max_length=128)
    allowed_workflows: list[str] | None = None
    model_inventory: list[dict[str, Any]] | None = None
    runtime_limits: dict[str, Any] | None = None
    maintenance_notes: str | None = None
    validation_checks: list[dict[str, Any]] | None = None
    metadata: dict[str, Any] | None = None


class CommercialOperationComfyUIAdapterConfigDecisionRequest(BaseModel):
    """Validate, fail, or archive a metadata-only ComfyUI adapter config."""

    failure_reason: str | None = None


class CommercialOperationComfyUIAdapterConfigResponse(BaseModel):
    """Commercial operation metadata-only ComfyUI adapter config response."""

    id: UUID
    workspace_id: str
    operation_id: UUID
    title: str
    config_status: str
    target_url: str | None
    auth_mode: str
    secret_ref: str | None
    queue_name: str | None
    default_workflow_name: str | None
    allowed_workflows: list[str]
    model_inventory: list[dict[str, Any]]
    runtime_limits: dict[str, Any]
    maintenance_notes: str | None
    validation_checks: list[dict[str, Any]]
    config_payload: dict[str, Any]
    result_summary: str | None
    failure_reason: str | None
    created_by: str | None
    updated_by: str | None
    validated_by: str | None
    archived_by: str | None
    validated_at: datetime | None
    failed_at: datetime | None
    archived_at: datetime | None
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(
        cls,
        config: CommercialOperationComfyUIAdapterConfig,
    ) -> "CommercialOperationComfyUIAdapterConfigResponse":
        return cls(
            id=config.id,
            workspace_id=config.workspace_id,
            operation_id=config.operation_id,
            title=config.title,
            config_status=config.config_status,
            target_url=config.target_url,
            auth_mode=config.auth_mode,
            secret_ref=config.secret_ref,
            queue_name=config.queue_name,
            default_workflow_name=config.default_workflow_name,
            allowed_workflows=config.allowed_workflows,
            model_inventory=config.model_inventory,
            runtime_limits=config.runtime_limits,
            maintenance_notes=config.maintenance_notes,
            validation_checks=config.validation_checks,
            config_payload=config.config_payload,
            result_summary=config.result_summary,
            failure_reason=config.failure_reason,
            created_by=config.created_by,
            updated_by=config.updated_by,
            validated_by=config.validated_by,
            archived_by=config.archived_by,
            validated_at=config.validated_at,
            failed_at=config.failed_at,
            archived_at=config.archived_at,
            metadata=config.config_metadata,
            created_at=config.created_at,
            updated_at=config.updated_at,
        )


class CommercialOperationComfyUIAdapterConfigListResponse(BaseModel):
    """Commercial operation metadata-only ComfyUI adapter config list response."""

    operation_id: UUID
    items: list[CommercialOperationComfyUIAdapterConfigResponse]


class CommercialOperationComfyUIJobRequestCreateRequest(BaseModel):
    """Create a metadata-only ComfyUI job request from a checked preflight."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    priority: CommercialOperationPriorityLiteral = "normal"
    runtime_payload: dict[str, Any] = Field(default_factory=dict)
    safety_checks: list[dict[str, Any]] = Field(default_factory=list)
    output_expectations: list[str] = Field(default_factory=list)
    recovery_plan: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationComfyUIJobRequestUpdateRequest(BaseModel):
    """Patch a metadata-only ComfyUI job request before queue handoff."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    priority: CommercialOperationPriorityLiteral | None = None
    runtime_payload: dict[str, Any] | None = None
    safety_checks: list[dict[str, Any]] | None = None
    output_expectations: list[str] | None = None
    recovery_plan: dict[str, Any] | None = None
    result_summary: str | None = None
    failure_reason: str | None = None
    reviewer_notes: str | None = None
    metadata: dict[str, Any] | None = None


class CommercialOperationComfyUIJobRequestDecisionRequest(BaseModel):
    """Review, queue, fail, cancel, or archive a metadata-only ComfyUI job request."""

    reviewer_notes: str | None = None
    result_summary: str | None = None
    failure_reason: str | None = None


class CommercialOperationComfyUIJobRequestResponse(BaseModel):
    """Commercial operation metadata-only ComfyUI job request response."""

    id: UUID
    workspace_id: str
    operation_id: UUID
    preflight_id: UUID
    handoff_id: UUID
    adapter_config_id: UUID | None
    asset_request_id: UUID
    step_key: str
    title: str
    job_status: str
    priority: str
    target_url: str | None
    queue_name: str | None
    workflow_name: str
    connection_mode: str
    prompt_payload: dict[str, Any]
    workflow_payload: dict[str, Any]
    runtime_payload: dict[str, Any]
    safety_checks: list[dict[str, Any]]
    output_expectations: list[str]
    recovery_plan: dict[str, Any]
    job_payload: dict[str, Any]
    result_summary: str | None
    failure_reason: str | None
    reviewer_notes: str | None
    requested_by: str | None
    updated_by: str | None
    approved_by: str | None
    queued_by: str | None
    cancelled_by: str | None
    archived_by: str | None
    approved_at: datetime | None
    rejected_at: datetime | None
    queued_at: datetime | None
    failed_at: datetime | None
    cancelled_at: datetime | None
    archived_at: datetime | None
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(
        cls,
        job_request: CommercialOperationComfyUIJobRequest,
    ) -> "CommercialOperationComfyUIJobRequestResponse":
        return cls(
            id=job_request.id,
            workspace_id=job_request.workspace_id,
            operation_id=job_request.operation_id,
            preflight_id=job_request.preflight_id,
            handoff_id=job_request.handoff_id,
            adapter_config_id=job_request.adapter_config_id,
            asset_request_id=job_request.asset_request_id,
            step_key=job_request.step_key,
            title=job_request.title,
            job_status=job_request.job_status,
            priority=job_request.priority,
            target_url=job_request.target_url,
            queue_name=job_request.queue_name,
            workflow_name=job_request.workflow_name,
            connection_mode=job_request.connection_mode,
            prompt_payload=job_request.prompt_payload,
            workflow_payload=job_request.workflow_payload,
            runtime_payload=job_request.runtime_payload,
            safety_checks=job_request.safety_checks,
            output_expectations=job_request.output_expectations,
            recovery_plan=job_request.recovery_plan,
            job_payload=job_request.job_payload,
            result_summary=job_request.result_summary,
            failure_reason=job_request.failure_reason,
            reviewer_notes=job_request.reviewer_notes,
            requested_by=job_request.requested_by,
            updated_by=job_request.updated_by,
            approved_by=job_request.approved_by,
            queued_by=job_request.queued_by,
            cancelled_by=job_request.cancelled_by,
            archived_by=job_request.archived_by,
            approved_at=job_request.approved_at,
            rejected_at=job_request.rejected_at,
            queued_at=job_request.queued_at,
            failed_at=job_request.failed_at,
            cancelled_at=job_request.cancelled_at,
            archived_at=job_request.archived_at,
            metadata=job_request.job_metadata,
            created_at=job_request.created_at,
            updated_at=job_request.updated_at,
        )


class CommercialOperationComfyUIJobRequestListResponse(BaseModel):
    """Commercial operation metadata-only ComfyUI job request list response."""

    operation_id: UUID
    items: list[CommercialOperationComfyUIJobRequestResponse]


class CommercialOperationComfyUIExecutionPlanCreateRequest(BaseModel):
    """Create a metadata-only ComfyUI execution plan from a job request."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    priority: CommercialOperationPriorityLiteral = "normal"
    execution_steps: list[dict[str, Any]] = Field(default_factory=list)
    simulation_checks: list[dict[str, Any]] = Field(default_factory=list)
    operator_checklist: list[str] = Field(default_factory=list)
    rollback_plan: dict[str, Any] = Field(default_factory=dict)
    simulation_payload: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationComfyUIExecutionPlanUpdateRequest(BaseModel):
    """Patch a metadata-only ComfyUI execution plan before simulation."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    priority: CommercialOperationPriorityLiteral | None = None
    execution_steps: list[dict[str, Any]] | None = None
    simulation_checks: list[dict[str, Any]] | None = None
    operator_checklist: list[str] | None = None
    rollback_plan: dict[str, Any] | None = None
    simulation_payload: dict[str, Any] | None = None
    result_summary: str | None = None
    failure_reason: str | None = None
    reviewer_notes: str | None = None
    metadata: dict[str, Any] | None = None


class CommercialOperationComfyUIExecutionPlanDecisionRequest(BaseModel):
    """Review, simulate, fail, cancel, or archive a ComfyUI execution plan."""

    reviewer_notes: str | None = None
    result_summary: str | None = None
    failure_reason: str | None = None


class CommercialOperationComfyUIExecutionPlanResponse(BaseModel):
    """Commercial operation metadata-only ComfyUI execution plan response."""

    id: UUID
    workspace_id: str
    operation_id: UUID
    job_request_id: UUID
    preflight_id: UUID
    handoff_id: UUID
    adapter_config_id: UUID | None
    asset_request_id: UUID
    step_key: str
    title: str
    plan_status: str
    priority: str
    target_url: str | None
    queue_name: str | None
    workflow_name: str
    execution_mode: str
    queue_payload: dict[str, Any]
    execution_steps: list[dict[str, Any]]
    simulation_checks: list[dict[str, Any]]
    operator_checklist: list[str]
    rollback_plan: dict[str, Any]
    simulation_payload: dict[str, Any]
    plan_payload: dict[str, Any]
    result_summary: str | None
    failure_reason: str | None
    reviewer_notes: str | None
    planned_by: str | None
    updated_by: str | None
    approved_by: str | None
    simulated_by: str | None
    cancelled_by: str | None
    archived_by: str | None
    approved_at: datetime | None
    rejected_at: datetime | None
    simulated_at: datetime | None
    failed_at: datetime | None
    cancelled_at: datetime | None
    archived_at: datetime | None
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(
        cls,
        plan: CommercialOperationComfyUIExecutionPlan,
    ) -> "CommercialOperationComfyUIExecutionPlanResponse":
        return cls(
            id=plan.id,
            workspace_id=plan.workspace_id,
            operation_id=plan.operation_id,
            job_request_id=plan.job_request_id,
            preflight_id=plan.preflight_id,
            handoff_id=plan.handoff_id,
            adapter_config_id=plan.adapter_config_id,
            asset_request_id=plan.asset_request_id,
            step_key=plan.step_key,
            title=plan.title,
            plan_status=plan.plan_status,
            priority=plan.priority,
            target_url=plan.target_url,
            queue_name=plan.queue_name,
            workflow_name=plan.workflow_name,
            execution_mode=plan.execution_mode,
            queue_payload=plan.queue_payload,
            execution_steps=plan.execution_steps,
            simulation_checks=plan.simulation_checks,
            operator_checklist=plan.operator_checklist,
            rollback_plan=plan.rollback_plan,
            simulation_payload=plan.simulation_payload,
            plan_payload=plan.plan_payload,
            result_summary=plan.result_summary,
            failure_reason=plan.failure_reason,
            reviewer_notes=plan.reviewer_notes,
            planned_by=plan.planned_by,
            updated_by=plan.updated_by,
            approved_by=plan.approved_by,
            simulated_by=plan.simulated_by,
            cancelled_by=plan.cancelled_by,
            archived_by=plan.archived_by,
            approved_at=plan.approved_at,
            rejected_at=plan.rejected_at,
            simulated_at=plan.simulated_at,
            failed_at=plan.failed_at,
            cancelled_at=plan.cancelled_at,
            archived_at=plan.archived_at,
            metadata=plan.plan_metadata,
            created_at=plan.created_at,
            updated_at=plan.updated_at,
        )


class CommercialOperationComfyUIExecutionPlanListResponse(BaseModel):
    """Commercial operation metadata-only ComfyUI execution plan list response."""

    operation_id: UUID
    items: list[CommercialOperationComfyUIExecutionPlanResponse]


class CommercialOperationComfyUIConnectionProbeCreateRequest(BaseModel):
    """Create a metadata-only ComfyUI connection probe from an execution plan."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    probe_mode: str = Field(default="metadata_only", min_length=1, max_length=32)
    health_endpoint: str = Field(default="/system_stats", min_length=1, max_length=128)
    queue_endpoint: str = Field(default="/queue", min_length=1, max_length=128)
    expected_routes: list[str] = Field(default_factory=list)
    readiness_checks: list[dict[str, Any]] = Field(default_factory=list)
    probe_payload: dict[str, Any] = Field(default_factory=dict)
    health_snapshot: dict[str, Any] = Field(default_factory=dict)
    queue_snapshot: dict[str, Any] = Field(default_factory=dict)
    response_schema: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationComfyUIConnectionProbeUpdateRequest(BaseModel):
    """Patch a metadata-only ComfyUI connection probe before probe recording."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    probe_mode: str | None = Field(default=None, min_length=1, max_length=32)
    health_endpoint: str | None = Field(default=None, min_length=1, max_length=128)
    queue_endpoint: str | None = Field(default=None, min_length=1, max_length=128)
    expected_routes: list[str] | None = None
    readiness_checks: list[dict[str, Any]] | None = None
    probe_payload: dict[str, Any] | None = None
    health_snapshot: dict[str, Any] | None = None
    queue_snapshot: dict[str, Any] | None = None
    response_schema: dict[str, Any] | None = None
    result_summary: str | None = None
    failure_reason: str | None = None
    reviewer_notes: str | None = None
    metadata: dict[str, Any] | None = None


class CommercialOperationComfyUIConnectionProbeDecisionRequest(BaseModel):
    """Review, probe, fail, cancel, or archive a ComfyUI connection probe."""

    reviewer_notes: str | None = None
    result_summary: str | None = None
    failure_reason: str | None = None


class CommercialOperationComfyUIConnectionProbeResponse(BaseModel):
    """Commercial operation metadata-only ComfyUI connection probe response."""

    id: UUID
    workspace_id: str
    operation_id: UUID
    execution_plan_id: UUID
    job_request_id: UUID
    preflight_id: UUID
    handoff_id: UUID
    adapter_config_id: UUID | None
    asset_request_id: UUID
    step_key: str
    title: str
    probe_status: str
    target_url: str | None
    queue_name: str | None
    workflow_name: str
    probe_mode: str
    health_endpoint: str
    queue_endpoint: str
    expected_routes: list[str]
    readiness_checks: list[dict[str, Any]]
    probe_payload: dict[str, Any]
    health_snapshot: dict[str, Any]
    queue_snapshot: dict[str, Any]
    response_schema: dict[str, Any]
    probe_plan_payload: dict[str, Any]
    result_summary: str | None
    failure_reason: str | None
    reviewer_notes: str | None
    planned_by: str | None
    updated_by: str | None
    approved_by: str | None
    probed_by: str | None
    cancelled_by: str | None
    archived_by: str | None
    approved_at: datetime | None
    rejected_at: datetime | None
    probed_at: datetime | None
    failed_at: datetime | None
    cancelled_at: datetime | None
    archived_at: datetime | None
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(
        cls,
        probe: CommercialOperationComfyUIConnectionProbe,
    ) -> "CommercialOperationComfyUIConnectionProbeResponse":
        return cls(
            id=probe.id,
            workspace_id=probe.workspace_id,
            operation_id=probe.operation_id,
            execution_plan_id=probe.execution_plan_id,
            job_request_id=probe.job_request_id,
            preflight_id=probe.preflight_id,
            handoff_id=probe.handoff_id,
            adapter_config_id=probe.adapter_config_id,
            asset_request_id=probe.asset_request_id,
            step_key=probe.step_key,
            title=probe.title,
            probe_status=probe.probe_status,
            target_url=probe.target_url,
            queue_name=probe.queue_name,
            workflow_name=probe.workflow_name,
            probe_mode=probe.probe_mode,
            health_endpoint=probe.health_endpoint,
            queue_endpoint=probe.queue_endpoint,
            expected_routes=probe.expected_routes,
            readiness_checks=probe.readiness_checks,
            probe_payload=probe.probe_payload,
            health_snapshot=probe.health_snapshot,
            queue_snapshot=probe.queue_snapshot,
            response_schema=probe.response_schema,
            probe_plan_payload=probe.probe_plan_payload,
            result_summary=probe.result_summary,
            failure_reason=probe.failure_reason,
            reviewer_notes=probe.reviewer_notes,
            planned_by=probe.planned_by,
            updated_by=probe.updated_by,
            approved_by=probe.approved_by,
            probed_by=probe.probed_by,
            cancelled_by=probe.cancelled_by,
            archived_by=probe.archived_by,
            approved_at=probe.approved_at,
            rejected_at=probe.rejected_at,
            probed_at=probe.probed_at,
            failed_at=probe.failed_at,
            cancelled_at=probe.cancelled_at,
            archived_at=probe.archived_at,
            metadata=probe.probe_metadata,
            created_at=probe.created_at,
            updated_at=probe.updated_at,
        )


class CommercialOperationComfyUIConnectionProbeListResponse(BaseModel):
    """Commercial operation metadata-only ComfyUI connection probe list response."""

    operation_id: UUID
    items: list[CommercialOperationComfyUIConnectionProbeResponse]


class CommercialOperationComfyUIAdapterDispatchCreateRequest(BaseModel):
    """Create a metadata-only ComfyUI adapter dispatch from a probed connection probe."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    dispatch_mode: str = Field(default="metadata_only", min_length=1, max_length=32)
    prompt_payload: dict[str, Any] = Field(default_factory=dict)
    workflow_payload: dict[str, Any] = Field(default_factory=dict)
    queue_payload: dict[str, Any] = Field(default_factory=dict)
    dispatch_payload: dict[str, Any] = Field(default_factory=dict)
    guardrails: list[dict[str, Any]] = Field(default_factory=list)
    operator_checklist: list[str] = Field(default_factory=list)
    retry_policy: dict[str, Any] = Field(default_factory=dict)
    recovery_plan: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationComfyUIAdapterDispatchUpdateRequest(BaseModel):
    """Patch a metadata-only ComfyUI adapter dispatch before dispatch recording."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    dispatch_mode: str | None = Field(default=None, min_length=1, max_length=32)
    prompt_payload: dict[str, Any] | None = None
    workflow_payload: dict[str, Any] | None = None
    queue_payload: dict[str, Any] | None = None
    dispatch_payload: dict[str, Any] | None = None
    guardrails: list[dict[str, Any]] | None = None
    operator_checklist: list[str] | None = None
    retry_policy: dict[str, Any] | None = None
    recovery_plan: dict[str, Any] | None = None
    result_summary: str | None = None
    failure_reason: str | None = None
    reviewer_notes: str | None = None
    metadata: dict[str, Any] | None = None


class CommercialOperationComfyUIAdapterDispatchDecisionRequest(BaseModel):
    """Review, dispatch, fail, cancel, or archive a ComfyUI adapter dispatch."""

    reviewer_notes: str | None = None
    result_summary: str | None = None
    failure_reason: str | None = None


class CommercialOperationComfyUIAdapterDispatchResponse(BaseModel):
    """Commercial operation metadata-only ComfyUI adapter dispatch response."""

    id: UUID
    workspace_id: str
    operation_id: UUID
    connection_probe_id: UUID
    execution_plan_id: UUID
    job_request_id: UUID
    preflight_id: UUID
    handoff_id: UUID
    adapter_config_id: UUID | None
    asset_request_id: UUID
    step_key: str
    title: str
    dispatch_status: str
    dispatch_mode: str
    target_url: str | None
    queue_name: str | None
    workflow_name: str
    prompt_payload: dict[str, Any]
    workflow_payload: dict[str, Any]
    queue_payload: dict[str, Any]
    dispatch_payload: dict[str, Any]
    guardrails: list[dict[str, Any]]
    operator_checklist: list[str]
    retry_policy: dict[str, Any]
    recovery_plan: dict[str, Any]
    dispatch_plan_payload: dict[str, Any]
    result_summary: str | None
    failure_reason: str | None
    reviewer_notes: str | None
    planned_by: str | None
    updated_by: str | None
    approved_by: str | None
    dispatched_by: str | None
    cancelled_by: str | None
    archived_by: str | None
    approved_at: datetime | None
    rejected_at: datetime | None
    dispatched_at: datetime | None
    failed_at: datetime | None
    cancelled_at: datetime | None
    archived_at: datetime | None
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(
        cls,
        dispatch: CommercialOperationComfyUIAdapterDispatch,
    ) -> "CommercialOperationComfyUIAdapterDispatchResponse":
        return cls(
            id=dispatch.id,
            workspace_id=dispatch.workspace_id,
            operation_id=dispatch.operation_id,
            connection_probe_id=dispatch.connection_probe_id,
            execution_plan_id=dispatch.execution_plan_id,
            job_request_id=dispatch.job_request_id,
            preflight_id=dispatch.preflight_id,
            handoff_id=dispatch.handoff_id,
            adapter_config_id=dispatch.adapter_config_id,
            asset_request_id=dispatch.asset_request_id,
            step_key=dispatch.step_key,
            title=dispatch.title,
            dispatch_status=dispatch.dispatch_status,
            dispatch_mode=dispatch.dispatch_mode,
            target_url=dispatch.target_url,
            queue_name=dispatch.queue_name,
            workflow_name=dispatch.workflow_name,
            prompt_payload=dispatch.prompt_payload,
            workflow_payload=dispatch.workflow_payload,
            queue_payload=dispatch.queue_payload,
            dispatch_payload=dispatch.dispatch_payload,
            guardrails=dispatch.guardrails,
            operator_checklist=dispatch.operator_checklist,
            retry_policy=dispatch.retry_policy,
            recovery_plan=dispatch.recovery_plan,
            dispatch_plan_payload=dispatch.dispatch_plan_payload,
            result_summary=dispatch.result_summary,
            failure_reason=dispatch.failure_reason,
            reviewer_notes=dispatch.reviewer_notes,
            planned_by=dispatch.planned_by,
            updated_by=dispatch.updated_by,
            approved_by=dispatch.approved_by,
            dispatched_by=dispatch.dispatched_by,
            cancelled_by=dispatch.cancelled_by,
            archived_by=dispatch.archived_by,
            approved_at=dispatch.approved_at,
            rejected_at=dispatch.rejected_at,
            dispatched_at=dispatch.dispatched_at,
            failed_at=dispatch.failed_at,
            cancelled_at=dispatch.cancelled_at,
            archived_at=dispatch.archived_at,
            metadata=dispatch.dispatch_metadata,
            created_at=dispatch.created_at,
            updated_at=dispatch.updated_at,
        )


class CommercialOperationComfyUIAdapterDispatchListResponse(BaseModel):
    """Commercial operation metadata-only ComfyUI adapter dispatch list response."""

    operation_id: UUID
    items: list[CommercialOperationComfyUIAdapterDispatchResponse]


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
