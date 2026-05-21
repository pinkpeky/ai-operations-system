"""Commercial operation ORM models."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, JSON, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, IdTimestampMixin
from app.models.enums import (
    CommercialOperationApprovalStatus,
    CommercialOperationAssetRequestStatus,
    CommercialOperationComfyUIAdapterConfigStatus,
    CommercialOperationComfyUIAdapterDispatchStatus,
    CommercialOperationComfyUIConnectionProbeStatus,
    CommercialOperationComfyUIExecutionPlanStatus,
    CommercialOperationComfyUIHandoffStatus,
    CommercialOperationComfyUIJobRequestStatus,
    CommercialOperationComfyUIPreflightStatus,
    CommercialOperationComfyUIRuntimeGateStatus,
    CommercialOperationContentDraftStatus,
    CommercialOperationDeliverableStatus,
    CommercialOperationDryRunStatus,
    CommercialOperationEvidenceSnapshotStatus,
    CommercialOperationExecutionRequestStatus,
    CommercialOperationExecutionRunStatus,
    CommercialOperationLinkType,
    CommercialOperationMonitoringObservationStatus,
    CommercialOperationOptimizationDecisionStatus,
    CommercialOperationPriority,
    CommercialOperationResultStatus,
    CommercialOperationRiskLevel,
    CommercialOperationStatus,
)


class CommercialOperation(IdTimestampMixin, Base):
    """Workspace-scoped commercial automation project.

    Phase 61A turns a user's business goal into a durable project record.
    Later phases can attach workflow runs, approvals, content artifacts,
    OpenClaw execution, ComfyUI assets, monitoring, and recovery state.
    """

    __tablename__ = "commercial_operations"

    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Workspace ID")
    user_id: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Creator user ID")
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="Operation title")
    objective: Mapped[str] = mapped_column(Text, nullable=False, comment="Business objective")
    target_audience: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Target audience")
    channels: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False, comment="Target channels")
    status: Mapped[str] = mapped_column(
        String(32),
        default=CommercialOperationStatus.DRAFT.value,
        index=True,
        nullable=False,
        comment="Operation lifecycle status",
    )
    priority: Mapped[str] = mapped_column(
        String(16),
        default=CommercialOperationPriority.NORMAL.value,
        index=True,
        nullable=False,
        comment="Operation priority",
    )
    risk_level: Mapped[str] = mapped_column(
        String(16),
        default=CommercialOperationRiskLevel.MEDIUM.value,
        index=True,
        nullable=False,
        comment="Execution risk level",
    )
    budget_amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True, comment="Budget amount")
    budget_currency: Mapped[str] = mapped_column(String(16), default="CNY", nullable=False, comment="Budget currency")
    start_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Planned start")
    end_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Planned end")
    knowledge_collection: Mapped[str | None] = mapped_column(String(128), nullable=True, comment="RAG collection")
    success_metrics: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False, comment="Success metrics")
    constraints: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False, comment="Execution constraints")
    plan_outline: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False, comment="Draft plan")
    operation_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
        comment="Operation metadata",
    )


class CommercialOperationLink(IdTimestampMixin, Base):
    """Evidence or handoff link attached to a commercial operation."""

    __tablename__ = "commercial_operation_links"

    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Workspace ID")
    operation_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="Commercial operation ID",
    )
    link_type: Mapped[str] = mapped_column(
        String(64),
        default=CommercialOperationLinkType.EXTERNAL.value,
        index=True,
        nullable=False,
        comment="conversation / artifact / task_run / workflow_run / rag_document / knowledge_source / approval / external",
    )
    target_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False, comment="Target entity type")
    target_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Target entity ID")
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="Operator-facing link title")
    summary: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Short context summary")
    source_name: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Source surface")
    link_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
        comment="Link metadata",
    )


class CommercialOperationApproval(IdTimestampMixin, Base):
    """Human approval gate for a commercial operation plan step."""

    __tablename__ = "commercial_operation_approvals"

    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Workspace ID")
    operation_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="Commercial operation ID",
    )
    step_key: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Plan step key")
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="Approval title")
    requested_action: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Action or decision being requested")
    approval_status: Mapped[str] = mapped_column(
        String(32),
        default=CommercialOperationApprovalStatus.PENDING.value,
        index=True,
        nullable=False,
        comment="pending / approved / rejected / cancelled",
    )
    risk_level: Mapped[str] = mapped_column(
        String(16),
        default=CommercialOperationRiskLevel.MEDIUM.value,
        index=True,
        nullable=False,
        comment="Approval risk level",
    )
    requested_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Requester user ID")
    reviewer_user_id: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Reviewer user ID")
    reviewer_notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Reviewer decision notes")
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Approved at")
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Rejected at")
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Cancelled at")
    approval_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
        comment="Approval metadata",
    )


class CommercialOperationDryRun(IdTimestampMixin, Base):
    """Safe dry-run record for an approved commercial operation plan step."""

    __tablename__ = "commercial_operation_dry_runs"

    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Workspace ID")
    operation_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="Commercial operation ID",
    )
    approval_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operation_approvals.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="Approved operation approval ID",
    )
    step_key: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Plan step key")
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="Dry-run title")
    dry_run_status: Mapped[str] = mapped_column(
        String(32),
        default=CommercialOperationDryRunStatus.CREATED.value,
        index=True,
        nullable=False,
        comment="created / completed / failed / cancelled",
    )
    execution_mode: Mapped[str] = mapped_column(
        String(32),
        default="metadata_only",
        index=True,
        nullable=False,
        comment="metadata_only / dry_run",
    )
    execution_target: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Target channel or runtime")
    input_summary: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Operator-facing input summary")
    runbook: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False, comment="Non-executing dry-run steps")
    expected_outputs: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False, comment="Expected dry-run outputs")
    readiness_checks: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False, comment="Readiness checks")
    result_summary: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Dry-run result summary")
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Dry-run failure reason")
    requested_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Requester user ID")
    completed_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Completer user ID")
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Completed at")
    failed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Failed at")
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Cancelled at")
    dry_run_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
        comment="Dry-run metadata",
    )


class CommercialOperationContentDraft(IdTimestampMixin, Base):
    """Channel content draft attached to a commercial operation plan step."""

    __tablename__ = "commercial_operation_content_drafts"

    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Workspace ID")
    operation_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="Commercial operation ID",
    )
    step_key: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Plan step key")
    channel: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Target channel")
    content_format: Mapped[str] = mapped_column(
        String(64),
        default="copy",
        index=True,
        nullable=False,
        comment="copy / email / post / script / landing_page / ad",
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="Draft title")
    draft_status: Mapped[str] = mapped_column(
        String(32),
        default=CommercialOperationContentDraftStatus.DRAFT.value,
        index=True,
        nullable=False,
        comment="draft / ready_for_review / approved / rejected / archived",
    )
    audience_segment: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Audience segment")
    content_body: Mapped[str] = mapped_column(Text, nullable=False, comment="Draft content body")
    summary: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Draft summary")
    call_to_action: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Call to action")
    source_materials: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False, comment="Source materials")
    asset_requests: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="Non-executing asset request placeholders",
    )
    reviewer_notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Reviewer notes")
    created_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Creator user ID")
    updated_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Last updater user ID")
    approved_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Approver user ID")
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Approved at")
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Rejected at")
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Archived at")
    content_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
        comment="Content draft metadata",
    )


class CommercialOperationAssetRequest(IdTimestampMixin, Base):
    """First-class asset request for a commercial operation plan step."""

    __tablename__ = "commercial_operation_asset_requests"

    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Workspace ID")
    operation_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="Commercial operation ID",
    )
    content_draft_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("commercial_operation_content_drafts.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
        comment="Optional source content draft ID",
    )
    step_key: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Plan step key")
    channel: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Target channel")
    asset_type: Mapped[str] = mapped_column(
        String(64),
        default="image",
        index=True,
        nullable=False,
        comment="image / video / audio / document / design / copy_asset / other",
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="Asset request title")
    request_status: Mapped[str] = mapped_column(
        String(32),
        default=CommercialOperationAssetRequestStatus.DRAFT.value,
        index=True,
        nullable=False,
        comment="draft / ready_for_review / approved / rejected / prepared / failed / archived",
    )
    purpose: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Business purpose or placement")
    dimensions: Mapped[str | None] = mapped_column(String(128), nullable=True, comment="Requested size or format")
    style_constraints: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Style and brand constraints")
    generation_prompt: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Future generation prompt")
    negative_prompt: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Future negative prompt")
    source_materials: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False, comment="Source materials")
    readiness_checks: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False, comment="Readiness checks")
    handoff_payload: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
        comment="Non-executing future ComfyUI handoff payload",
    )
    result_summary: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Preparation result summary")
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Preparation failure reason")
    reviewer_notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Reviewer notes")
    requested_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Requester user ID")
    updated_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Last updater user ID")
    approved_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Approver user ID")
    prepared_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Preparation user ID")
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Approved at")
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Rejected at")
    prepared_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Prepared at")
    failed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Failed at")
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Archived at")
    asset_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
        comment="Asset request metadata",
    )


class CommercialOperationComfyUIHandoff(IdTimestampMixin, Base):
    """Metadata-only ComfyUI handoff record for an approved asset request."""

    __tablename__ = "commercial_operation_comfyui_handoffs"

    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Workspace ID")
    operation_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="Commercial operation ID",
    )
    asset_request_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operation_asset_requests.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
        comment="Approved or prepared asset request ID",
    )
    content_draft_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("commercial_operation_content_drafts.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
        comment="Optional source content draft ID snapshot",
    )
    step_key: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Plan step key")
    channel: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Target channel")
    asset_type: Mapped[str] = mapped_column(
        String(64),
        default="image",
        index=True,
        nullable=False,
        comment="image / video / audio / document / design / copy_asset / other",
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="ComfyUI handoff title")
    handoff_status: Mapped[str] = mapped_column(
        String(32),
        default=CommercialOperationComfyUIHandoffStatus.DRAFT.value,
        index=True,
        nullable=False,
        comment="draft / ready_for_review / approved / rejected / prepared / failed / archived",
    )
    workflow_name: Mapped[str] = mapped_column(
        String(128),
        default="future_comfyui_handoff",
        index=True,
        nullable=False,
        comment="Future ComfyUI workflow name",
    )
    dimensions: Mapped[str | None] = mapped_column(String(128), nullable=True, comment="Requested size or format")
    generation_prompt: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Future generation prompt")
    negative_prompt: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Future negative prompt")
    workflow_payload: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
        comment="Metadata-only future workflow payload",
    )
    prompt_payload: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
        comment="Metadata-only future prompt payload",
    )
    source_materials: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False, comment="Source materials")
    readiness_checks: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False, comment="Readiness checks")
    handoff_payload: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
        comment="Non-executing guarded ComfyUI handoff payload",
    )
    result_summary: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Preparation result summary")
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Preparation failure reason")
    reviewer_notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Reviewer notes")
    requested_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Requester user ID")
    updated_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Last updater user ID")
    approved_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Approver user ID")
    prepared_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Preparation user ID")
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Approved at")
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Rejected at")
    prepared_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Prepared at")
    failed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Failed at")
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Archived at")
    handoff_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
        comment="ComfyUI handoff metadata",
    )


class CommercialOperationComfyUIPreflight(IdTimestampMixin, Base):
    """Metadata-only ComfyUI adapter readiness preflight for a handoff."""

    __tablename__ = "commercial_operation_comfyui_preflights"

    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Workspace ID")
    operation_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="Commercial operation ID",
    )
    handoff_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operation_comfyui_handoffs.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="ComfyUI handoff ID",
    )
    adapter_config_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("commercial_operation_comfyui_adapter_configs.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
        comment="Optional maintained ComfyUI adapter config snapshot",
    )
    asset_request_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operation_asset_requests.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
        comment="Source asset request ID snapshot",
    )
    step_key: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Plan step key")
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="ComfyUI preflight title")
    preflight_status: Mapped[str] = mapped_column(
        String(32),
        default=CommercialOperationComfyUIPreflightStatus.DRAFT.value,
        index=True,
        nullable=False,
        comment="draft / checked / blocked / failed / archived",
    )
    target_url: Mapped[str | None] = mapped_column(String(512), nullable=True, comment="Future ComfyUI endpoint URL")
    connection_mode: Mapped[str] = mapped_column(
        String(32),
        default="metadata_only",
        index=True,
        nullable=False,
        comment="metadata_only / future_guarded_adapter",
    )
    queue_name: Mapped[str | None] = mapped_column(String(128), nullable=True, comment="Future ComfyUI queue name")
    workflow_name: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="ComfyUI workflow name")
    model_refs: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False, comment="Expected model/checkpoint refs")
    adapter_config: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
        comment="Metadata-only adapter configuration",
    )
    check_items: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False, comment="Preflight check items")
    preflight_payload: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
        comment="Non-executing ComfyUI preflight payload",
    )
    result_summary: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Preflight result summary")
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Preflight failure reason")
    checked_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Checker user ID")
    updated_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Last updater user ID")
    archived_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Archiver user ID")
    checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Checked at")
    failed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Failed at")
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Archived at")
    preflight_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
        comment="ComfyUI preflight metadata",
    )


class CommercialOperationComfyUIAdapterConfig(IdTimestampMixin, Base):
    """Metadata-only ComfyUI adapter configuration for server maintainers."""

    __tablename__ = "commercial_operation_comfyui_adapter_configs"

    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Workspace ID")
    operation_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="Commercial operation ID",
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="Adapter config title")
    config_status: Mapped[str] = mapped_column(
        String(32),
        default=CommercialOperationComfyUIAdapterConfigStatus.DRAFT.value,
        index=True,
        nullable=False,
        comment="draft / ready / blocked / failed / archived",
    )
    target_url: Mapped[str | None] = mapped_column(String(512), nullable=True, comment="Future ComfyUI endpoint URL")
    auth_mode: Mapped[str] = mapped_column(
        String(32),
        default="none",
        index=True,
        nullable=False,
        comment="none / token_ref / basic_ref / custom_ref",
    )
    secret_ref: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Secret reference only; no secret value is stored",
    )
    queue_name: Mapped[str | None] = mapped_column(String(128), nullable=True, comment="Future ComfyUI queue name")
    default_workflow_name: Mapped[str | None] = mapped_column(
        String(128),
        index=True,
        nullable=True,
        comment="Default allowed workflow name",
    )
    allowed_workflows: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="Allowed future workflow names",
    )
    model_inventory: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="Model/checkpoint inventory for maintenance",
    )
    runtime_limits: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
        comment="Metadata-only runtime limits and disabled execution flags",
    )
    maintenance_notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Server maintenance notes")
    validation_checks: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="Local validation checks for the adapter config",
    )
    config_payload: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
        comment="Non-executing adapter config payload",
    )
    result_summary: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Validation result summary")
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Validation failure reason")
    created_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Creator user ID")
    updated_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Last updater user ID")
    validated_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Validator user ID")
    archived_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Archiver user ID")
    validated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Validated at")
    failed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Failed at")
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Archived at")
    config_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
        comment="Adapter config metadata",
    )


class CommercialOperationComfyUIJobRequest(IdTimestampMixin, Base):
    """Metadata-only ComfyUI job request assembled from checked preflight."""

    __tablename__ = "commercial_operation_comfyui_job_requests"

    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Workspace ID")
    operation_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="Commercial operation ID",
    )
    preflight_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operation_comfyui_preflights.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
        comment="Checked ComfyUI preflight ID",
    )
    handoff_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operation_comfyui_handoffs.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
        comment="Approved or prepared ComfyUI handoff ID",
    )
    adapter_config_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("commercial_operation_comfyui_adapter_configs.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
        comment="Linked maintained ComfyUI adapter config ID",
    )
    asset_request_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operation_asset_requests.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
        comment="Source asset request ID snapshot",
    )
    step_key: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Plan step key")
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="ComfyUI job request title")
    job_status: Mapped[str] = mapped_column(
        String(32),
        default=CommercialOperationComfyUIJobRequestStatus.DRAFT.value,
        index=True,
        nullable=False,
        comment="draft / ready_for_review / approved / queued / failed / cancelled / archived",
    )
    priority: Mapped[str] = mapped_column(String(32), default="normal", index=True, nullable=False, comment="Job priority")
    target_url: Mapped[str | None] = mapped_column(String(512), nullable=True, comment="Future ComfyUI endpoint URL")
    queue_name: Mapped[str | None] = mapped_column(String(128), nullable=True, comment="Future ComfyUI queue name")
    workflow_name: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="ComfyUI workflow name")
    connection_mode: Mapped[str] = mapped_column(
        String(32),
        default="metadata_only",
        index=True,
        nullable=False,
        comment="metadata_only / future_guarded_adapter",
    )
    prompt_payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False, comment="Prompt payload snapshot")
    workflow_payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False, comment="Workflow payload snapshot")
    runtime_payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False, comment="Metadata-only runtime payload")
    safety_checks: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False, comment="Safety checks")
    output_expectations: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False, comment="Expected future outputs")
    recovery_plan: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False, comment="Failure recovery guidance")
    job_payload: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
        comment="Non-executing ComfyUI job request payload",
    )
    result_summary: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Queue preparation result summary")
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Failure or blocker reason")
    reviewer_notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Reviewer notes")
    requested_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Requester user ID")
    updated_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Last updater user ID")
    approved_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Approver user ID")
    queued_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Queueing user ID")
    cancelled_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Canceller user ID")
    archived_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Archiver user ID")
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Approved at")
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Rejected at")
    queued_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Queued at")
    failed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Failed at")
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Cancelled at")
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Archived at")
    job_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
        comment="ComfyUI job request metadata",
    )


class CommercialOperationComfyUIExecutionPlan(IdTimestampMixin, Base):
    """Metadata-only ComfyUI execution plan and queue simulation record."""

    __tablename__ = "commercial_operation_comfyui_execution_plans"

    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Workspace ID")
    operation_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="Commercial operation ID",
    )
    job_request_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operation_comfyui_job_requests.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
        comment="Approved or queued ComfyUI job request ID",
    )
    preflight_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operation_comfyui_preflights.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
        comment="Checked ComfyUI preflight ID",
    )
    handoff_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operation_comfyui_handoffs.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
        comment="ComfyUI handoff ID",
    )
    adapter_config_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("commercial_operation_comfyui_adapter_configs.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
        comment="Linked maintained ComfyUI adapter config ID",
    )
    asset_request_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operation_asset_requests.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
        comment="Source asset request ID snapshot",
    )
    step_key: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Plan step key")
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="ComfyUI execution plan title")
    plan_status: Mapped[str] = mapped_column(
        String(32),
        default=CommercialOperationComfyUIExecutionPlanStatus.DRAFT.value,
        index=True,
        nullable=False,
        comment="draft / ready_for_review / approved / simulated / failed / cancelled / archived",
    )
    priority: Mapped[str] = mapped_column(String(32), default="normal", index=True, nullable=False, comment="Plan priority")
    target_url: Mapped[str | None] = mapped_column(String(512), nullable=True, comment="Future ComfyUI endpoint URL")
    queue_name: Mapped[str | None] = mapped_column(String(128), nullable=True, comment="Future ComfyUI queue name")
    workflow_name: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="ComfyUI workflow name")
    execution_mode: Mapped[str] = mapped_column(
        String(32),
        default="metadata_only",
        index=True,
        nullable=False,
        comment="metadata_only / future_guarded_adapter",
    )
    queue_payload: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
        comment="Metadata-only future queue payload snapshot",
    )
    execution_steps: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="Operator execution plan steps",
    )
    simulation_checks: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="Local simulation checks",
    )
    operator_checklist: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="Human operator checklist",
    )
    rollback_plan: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
        comment="Rollback and recovery plan",
    )
    simulation_payload: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
        comment="Metadata-only simulation payload",
    )
    plan_payload: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
        comment="Non-executing ComfyUI execution plan payload",
    )
    result_summary: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Simulation result summary")
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Failure or blocker reason")
    reviewer_notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Reviewer notes")
    planned_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Planner user ID")
    updated_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Last updater user ID")
    approved_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Approver user ID")
    simulated_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Simulator user ID")
    cancelled_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Canceller user ID")
    archived_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Archiver user ID")
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Approved at")
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Rejected at")
    simulated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Simulated at")
    failed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Failed at")
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Cancelled at")
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Archived at")
    plan_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
        comment="ComfyUI execution plan metadata",
    )


class CommercialOperationComfyUIConnectionProbe(IdTimestampMixin, Base):
    """Metadata-only ComfyUI connection probe and read-only queue snapshot plan."""

    __tablename__ = "commercial_operation_comfyui_connection_probes"

    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Workspace ID")
    operation_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="Commercial operation ID",
    )
    execution_plan_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operation_comfyui_execution_plans.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
        comment="Approved or simulated ComfyUI execution plan ID",
    )
    job_request_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operation_comfyui_job_requests.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
        comment="ComfyUI job request ID snapshot",
    )
    preflight_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operation_comfyui_preflights.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
        comment="Checked ComfyUI preflight ID",
    )
    handoff_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operation_comfyui_handoffs.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
        comment="ComfyUI handoff ID",
    )
    adapter_config_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("commercial_operation_comfyui_adapter_configs.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
        comment="Linked maintained ComfyUI adapter config ID",
    )
    asset_request_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operation_asset_requests.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
        comment="Source asset request ID snapshot",
    )
    step_key: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Plan step key")
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="ComfyUI connection probe title")
    probe_status: Mapped[str] = mapped_column(
        String(32),
        default=CommercialOperationComfyUIConnectionProbeStatus.DRAFT.value,
        index=True,
        nullable=False,
        comment="draft / ready_for_review / approved / probed / failed / cancelled / archived",
    )
    target_url: Mapped[str | None] = mapped_column(String(512), nullable=True, comment="Future ComfyUI endpoint URL")
    queue_name: Mapped[str | None] = mapped_column(String(128), nullable=True, comment="Future ComfyUI queue name")
    workflow_name: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="ComfyUI workflow name")
    probe_mode: Mapped[str] = mapped_column(
        String(32),
        default="metadata_only",
        index=True,
        nullable=False,
        comment="metadata_only / future_read_only_probe",
    )
    health_endpoint: Mapped[str] = mapped_column(String(128), default="/system_stats", nullable=False, comment="Future read-only health endpoint")
    queue_endpoint: Mapped[str] = mapped_column(String(128), default="/queue", nullable=False, comment="Future read-only queue endpoint")
    expected_routes: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False, comment="Expected read-only routes")
    readiness_checks: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False, comment="Local probe readiness checks")
    probe_payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False, comment="Metadata-only probe request payload")
    health_snapshot: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False, comment="Metadata-only health snapshot")
    queue_snapshot: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False, comment="Metadata-only queue snapshot")
    response_schema: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False, comment="Expected future response schema")
    probe_plan_payload: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
        comment="Non-executing ComfyUI connection probe payload",
    )
    result_summary: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Probe result summary")
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Failure or blocker reason")
    reviewer_notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Reviewer notes")
    planned_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Planner user ID")
    updated_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Last updater user ID")
    approved_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Approver user ID")
    probed_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Probe recorder user ID")
    cancelled_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Canceller user ID")
    archived_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Archiver user ID")
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Approved at")
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Rejected at")
    probed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Probed at")
    failed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Failed at")
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Cancelled at")
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Archived at")
    probe_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
        comment="ComfyUI connection probe metadata",
    )


class CommercialOperationComfyUIAdapterDispatch(IdTimestampMixin, Base):
    """Metadata-only ComfyUI adapter dispatch handoff record."""

    __tablename__ = "commercial_operation_comfyui_adapter_dispatches"

    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Workspace ID")
    operation_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="Commercial operation ID",
    )
    connection_probe_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operation_comfyui_connection_probes.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
        comment="Probed ComfyUI connection probe ID",
    )
    execution_plan_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operation_comfyui_execution_plans.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
        comment="ComfyUI execution plan ID snapshot",
    )
    job_request_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operation_comfyui_job_requests.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
        comment="ComfyUI job request ID snapshot",
    )
    preflight_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operation_comfyui_preflights.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
        comment="Checked ComfyUI preflight ID snapshot",
    )
    handoff_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operation_comfyui_handoffs.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
        comment="ComfyUI handoff ID snapshot",
    )
    adapter_config_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("commercial_operation_comfyui_adapter_configs.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
        comment="Linked maintained ComfyUI adapter config ID",
    )
    asset_request_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operation_asset_requests.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
        comment="Source asset request ID snapshot",
    )
    step_key: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Plan step key")
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="ComfyUI adapter dispatch title")
    dispatch_status: Mapped[str] = mapped_column(
        String(32),
        default=CommercialOperationComfyUIAdapterDispatchStatus.DRAFT.value,
        index=True,
        nullable=False,
        comment="draft / ready_for_review / approved / dispatched / failed / cancelled / archived",
    )
    dispatch_mode: Mapped[str] = mapped_column(
        String(32),
        default="metadata_only",
        index=True,
        nullable=False,
        comment="metadata_only / future_guarded_dispatch",
    )
    target_url: Mapped[str | None] = mapped_column(String(512), nullable=True, comment="Future ComfyUI endpoint URL")
    queue_name: Mapped[str | None] = mapped_column(String(128), nullable=True, comment="Future ComfyUI queue name")
    workflow_name: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="ComfyUI workflow name")
    prompt_payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False, comment="Metadata-only prompt payload")
    workflow_payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False, comment="Metadata-only workflow payload")
    queue_payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False, comment="Metadata-only queue payload")
    dispatch_payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False, comment="Sanitized adapter dispatch payload")
    guardrails: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False, comment="Dispatch guardrail checks")
    operator_checklist: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False, comment="Human operator checklist")
    retry_policy: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False, comment="Retry policy for future dispatch")
    recovery_plan: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False, comment="Recovery plan for future dispatch")
    dispatch_plan_payload: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
        comment="Non-executing ComfyUI adapter dispatch payload",
    )
    result_summary: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Dispatch result summary")
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Failure or blocker reason")
    reviewer_notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Reviewer notes")
    planned_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Planner user ID")
    updated_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Last updater user ID")
    approved_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Approver user ID")
    dispatched_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Dispatch recorder user ID")
    cancelled_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Canceller user ID")
    archived_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Archiver user ID")
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Approved at")
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Rejected at")
    dispatched_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Dispatch recorded at")
    failed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Failed at")
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Cancelled at")
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Archived at")
    dispatch_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
        comment="ComfyUI adapter dispatch metadata",
    )


class CommercialOperationComfyUIRuntimeGate(IdTimestampMixin, Base):
    """Metadata-only ComfyUI runtime gate readiness record."""

    __tablename__ = "commercial_operation_comfyui_runtime_gates"

    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Workspace ID")
    operation_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="Commercial operation ID",
    )
    adapter_dispatch_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operation_comfyui_adapter_dispatches.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
        comment="Dispatched ComfyUI adapter dispatch ID",
    )
    connection_probe_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operation_comfyui_connection_probes.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
        comment="ComfyUI connection probe ID snapshot",
    )
    execution_plan_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operation_comfyui_execution_plans.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
        comment="ComfyUI execution plan ID snapshot",
    )
    job_request_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operation_comfyui_job_requests.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
        comment="ComfyUI job request ID snapshot",
    )
    preflight_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operation_comfyui_preflights.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
        comment="Checked ComfyUI preflight ID snapshot",
    )
    handoff_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operation_comfyui_handoffs.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
        comment="ComfyUI handoff ID snapshot",
    )
    adapter_config_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("commercial_operation_comfyui_adapter_configs.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
        comment="Linked maintained ComfyUI adapter config ID",
    )
    asset_request_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operation_asset_requests.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
        comment="Source asset request ID snapshot",
    )
    step_key: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Plan step key")
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="ComfyUI runtime gate title")
    gate_status: Mapped[str] = mapped_column(
        String(32),
        default=CommercialOperationComfyUIRuntimeGateStatus.DRAFT.value,
        index=True,
        nullable=False,
        comment="draft / ready_for_review / approved / armed / disabled / failed / archived",
    )
    runtime_mode: Mapped[str] = mapped_column(
        String(32),
        default="metadata_only",
        index=True,
        nullable=False,
        comment="metadata_only / future_guarded_runtime",
    )
    target_url: Mapped[str | None] = mapped_column(String(512), nullable=True, comment="Future ComfyUI endpoint URL")
    queue_name: Mapped[str | None] = mapped_column(String(128), nullable=True, comment="Future ComfyUI queue name")
    workflow_name: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="ComfyUI workflow name")
    environment_payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False, comment="Runtime environment snapshot")
    network_policy: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False, comment="Network boundary policy")
    queue_policy: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False, comment="Queue boundary policy")
    secret_policy: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False, comment="Secret reference policy")
    approval_policy: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False, comment="Human approval policy")
    validation_checks: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False, comment="Runtime gate validation checks")
    operator_checklist: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False, comment="Human operator checklist")
    rollback_plan: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False, comment="Rollback and disable plan")
    gate_payload: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
        comment="Non-executing ComfyUI runtime gate payload",
    )
    result_summary: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Runtime gate result summary")
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Failure or blocker reason")
    reviewer_notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Reviewer notes")
    planned_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Planner user ID")
    updated_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Last updater user ID")
    approved_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Approver user ID")
    armed_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Runtime gate arming user ID")
    disabled_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Runtime gate disabler user ID")
    archived_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Archiver user ID")
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Approved at")
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Rejected at")
    armed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Runtime gate armed at")
    disabled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Runtime gate disabled at")
    failed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Failed at")
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Archived at")
    gate_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
        comment="ComfyUI runtime gate metadata",
    )


class CommercialOperationDeliverable(IdTimestampMixin, Base):
    """Reviewable commercial operation deliverable linked to Output Library."""

    __tablename__ = "commercial_operation_deliverables"

    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Workspace ID")
    operation_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="Commercial operation ID",
    )
    content_draft_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operation_content_drafts.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
        comment="Approved content draft ID",
    )
    output_artifact_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("output_artifacts.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
        comment="Generated Output Library artifact ID",
    )
    step_key: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Plan step key")
    channel: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Target channel")
    deliverable_type: Mapped[str] = mapped_column(
        String(64),
        default="content_package",
        index=True,
        nullable=False,
        comment="content_package / post / email / landing_page / ad / script / asset_brief / report",
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="Deliverable title")
    deliverable_status: Mapped[str] = mapped_column(
        String(32),
        default=CommercialOperationDeliverableStatus.DRAFT.value,
        index=True,
        nullable=False,
        comment="draft / ready_for_review / approved / rejected / packaged / failed / archived",
    )
    summary: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Operator-facing summary")
    delivery_notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Delivery and handoff notes")
    asset_request_ids: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False, comment="Linked asset request IDs")
    quality_checks: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False, comment="Quality checks")
    package_payload: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
        comment="Non-executing delivery package payload",
    )
    result_summary: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Package result summary")
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Package failure reason")
    reviewer_notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Reviewer notes")
    created_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Creator user ID")
    updated_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Last updater user ID")
    approved_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Approver user ID")
    packaged_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Packager user ID")
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Approved at")
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Rejected at")
    packaged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Packaged at")
    failed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Failed at")
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Archived at")
    deliverable_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
        comment="Deliverable metadata",
    )


class CommercialOperationEvidenceSnapshot(IdTimestampMixin, Base):
    """Reviewable evidence snapshot attached to a packaged commercial deliverable."""

    __tablename__ = "commercial_operation_evidence_snapshots"

    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Workspace ID")
    operation_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="Commercial operation ID",
    )
    deliverable_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operation_deliverables.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
        comment="Packaged commercial deliverable ID",
    )
    content_draft_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operation_content_drafts.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
        comment="Approved content draft ID snapshot",
    )
    output_artifact_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("output_artifacts.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
        comment="Linked Output Library artifact ID",
    )
    step_key: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Plan step key")
    channel: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Target channel")
    evidence_type: Mapped[str] = mapped_column(
        String(64),
        default="rag_snapshot",
        index=True,
        nullable=False,
        comment="rag_snapshot / source_review / operator_note / compliance_note / other",
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="Evidence snapshot title")
    snapshot_status: Mapped[str] = mapped_column(
        String(32),
        default=CommercialOperationEvidenceSnapshotStatus.DRAFT.value,
        index=True,
        nullable=False,
        comment="draft / ready_for_review / approved / rejected / archived",
    )
    knowledge_collection: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="RAG collection snapshot")
    query: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Evidence retrieval or review query")
    evidence_summary: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Operator evidence summary")
    relevance_notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Why this evidence supports the deliverable")
    source_document_ids: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False, comment="Referenced RAG document IDs")
    source_links: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False, comment="Referenced evidence links")
    evidence_items: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False, comment="Evidence item snapshots")
    coverage_checks: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False, comment="Coverage and safety checks")
    snapshot_payload: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
        comment="Evidence snapshot payload and boundaries",
    )
    reviewer_notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Reviewer notes")
    created_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Creator user ID")
    updated_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Last updater user ID")
    approved_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Approver user ID")
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Approved at")
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Rejected at")
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Archived at")
    snapshot_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
        comment="Evidence snapshot metadata",
    )


class CommercialOperationExecutionRequest(IdTimestampMixin, Base):
    """Metadata-only monitored execution request for a packaged deliverable."""

    __tablename__ = "commercial_operation_execution_requests"

    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Workspace ID")
    operation_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="Commercial operation ID",
    )
    deliverable_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operation_deliverables.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
        comment="Packaged commercial deliverable ID",
    )
    output_artifact_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("output_artifacts.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
        comment="Linked Output Library artifact ID",
    )
    step_key: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Plan step key")
    channel: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Target channel")
    execution_type: Mapped[str] = mapped_column(
        String(64),
        default="manual_handoff",
        index=True,
        nullable=False,
        comment="manual_handoff / browser_worker / openclaw / platform_post / email_send / other",
    )
    execution_mode: Mapped[str] = mapped_column(
        String(32),
        default="metadata_only",
        index=True,
        nullable=False,
        comment="metadata_only / approval_handoff / future_runtime",
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="Execution request title")
    request_status: Mapped[str] = mapped_column(
        String(32),
        default=CommercialOperationExecutionRequestStatus.DRAFT.value,
        index=True,
        nullable=False,
        comment="draft / ready_for_review / approved / rejected / prepared / failed / cancelled / archived",
    )
    execution_target: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Future target runtime or account")
    input_summary: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Operator-facing execution input summary")
    runbook: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False, comment="Metadata-only execution runbook")
    readiness_checks: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False, comment="Readiness checks")
    expected_outputs: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False, comment="Expected monitored outputs")
    evidence_snapshot_ids: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="Approved evidence snapshot IDs included in the handoff",
    )
    operator_checklist: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="Operator checklist before future runtime handoff",
    )
    handoff_payload: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
        comment="Non-executing future runtime handoff payload",
    )
    result_summary: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Preparation result summary")
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Preparation failure reason")
    reviewer_notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Reviewer notes")
    requested_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Requester user ID")
    updated_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Last updater user ID")
    approved_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Approver user ID")
    prepared_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Preparation user ID")
    cancelled_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Canceller user ID")
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Approved at")
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Rejected at")
    prepared_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Prepared at")
    failed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Failed at")
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Cancelled at")
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Archived at")
    execution_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
        comment="Execution request metadata",
    )


class CommercialOperationExecutionRun(IdTimestampMixin, Base):
    """Metadata-only execution run monitor record for a prepared execution request."""

    __tablename__ = "commercial_operation_execution_runs"

    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Workspace ID")
    operation_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="Commercial operation ID",
    )
    execution_request_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operation_execution_requests.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
        comment="Prepared execution request ID",
    )
    deliverable_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operation_deliverables.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
        comment="Packaged commercial deliverable ID",
    )
    output_artifact_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("output_artifacts.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
        comment="Linked Output Library artifact ID",
    )
    step_key: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Plan step key")
    channel: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Target channel")
    execution_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False, comment="Execution type snapshot")
    execution_mode: Mapped[str] = mapped_column(String(32), index=True, nullable=False, comment="Execution mode snapshot")
    execution_target: Mapped[str | None] = mapped_column(
        String(128),
        index=True,
        nullable=True,
        comment="Future target runtime or account",
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="Execution run title")
    run_status: Mapped[str] = mapped_column(
        String(32),
        default=CommercialOperationExecutionRunStatus.QUEUED.value,
        index=True,
        nullable=False,
        comment="queued / running / succeeded / failed / retrying / cancelled / archived",
    )
    input_payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False, comment="Run input payload snapshot")
    runbook_snapshot: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False, comment="Runbook snapshot")
    readiness_checks: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False, comment="Readiness checks snapshot")
    expected_outputs: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False, comment="Expected monitored outputs")
    evidence_snapshot_ids: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="Evidence snapshot IDs inherited from execution request",
    )
    operator_checklist_snapshot: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="Operator checklist inherited from execution request",
    )
    runtime_payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False, comment="Metadata-only runtime payload")
    result_payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False, comment="Operator result payload")
    recovery_plan: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False, comment="Failure recovery guidance")
    retry_count: Mapped[int] = mapped_column(default=0, nullable=False, comment="Retry count")
    max_retries: Mapped[int] = mapped_column(default=0, nullable=False, comment="Maximum operator retries")
    result_summary: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Run result summary")
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Run failure reason")
    operator_notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Operator notes")
    queued_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Queueing user ID")
    started_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Starter user ID")
    completed_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Completer user ID")
    cancelled_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Canceller user ID")
    queued_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Queued at")
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Started at")
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Completed at")
    failed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Failed at")
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Cancelled at")
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Archived at")
    run_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
        comment="Execution run metadata",
    )


class CommercialOperationResult(IdTimestampMixin, Base):
    """Operator-reviewed commercial result record for a terminal execution run."""

    __tablename__ = "commercial_operation_results"

    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Workspace ID")
    operation_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="Commercial operation ID",
    )
    execution_run_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operation_execution_runs.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
        comment="Terminal execution run ID",
    )
    execution_request_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operation_execution_requests.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
        comment="Execution request ID snapshot",
    )
    deliverable_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operation_deliverables.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
        comment="Packaged commercial deliverable ID",
    )
    output_artifact_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("output_artifacts.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
        comment="Linked Output Library artifact ID",
    )
    step_key: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Plan step key")
    channel: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Target channel")
    result_type: Mapped[str] = mapped_column(
        String(64),
        index=True,
        default="operator_report",
        nullable=False,
        comment="Result record type",
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="Result report title")
    result_status: Mapped[str] = mapped_column(
        String(32),
        default=CommercialOperationResultStatus.DRAFT.value,
        index=True,
        nullable=False,
        comment="draft / ready_for_review / approved / rejected / archived",
    )
    summary: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Operator result summary")
    outcome_summary: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Observed commercial outcome")
    observed_metrics: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="Operator-observed metric snapshots",
    )
    commercial_signals: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="Qualitative commercial signals",
    )
    evidence_links: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="Result evidence links",
    )
    follow_up_actions: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="Follow-up actions",
    )
    result_payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False, comment="Result payload")
    recommendation_payload: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
        comment="Non-executing recommendation payload",
    )
    reviewer_notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Reviewer notes")
    created_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Creator user ID")
    updated_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Last updater user ID")
    approved_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Approver user ID")
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Approved at")
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Rejected at")
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Archived at")
    result_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
        comment="Result report metadata",
    )


class CommercialOperationMonitoringObservation(IdTimestampMixin, Base):
    """Operator-reviewed monitoring observation for an approved commercial result."""

    __tablename__ = "commercial_operation_monitoring_observations"

    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Workspace ID")
    operation_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="Commercial operation ID",
    )
    result_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operation_results.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
        comment="Approved commercial result ID",
    )
    execution_run_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operation_execution_runs.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
        comment="Terminal execution run ID snapshot",
    )
    execution_request_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operation_execution_requests.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
        comment="Execution request ID snapshot",
    )
    deliverable_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operation_deliverables.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
        comment="Packaged commercial deliverable ID",
    )
    output_artifact_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("output_artifacts.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
        comment="Linked Output Library artifact ID",
    )
    step_key: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Plan step key")
    channel: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Target channel")
    observation_type: Mapped[str] = mapped_column(
        String(64),
        default="manual_snapshot",
        index=True,
        nullable=False,
        comment="manual_snapshot / platform_note / customer_signal / anomaly_review / follow_up_review",
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="Monitoring observation title")
    observation_status: Mapped[str] = mapped_column(
        String(32),
        default=CommercialOperationMonitoringObservationStatus.DRAFT.value,
        index=True,
        nullable=False,
        comment="draft / ready_for_review / approved / rejected / archived",
    )
    observation_window_start: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Observation window start",
    )
    observation_window_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Observation window end",
    )
    metric_snapshots: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="Operator-observed metric snapshots",
    )
    qualitative_signals: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="Qualitative monitoring signals",
    )
    evidence_links: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="Monitoring evidence links",
    )
    anomaly_flags: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="Operator-flagged anomalies",
    )
    recommended_actions: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        comment="Recommended follow-up actions",
    )
    observation_payload: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
        comment="Observation payload and boundaries",
    )
    reviewer_notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Reviewer notes")
    created_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Creator user ID")
    updated_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Last updater user ID")
    approved_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Approver user ID")
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Approved at")
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Rejected at")
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Archived at")
    observation_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
        comment="Monitoring observation metadata",
    )


class CommercialOperationOptimizationDecision(IdTimestampMixin, Base):
    """Operator-reviewed optimization decision from an approved monitoring observation."""

    __tablename__ = "commercial_operation_optimization_decisions"

    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Workspace ID")
    operation_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="Commercial operation ID",
    )
    observation_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operation_monitoring_observations.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
        comment="Approved monitoring observation ID",
    )
    result_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operation_results.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
        comment="Approved commercial result ID snapshot",
    )
    execution_run_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operation_execution_runs.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
        comment="Terminal execution run ID snapshot",
    )
    execution_request_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operation_execution_requests.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
        comment="Execution request ID snapshot",
    )
    deliverable_id: Mapped[UUID] = mapped_column(
        ForeignKey("commercial_operation_deliverables.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
        comment="Packaged commercial deliverable ID",
    )
    output_artifact_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("output_artifacts.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
        comment="Linked Output Library artifact ID",
    )
    step_key: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Plan step key")
    channel: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Target channel")
    decision_type: Mapped[str] = mapped_column(
        String(64),
        default="iterate",
        index=True,
        nullable=False,
        comment="continue / iterate / retarget / retry / pause / escalate / stop",
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="Optimization decision title")
    decision_status: Mapped[str] = mapped_column(
        String(32),
        default=CommercialOperationOptimizationDecisionStatus.DRAFT.value,
        index=True,
        nullable=False,
        comment="draft / ready_for_review / approved / rejected / archived",
    )
    priority: Mapped[str] = mapped_column(String(16), default="normal", index=True, nullable=False, comment="Decision priority")
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Decision rationale")
    objective_updates: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False, comment="Objective adjustments")
    content_actions: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False, comment="Content optimization actions")
    asset_actions: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False, comment="Asset optimization actions")
    audience_actions: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False, comment="Audience optimization actions")
    execution_actions: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False, comment="Execution handoff actions")
    risk_controls: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False, comment="Risk controls before next step")
    decision_payload: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
        comment="Optimization decision payload and boundaries",
    )
    next_review_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Next review time")
    reviewer_notes: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Reviewer notes")
    created_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Creator user ID")
    updated_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Last updater user ID")
    approved_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Approver user ID")
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Approved at")
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Rejected at")
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="Archived at")
    decision_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
        comment="Optimization decision metadata",
    )
