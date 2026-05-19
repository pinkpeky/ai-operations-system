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
    CommercialOperationContentDraftStatus,
    CommercialOperationDryRunStatus,
    CommercialOperationLinkType,
    CommercialOperationPriority,
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
