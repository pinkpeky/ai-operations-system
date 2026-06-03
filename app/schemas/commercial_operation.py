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
    CommercialOperationComfyUIRuntimeActivation,
    CommercialOperationComfyUIRuntimeDryRun,
    CommercialOperationComfyUIRuntimeGate,
    CommercialOperationContentDraft,
    CommercialOperationDeliverable,
    CommercialOperationDryRun,
    CommercialOperationEvidenceSnapshot,
    CommercialOperationExecutionRequest,
    CommercialOperationExecutionRun,
    CommercialOperationLink,
    CommercialOperationMonitoringObservation,
    CommercialOperationOptimizationDecision,
    CommercialOperationOutputCandidate,
    CommercialOperationFinalSelection,
    CommercialOperationPlan,
    CommercialOperationPlatformMetricSnapshot,
    CommercialOperationProductionTask,
    CommercialOperationProjectMaterial,
    CommercialOperationPublishPackage,
    CommercialOperationResult,
    CommercialOperationWorkflowSelection,
)
from app.schemas.rag import SearchMode


CommercialOperationStatusLiteral = Literal["draft", "planning", "ready", "active", "paused", "completed", "archived"]
CommercialOperationPriorityLiteral = Literal["low", "normal", "high"]
CommercialOperationRiskLiteral = Literal["low", "medium", "high"]
CommercialOperationPlanStatusLiteral = Literal["draft", "ready_for_review", "approved", "rejected", "archived"]
CommercialOperationProjectMaterialStatusLiteral = Literal["available", "ready_for_review", "approved", "rejected", "archived"]
CommercialOperationProductionTaskStatusLiteral = Literal[
    "draft",
    "ready_for_review",
    "approved",
    "in_progress",
    "blocked",
    "completed",
    "rejected",
    "archived",
]
CommercialOperationProductionTaskTypeLiteral = Literal["copy", "image", "media"]
CommercialOperationMediaSubtypeLiteral = Literal["video", "audio", "audio_video", "digital_human", "postprocess"]
CommercialOperationWorkflowSelectionStatusLiteral = Literal["recommended", "ready_for_review", "approved", "rejected", "archived"]
CommercialOperationOutputCandidateStatusLiteral = Literal["generated", "ready_for_review", "selected", "rejected", "archived"]
CommercialOperationFinalSelectionStatusLiteral = Literal["draft", "ready_for_review", "approved", "rejected", "archived"]
CommercialOperationPublishPackageStatusLiteral = Literal[
    "draft",
    "ready_for_review",
    "approved",
    "prepared",
    "published",
    "rejected",
    "failed",
    "archived",
]
CommercialOperationPlatformMetricSnapshotStatusLiteral = Literal[
    "draft",
    "collected",
    "ready_for_review",
    "approved",
    "rejected",
    "archived",
]
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
CommercialOperationComfyUIRuntimeGateStatusLiteral = Literal[
    "draft",
    "ready_for_review",
    "approved",
    "rejected",
    "armed",
    "disabled",
    "failed",
    "archived",
]
CommercialOperationComfyUIRuntimeDryRunStatusLiteral = Literal[
    "draft",
    "ready_for_review",
    "approved",
    "rejected",
    "validated",
    "failed",
    "cancelled",
    "archived",
]
CommercialOperationComfyUIRuntimeActivationStatusLiteral = Literal[
    "draft",
    "ready_for_review",
    "approved",
    "rejected",
    "scheduled",
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
    production_closed_loop_action_audit_summary: dict[str, Any] = Field(default_factory=dict)
    production_closed_loop_primary_step: dict[str, Any] | None = None
    production_closed_loop_primary_step_staleness: dict[str, Any] = Field(default_factory=dict)
    production_closed_loop_primary_step_key: str | None = None
    production_closed_loop_staleness_status: str = "none"
    production_closed_loop_escalation_recommended: bool = False
    production_closed_loop_waiting_seconds: int = 0
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(
        cls,
        operation: CommercialOperation,
        *,
        production_closed_loop_action_audit_summary: dict[str, Any] | None = None,
    ) -> "CommercialOperationResponse":
        closed_loop_summary = dict(production_closed_loop_action_audit_summary or {})
        primary_step = (
            dict(closed_loop_summary["primary_step"])
            if isinstance(closed_loop_summary.get("primary_step"), dict)
            else None
        )
        staleness = (
            dict(closed_loop_summary["primary_step_staleness"])
            if isinstance(closed_loop_summary.get("primary_step_staleness"), dict)
            else {}
        )
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
            production_closed_loop_action_audit_summary=closed_loop_summary,
            production_closed_loop_primary_step=primary_step,
            production_closed_loop_primary_step_staleness=staleness,
            production_closed_loop_primary_step_key=str(primary_step.get("step_key")) if primary_step else None,
            production_closed_loop_staleness_status=str(staleness.get("status") or "none"),
            production_closed_loop_escalation_recommended=bool(staleness.get("escalation_recommended")),
            production_closed_loop_waiting_seconds=int(staleness.get("waiting_seconds") or 0),
            created_at=operation.created_at,
            updated_at=operation.updated_at,
        )


class CommercialOperationListResponse(BaseModel):
    """Commercial operation list response."""

    items: list[CommercialOperationResponse]


class CommercialOperationProductionClosedLoopInterventionQueueItemResponse(BaseModel):
    """One stale/watch production closed-loop operation that needs operator intervention."""

    operation_id: UUID
    workspace_id: str
    operation_title: str
    operation_status: str
    operation_priority: str
    operation_risk_level: str
    operation: CommercialOperationResponse
    action_audit_summary: dict[str, Any] = Field(default_factory=dict)
    primary_step: dict[str, Any] | None = None
    primary_step_key: str | None = None
    primary_step_label: str | None = None
    staleness_status: str = "none"
    waiting_seconds: int = 0
    escalation_recommended: bool = False
    priority_score: int = 0
    recommended_action_key: str | None = None
    latest_intervention_acknowledgement: dict[str, Any] = Field(default_factory=dict)
    acknowledgement_status: str | None = None
    acknowledgement_assignee: str | None = None
    acknowledgement_sla: dict[str, Any] = Field(default_factory=dict)
    latest_intervention_reminder_dispatch: dict[str, Any] = Field(default_factory=dict)
    reminder_dispatch_status: str | None = None
    reminder_dispatch_channel: str | None = None
    reminder_dispatch_cooldown: dict[str, Any] = Field(default_factory=dict)
    reminder_follow_up_recommended: bool = False
    reminder_next_allowed_at: datetime | None = None
    reason: str | None = None


class CommercialOperationProductionClosedLoopInterventionQueueResponse(BaseModel):
    """Workspace-level stale/watch production closed-loop intervention queue."""

    workspace_id: str
    queue_status: str
    statuses: list[str] = Field(default_factory=list)
    queue_count: int = 0
    stale_count: int = 0
    watch_count: int = 0
    acknowledgement_sla_status_counts: dict[str, int] = Field(default_factory=dict)
    reminder_dispatch_status_counts: dict[str, int] = Field(default_factory=dict)
    reminder_cooldown_status_counts: dict[str, int] = Field(default_factory=dict)
    acknowledgement_overdue_count: int = 0
    reminder_follow_up_count: int = 0
    queue_summary: dict[str, Any] = Field(default_factory=dict)
    recommended_action: dict[str, Any] = Field(default_factory=dict)
    scanned_operation_count: int = 0
    scan_limit: int = 500
    limit: int = 50
    items: list[CommercialOperationProductionClosedLoopInterventionQueueItemResponse] = Field(default_factory=list)
    generated_at: datetime
    boundaries: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


CommercialOperationProductionClosedLoopInterventionAcknowledgementStatus = Literal[
    "acknowledged",
    "assigned",
    "in_progress",
    "dismissed",
]


class CommercialOperationProductionClosedLoopInterventionAcknowledgementRequest(BaseModel):
    """Record operator ownership for a stale/watch queue item without executing it."""

    acknowledgement_status: CommercialOperationProductionClosedLoopInterventionAcknowledgementStatus = "acknowledged"
    assignee: str | None = Field(default=None, max_length=120)
    operator_confirmed: bool = False
    acknowledgement_notes: str | None = Field(default=None, max_length=2000)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationProductionClosedLoopInterventionAcknowledgementResponse(BaseModel):
    """One operator acknowledgement for a production closed-loop intervention queue item."""

    operation_id: UUID
    workspace_id: str
    acknowledgement_id: UUID
    acknowledgement_status: str
    assignee: str | None = None
    primary_step_key: str | None = None
    staleness_status: str
    waiting_seconds: int = 0
    priority_score: int = 0
    recommended_action_key: str | None = None
    queue_item_snapshot: dict[str, Any] = Field(default_factory=dict)
    operator_confirmed: bool = False
    acknowledgement_notes: str | None = None
    created_by: str | None = None
    created_at: datetime
    boundaries: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationProductionClosedLoopInterventionAcknowledgementListResponse(BaseModel):
    """Intervention queue acknowledgement history for one operation."""

    operation_id: UUID
    workspace_id: str
    acknowledgement_count: int = 0
    latest_record: CommercialOperationProductionClosedLoopInterventionAcknowledgementResponse | None = None
    records: list[CommercialOperationProductionClosedLoopInterventionAcknowledgementResponse] = Field(default_factory=list)
    generated_at: datetime
    boundaries: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


CommercialOperationProductionClosedLoopInterventionReminderDispatchStatus = Literal[
    "drafted",
    "ready_for_review",
    "routed_to_operator",
    "sent_manually",
    "dismissed",
]


class CommercialOperationProductionClosedLoopInterventionReminderDispatchRequest(BaseModel):
    """Record a safe reminder dispatch plan/result without sending platform messages automatically."""

    reminder_status: CommercialOperationProductionClosedLoopInterventionReminderDispatchStatus = "ready_for_review"
    reminder_channel: str = Field(default="internal", min_length=1, max_length=120)
    reminder_recipient: str | None = Field(default=None, max_length=200)
    reminder_message: str | None = Field(default=None, max_length=2000)
    operator_confirmed: bool = False
    evidence_links: list[dict[str, Any]] = Field(default_factory=list)
    dispatch_notes: str | None = Field(default=None, max_length=2000)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationProductionClosedLoopInterventionReminderDispatchResponse(BaseModel):
    """One operator-safe reminder dispatch record for an intervention queue item."""

    operation_id: UUID
    workspace_id: str
    reminder_dispatch_id: UUID
    reminder_status: str
    reminder_channel: str
    reminder_recipient: str | None = None
    reminder_message: str | None = None
    primary_step_key: str | None = None
    staleness_status: str
    acknowledgement_status: str | None = None
    acknowledgement_assignee: str | None = None
    acknowledgement_sla: dict[str, Any] = Field(default_factory=dict)
    reminder_dispatch_cooldown_before: dict[str, Any] = Field(default_factory=dict)
    queue_item_snapshot: dict[str, Any] = Field(default_factory=dict)
    operator_confirmed: bool = False
    evidence_links: list[dict[str, Any]] = Field(default_factory=list)
    dispatch_notes: str | None = None
    created_by: str | None = None
    created_at: datetime
    boundaries: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationProductionClosedLoopInterventionReminderDispatchListResponse(BaseModel):
    """Reminder dispatch history for one operation's intervention queue item."""

    operation_id: UUID
    workspace_id: str
    reminder_dispatch_count: int = 0
    latest_record: CommercialOperationProductionClosedLoopInterventionReminderDispatchResponse | None = None
    records: list[CommercialOperationProductionClosedLoopInterventionReminderDispatchResponse] = Field(default_factory=list)
    generated_at: datetime
    boundaries: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationProjectDecisionRequest(BaseModel):
    """Generic decision request for operation-project governance records."""

    reviewer_notes: str | None = None
    failure_reason: str | None = None


class CommercialOperationPlanCreateRequest(BaseModel):
    """Create a first-class operation plan."""

    plan_version: int = Field(default=1, ge=1)
    title: str = Field(min_length=1, max_length=255)
    objective_summary: str = Field(min_length=1)
    audience_strategy: str | None = None
    channel_strategy: list[dict[str, Any]] = Field(default_factory=list)
    content_strategy: dict[str, Any] = Field(default_factory=dict)
    production_scope: list[dict[str, Any]] = Field(default_factory=list)
    material_requirements: list[dict[str, Any]] = Field(default_factory=list)
    kpis: list[dict[str, Any]] = Field(default_factory=list)
    publish_schedule: list[dict[str, Any]] = Field(default_factory=list)
    risk_notes: str | None = None
    source_goal: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationPlanResponse(BaseModel):
    """Operation plan response."""

    id: UUID
    workspace_id: str
    operation_id: UUID
    plan_version: int
    title: str
    plan_status: str
    objective_summary: str
    audience_strategy: str | None
    channel_strategy: list[dict[str, Any]]
    content_strategy: dict[str, Any]
    production_scope: list[dict[str, Any]]
    material_requirements: list[dict[str, Any]]
    kpis: list[dict[str, Any]]
    publish_schedule: list[dict[str, Any]]
    risk_notes: str | None
    source_goal: str | None
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
    def from_model(cls, plan: CommercialOperationPlan) -> "CommercialOperationPlanResponse":
        return cls(
            id=plan.id,
            workspace_id=plan.workspace_id,
            operation_id=plan.operation_id,
            plan_version=plan.plan_version,
            title=plan.title,
            plan_status=plan.plan_status,
            objective_summary=plan.objective_summary,
            audience_strategy=plan.audience_strategy,
            channel_strategy=plan.channel_strategy,
            content_strategy=plan.content_strategy,
            production_scope=plan.production_scope,
            material_requirements=plan.material_requirements,
            kpis=plan.kpis,
            publish_schedule=plan.publish_schedule,
            risk_notes=plan.risk_notes,
            source_goal=plan.source_goal,
            reviewer_notes=plan.reviewer_notes,
            created_by=plan.created_by,
            updated_by=plan.updated_by,
            approved_by=plan.approved_by,
            approved_at=plan.approved_at,
            rejected_at=plan.rejected_at,
            archived_at=plan.archived_at,
            metadata=plan.plan_metadata,
            created_at=plan.created_at,
            updated_at=plan.updated_at,
        )


class CommercialOperationPlanListResponse(BaseModel):
    operation_id: UUID
    items: list[CommercialOperationPlanResponse]


class CommercialOperationProjectMaterialCreateRequest(BaseModel):
    """Register a project material imported from customer machine or server."""

    production_task_id: UUID | None = None
    material_type: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=255)
    source_uri: str = Field(min_length=1)
    file_name: str | None = Field(default=None, max_length=512)
    mime_type: str | None = Field(default=None, max_length=255)
    size_bytes: int | None = Field(default=None, ge=0)
    checksum: str | None = Field(default=None, max_length=128)
    authorization_status: str = Field(default="unverified", max_length=64)
    usage_scope: str | None = None
    tags: list[str] = Field(default_factory=list)
    linked_task_ids: list[str] = Field(default_factory=list)
    notes: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationProjectMaterialResponse(BaseModel):
    id: UUID
    workspace_id: str
    operation_id: UUID
    production_task_id: UUID | None
    material_type: str
    material_status: str
    name: str
    source_uri: str
    file_name: str | None
    mime_type: str | None
    size_bytes: int | None
    checksum: str | None
    authorization_status: str
    usage_scope: str | None
    tags: list[str]
    linked_task_ids: list[str]
    notes: str | None
    uploaded_by: str | None
    reviewed_by: str | None
    reviewed_at: datetime | None
    archived_at: datetime | None
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, material: CommercialOperationProjectMaterial) -> "CommercialOperationProjectMaterialResponse":
        return cls(
            id=material.id,
            workspace_id=material.workspace_id,
            operation_id=material.operation_id,
            production_task_id=material.production_task_id,
            material_type=material.material_type,
            material_status=material.material_status,
            name=material.name,
            source_uri=material.source_uri,
            file_name=material.file_name,
            mime_type=material.mime_type,
            size_bytes=material.size_bytes,
            checksum=material.checksum,
            authorization_status=material.authorization_status,
            usage_scope=material.usage_scope,
            tags=material.tags,
            linked_task_ids=material.linked_task_ids,
            notes=material.notes,
            uploaded_by=material.uploaded_by,
            reviewed_by=material.reviewed_by,
            reviewed_at=material.reviewed_at,
            archived_at=material.archived_at,
            metadata=material.material_metadata,
            created_at=material.created_at,
            updated_at=material.updated_at,
        )


class CommercialOperationProjectMaterialListResponse(BaseModel):
    operation_id: UUID
    items: list[CommercialOperationProjectMaterialResponse]


class CommercialOperationProductionTaskCreateRequest(BaseModel):
    """Create a production task derived from an operation plan."""

    operation_plan_id: UUID | None = None
    task_type: CommercialOperationProductionTaskTypeLiteral
    media_subtype: CommercialOperationMediaSubtypeLiteral | None = None
    channel: str = Field(min_length=1, max_length=128)
    title: str = Field(min_length=1, max_length=255)
    brief: str | None = None
    source_material_ids: list[str] = Field(default_factory=list)
    output_requirements: list[dict[str, Any]] = Field(default_factory=list)
    target_specs: dict[str, Any] = Field(default_factory=dict)
    workflow_selection_required: bool = True
    assigned_agent: str | None = Field(default=None, max_length=128)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationProductionTaskResponse(BaseModel):
    id: UUID
    workspace_id: str
    operation_id: UUID
    operation_plan_id: UUID | None
    task_type: str
    media_subtype: str | None
    channel: str
    title: str
    task_status: str
    brief: str | None
    source_material_ids: list[str]
    output_requirements: list[dict[str, Any]]
    target_specs: dict[str, Any]
    workflow_selection_required: bool
    assigned_agent: str | None
    reviewer_notes: str | None
    created_by: str | None
    updated_by: str | None
    approved_by: str | None
    completed_by: str | None
    approved_at: datetime | None
    started_at: datetime | None
    completed_at: datetime | None
    rejected_at: datetime | None
    archived_at: datetime | None
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, task: CommercialOperationProductionTask) -> "CommercialOperationProductionTaskResponse":
        return cls(
            id=task.id,
            workspace_id=task.workspace_id,
            operation_id=task.operation_id,
            operation_plan_id=task.operation_plan_id,
            task_type=task.task_type,
            media_subtype=task.media_subtype,
            channel=task.channel,
            title=task.title,
            task_status=task.task_status,
            brief=task.brief,
            source_material_ids=task.source_material_ids,
            output_requirements=task.output_requirements,
            target_specs=task.target_specs,
            workflow_selection_required=task.workflow_selection_required,
            assigned_agent=task.assigned_agent,
            reviewer_notes=task.reviewer_notes,
            created_by=task.created_by,
            updated_by=task.updated_by,
            approved_by=task.approved_by,
            completed_by=task.completed_by,
            approved_at=task.approved_at,
            started_at=task.started_at,
            completed_at=task.completed_at,
            rejected_at=task.rejected_at,
            archived_at=task.archived_at,
            metadata=task.task_metadata,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )


class CommercialOperationProductionTaskListResponse(BaseModel):
    operation_id: UUID
    items: list[CommercialOperationProductionTaskResponse]


CommercialOperationNextCycleDraftStatusLiteral = Literal["created", "reused"]


class CommercialOperationNextCycleDraftRequest(BaseModel):
    """Prepare a reviewable next operation cycle from an approved optimization decision."""

    operator_confirmed: bool = False
    source_decision_id: UUID | None = None
    create_tasks: bool = True
    operator_note: str | None = Field(default=None, max_length=2000)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationNextCycleDraftResponse(BaseModel):
    """Reviewable next-cycle plan and production-task draft package."""

    operation_id: UUID
    workspace_id: str
    draft_status: CommercialOperationNextCycleDraftStatusLiteral
    source_decision_id: UUID
    operation_plan: CommercialOperationPlanResponse
    production_tasks: list[CommercialOperationProductionTaskResponse] = Field(default_factory=list)
    readiness_status_before: str | None = None
    next_action_key_before: str | None = None
    operator_next_actions: list[str] = Field(default_factory=list)
    server_next_actions: list[str] = Field(default_factory=list)
    client_next_actions: list[str] = Field(default_factory=list)
    boundaries: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    generated_at: datetime


class CommercialOperationWorkflowSelectionCreateRequest(BaseModel):
    production_task_id: UUID
    workflow_source: str = Field(default="comfyui", min_length=1, max_length=64)
    workflow_name: str = Field(min_length=1, max_length=255)
    workflow_kind: str | None = Field(default=None, max_length=128)
    output_type: str = Field(min_length=1, max_length=64)
    candidate_summary: str | None = None
    input_requirements: list[dict[str, Any]] = Field(default_factory=list)
    expected_outputs: list[dict[str, Any]] = Field(default_factory=list)
    recommendation_reason: str | None = None
    estimated_duration_seconds: float | None = Field(default=None, ge=0)
    estimated_vram_mb: int | None = Field(default=None, ge=0)
    risk_notes: str | None = None
    validation_status: str = Field(default="not_checked", max_length=64)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationWorkflowSelectionResponse(BaseModel):
    id: UUID
    workspace_id: str
    operation_id: UUID
    production_task_id: UUID
    workflow_source: str
    workflow_name: str
    workflow_kind: str | None
    output_type: str
    selection_status: str
    candidate_summary: str | None
    input_requirements: list[dict[str, Any]]
    expected_outputs: list[dict[str, Any]]
    recommendation_reason: str | None
    estimated_duration_seconds: float | None
    estimated_vram_mb: int | None
    risk_notes: str | None
    validation_status: str
    selected_by: str | None
    approved_by: str | None
    approved_at: datetime | None
    rejected_at: datetime | None
    archived_at: datetime | None
    reviewer_notes: str | None
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, selection: CommercialOperationWorkflowSelection) -> "CommercialOperationWorkflowSelectionResponse":
        return cls(
            id=selection.id,
            workspace_id=selection.workspace_id,
            operation_id=selection.operation_id,
            production_task_id=selection.production_task_id,
            workflow_source=selection.workflow_source,
            workflow_name=selection.workflow_name,
            workflow_kind=selection.workflow_kind,
            output_type=selection.output_type,
            selection_status=selection.selection_status,
            candidate_summary=selection.candidate_summary,
            input_requirements=selection.input_requirements,
            expected_outputs=selection.expected_outputs,
            recommendation_reason=selection.recommendation_reason,
            estimated_duration_seconds=selection.estimated_duration_seconds,
            estimated_vram_mb=selection.estimated_vram_mb,
            risk_notes=selection.risk_notes,
            validation_status=selection.validation_status,
            selected_by=selection.selected_by,
            approved_by=selection.approved_by,
            approved_at=selection.approved_at,
            rejected_at=selection.rejected_at,
            archived_at=selection.archived_at,
            reviewer_notes=selection.reviewer_notes,
            metadata=selection.selection_metadata,
            created_at=selection.created_at,
            updated_at=selection.updated_at,
        )


class CommercialOperationWorkflowSelectionListResponse(BaseModel):
    operation_id: UUID
    items: list[CommercialOperationWorkflowSelectionResponse]


class CommercialOperationWorkflowCandidateResponse(BaseModel):
    """Library-backed workflow candidate that can be turned into a selection."""

    candidate_id: str
    rank: int
    score: float
    workflow_source: str = "comfyui_cu130_rag"
    workflow_name: str
    workflow_kind: str | None = None
    output_type: str
    category: str | None = None
    capabilities: list[str]
    candidate_summary: str | None = None
    input_requirements: list[dict[str, Any]] = Field(default_factory=list)
    expected_outputs: list[dict[str, Any]] = Field(default_factory=list)
    recommendation_reason: str | None = None
    estimated_duration_seconds: float | None = Field(default=None, ge=0)
    estimated_vram_mb: int | None = Field(default=None, ge=0)
    risk_notes: str | None = None
    validation_status: str
    runtime_readiness: str
    workflow_path: str | None = None
    workflow_path_exists: bool = False
    requires_prompt_validation: bool = True
    model_refs_found_count: int = 0
    model_refs_missing: list[str] = Field(default_factory=list)
    missing_executable_node_types: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationWorkflowCandidateListResponse(BaseModel):
    """Workflow candidate list for one production task."""

    operation_id: UUID
    production_task_id: UUID
    query: str
    required_capabilities: list[str]
    preferred_terms: list[str]
    items: list[CommercialOperationWorkflowCandidateResponse]
    library_metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationOutputCandidateCreateRequest(BaseModel):
    production_task_id: UUID | None = None
    workflow_selection_id: UUID | None = None
    output_artifact_id: UUID | None = None
    candidate_type: str = Field(min_length=1, max_length=64)
    title: str = Field(min_length=1, max_length=255)
    preview_uri: str | None = None
    source_uri: str | None = None
    thumbnail_uri: str | None = None
    mime_type: str | None = Field(default=None, max_length=255)
    duration_seconds: float | None = Field(default=None, ge=0)
    generation_summary: str | None = None
    quality_checks: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationOutputCandidateResponse(BaseModel):
    id: UUID
    workspace_id: str
    operation_id: UUID
    production_task_id: UUID | None
    workflow_selection_id: UUID | None
    output_artifact_id: UUID | None
    candidate_type: str
    candidate_status: str
    title: str
    preview_uri: str | None
    source_uri: str | None
    thumbnail_uri: str | None
    mime_type: str | None
    duration_seconds: float | None
    generation_summary: str | None
    quality_checks: list[str]
    reviewer_notes: str | None
    created_by: str | None
    selected_by: str | None
    selected_at: datetime | None
    rejected_at: datetime | None
    archived_at: datetime | None
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, candidate: CommercialOperationOutputCandidate) -> "CommercialOperationOutputCandidateResponse":
        return cls(
            id=candidate.id,
            workspace_id=candidate.workspace_id,
            operation_id=candidate.operation_id,
            production_task_id=candidate.production_task_id,
            workflow_selection_id=candidate.workflow_selection_id,
            output_artifact_id=candidate.output_artifact_id,
            candidate_type=candidate.candidate_type,
            candidate_status=candidate.candidate_status,
            title=candidate.title,
            preview_uri=candidate.preview_uri,
            source_uri=candidate.source_uri,
            thumbnail_uri=candidate.thumbnail_uri,
            mime_type=candidate.mime_type,
            duration_seconds=candidate.duration_seconds,
            generation_summary=candidate.generation_summary,
            quality_checks=candidate.quality_checks,
            reviewer_notes=candidate.reviewer_notes,
            created_by=candidate.created_by,
            selected_by=candidate.selected_by,
            selected_at=candidate.selected_at,
            rejected_at=candidate.rejected_at,
            archived_at=candidate.archived_at,
            metadata=candidate.candidate_metadata,
            created_at=candidate.created_at,
            updated_at=candidate.updated_at,
        )


class CommercialOperationOutputCandidateListResponse(BaseModel):
    operation_id: UUID
    items: list[CommercialOperationOutputCandidateResponse]


class CommercialOperationFinalSelectionCreateRequest(BaseModel):
    production_task_id: UUID | None = None
    output_candidate_id: UUID
    final_type: str = Field(min_length=1, max_length=64)
    title: str = Field(min_length=1, max_length=255)
    selection_reason: str | None = None
    platform_targets: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationFinalSelectionResponse(BaseModel):
    id: UUID
    workspace_id: str
    operation_id: UUID
    production_task_id: UUID | None
    output_candidate_id: UUID
    final_type: str
    title: str
    selection_status: str
    selection_reason: str | None
    platform_targets: list[str]
    selected_by: str | None
    approved_by: str | None
    approved_at: datetime | None
    rejected_at: datetime | None
    archived_at: datetime | None
    reviewer_notes: str | None
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, selection: CommercialOperationFinalSelection) -> "CommercialOperationFinalSelectionResponse":
        return cls(
            id=selection.id,
            workspace_id=selection.workspace_id,
            operation_id=selection.operation_id,
            production_task_id=selection.production_task_id,
            output_candidate_id=selection.output_candidate_id,
            final_type=selection.final_type,
            title=selection.title,
            selection_status=selection.selection_status,
            selection_reason=selection.selection_reason,
            platform_targets=selection.platform_targets,
            selected_by=selection.selected_by,
            approved_by=selection.approved_by,
            approved_at=selection.approved_at,
            rejected_at=selection.rejected_at,
            archived_at=selection.archived_at,
            reviewer_notes=selection.reviewer_notes,
            metadata=selection.selection_metadata,
            created_at=selection.created_at,
            updated_at=selection.updated_at,
        )


class CommercialOperationFinalSelectionListResponse(BaseModel):
    operation_id: UUID
    items: list[CommercialOperationFinalSelectionResponse]


class CommercialOperationOutputPrepPackageResponse(BaseModel):
    """Read-only output preparation package for one production task."""

    operation_id: UUID
    production_task_id: UUID
    readiness_status: str
    blocking_reasons: list[str] = Field(default_factory=list)
    task_status: str
    workflow_selection_required: bool
    approved_workflow_selection_id: UUID | None = None
    task_summary: dict[str, Any] = Field(default_factory=dict)
    candidate_blueprint: dict[str, Any] = Field(default_factory=dict)
    required_inputs: list[dict[str, Any]] = Field(default_factory=list)
    expected_outputs: list[dict[str, Any]] = Field(default_factory=list)
    review_gates: list[str] = Field(default_factory=list)
    available_output_candidates: list[CommercialOperationOutputCandidateResponse] = Field(default_factory=list)
    existing_final_selections: list[CommercialOperationFinalSelectionResponse] = Field(default_factory=list)
    output_storage_policy: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationPublishPackageCreateRequest(BaseModel):
    final_selection_id: UUID | None = None
    platform: str = Field(min_length=1, max_length=128)
    account_ref: str | None = Field(default=None, max_length=255)
    title: str = Field(min_length=1, max_length=255)
    body: str = Field(min_length=1)
    hashtags: list[str] = Field(default_factory=list)
    cover_candidate_id: UUID | None = None
    scheduled_at: datetime | None = None
    publish_payload: dict[str, Any] = Field(default_factory=dict)
    risk_notes: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationPublishPackageResponse(BaseModel):
    id: UUID
    workspace_id: str
    operation_id: UUID
    final_selection_id: UUID | None
    platform: str
    account_ref: str | None
    title: str
    body: str
    package_status: str
    hashtags: list[str]
    cover_candidate_id: UUID | None
    scheduled_at: datetime | None
    publish_payload: dict[str, Any]
    risk_notes: str | None
    reviewer_notes: str | None
    created_by: str | None
    approved_by: str | None
    prepared_by: str | None
    approved_at: datetime | None
    prepared_at: datetime | None
    published_at: datetime | None
    rejected_at: datetime | None
    failed_at: datetime | None
    archived_at: datetime | None
    failure_reason: str | None
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, package: CommercialOperationPublishPackage) -> "CommercialOperationPublishPackageResponse":
        return cls(
            id=package.id,
            workspace_id=package.workspace_id,
            operation_id=package.operation_id,
            final_selection_id=package.final_selection_id,
            platform=package.platform,
            account_ref=package.account_ref,
            title=package.title,
            body=package.body,
            package_status=package.package_status,
            hashtags=package.hashtags,
            cover_candidate_id=package.cover_candidate_id,
            scheduled_at=package.scheduled_at,
            publish_payload=package.publish_payload,
            risk_notes=package.risk_notes,
            reviewer_notes=package.reviewer_notes,
            created_by=package.created_by,
            approved_by=package.approved_by,
            prepared_by=package.prepared_by,
            approved_at=package.approved_at,
            prepared_at=package.prepared_at,
            published_at=package.published_at,
            rejected_at=package.rejected_at,
            failed_at=package.failed_at,
            archived_at=package.archived_at,
            failure_reason=package.failure_reason,
            metadata=package.package_metadata,
            created_at=package.created_at,
            updated_at=package.updated_at,
        )


class CommercialOperationPublishPackageListResponse(BaseModel):
    operation_id: UUID
    items: list[CommercialOperationPublishPackageResponse]


class CommercialOperationPublishPrepPackageResponse(BaseModel):
    """Read-only publish preparation package for one approved final selection."""

    operation_id: UUID
    final_selection_id: UUID
    readiness_status: str
    blocking_reasons: list[str] = Field(default_factory=list)
    final_selection_status: str
    platform_targets: list[str] = Field(default_factory=list)
    final_selection: CommercialOperationFinalSelectionResponse
    selected_output_candidate: CommercialOperationOutputCandidateResponse | None = None
    package_blueprints: list[dict[str, Any]] = Field(default_factory=list)
    copy_guidance: dict[str, Any] = Field(default_factory=dict)
    review_gates: list[str] = Field(default_factory=list)
    existing_publish_packages: list[CommercialOperationPublishPackageResponse] = Field(default_factory=list)
    platform_policy: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationPlatformMetricSnapshotCreateRequest(BaseModel):
    publish_package_id: UUID | None = None
    platform: str = Field(min_length=1, max_length=128)
    platform_content_id: str | None = Field(default=None, max_length=255)
    source_type: str = Field(default="manual", max_length=64)
    collected_at: datetime | None = None
    metric_date: datetime | None = None
    metrics: dict[str, Any] = Field(default_factory=dict)
    summary: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationPlatformMetricSnapshotResponse(BaseModel):
    id: UUID
    workspace_id: str
    operation_id: UUID
    publish_package_id: UUID | None
    platform: str
    platform_content_id: str | None
    source_type: str
    snapshot_status: str
    collected_at: datetime | None
    metric_date: datetime | None
    metrics: dict[str, Any]
    summary: str | None
    reviewer_notes: str | None
    collected_by: str | None
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
        snapshot: CommercialOperationPlatformMetricSnapshot,
    ) -> "CommercialOperationPlatformMetricSnapshotResponse":
        return cls(
            id=snapshot.id,
            workspace_id=snapshot.workspace_id,
            operation_id=snapshot.operation_id,
            publish_package_id=snapshot.publish_package_id,
            platform=snapshot.platform,
            platform_content_id=snapshot.platform_content_id,
            source_type=snapshot.source_type,
            snapshot_status=snapshot.snapshot_status,
            collected_at=snapshot.collected_at,
            metric_date=snapshot.metric_date,
            metrics=snapshot.metrics,
            summary=snapshot.summary,
            reviewer_notes=snapshot.reviewer_notes,
            collected_by=snapshot.collected_by,
            approved_by=snapshot.approved_by,
            approved_at=snapshot.approved_at,
            rejected_at=snapshot.rejected_at,
            archived_at=snapshot.archived_at,
            metadata=snapshot.snapshot_metadata,
            created_at=snapshot.created_at,
            updated_at=snapshot.updated_at,
        )


class CommercialOperationPlatformMetricSnapshotListResponse(BaseModel):
    operation_id: UUID
    items: list[CommercialOperationPlatformMetricSnapshotResponse]


class CommercialOperationPublishExecutionHandoffResponse(BaseModel):
    """Read-only guarded customer-machine execution handoff for one publish package."""

    operation_id: UUID
    publish_package_id: UUID
    readiness_status: str
    blocking_reasons: list[str] = Field(default_factory=list)
    package_status: str
    platform: str
    execution_target: str | None = None
    publish_package: CommercialOperationPublishPackageResponse
    final_selection: CommercialOperationFinalSelectionResponse | None = None
    selected_output_candidate: CommercialOperationOutputCandidateResponse | None = None
    execution_status: dict[str, Any] = Field(default_factory=dict)
    client_execution_payload: dict[str, Any] = Field(default_factory=dict)
    execution_runbook: list[dict[str, Any]] = Field(default_factory=list)
    account_confirmation: dict[str, Any] = Field(default_factory=dict)
    dry_run_plan: dict[str, Any] = Field(default_factory=dict)
    expected_evidence: list[dict[str, Any]] = Field(default_factory=list)
    metric_pullback_plan: dict[str, Any] = Field(default_factory=dict)
    review_gates: list[str] = Field(default_factory=list)
    existing_metric_snapshots: list[CommercialOperationPlatformMetricSnapshotResponse] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationPublishExecutionResultCreateRequest(BaseModel):
    """Capture customer-machine publish execution result evidence for one publish package."""

    publish_succeeded: bool = True
    platform_content_id: str | None = Field(default=None, max_length=255)
    published_url: str | None = Field(default=None, max_length=2048)
    execution_summary: str | None = None
    operator_notes: str | None = None
    evidence_links: list[dict[str, Any]] = Field(default_factory=list)
    dry_run_evidence: list[dict[str, Any]] = Field(default_factory=list)
    execution_log: list[dict[str, Any]] = Field(default_factory=list)
    observed_metrics: dict[str, Any] = Field(default_factory=dict)
    metric_snapshot_summary: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_success_has_platform_reference(self) -> "CommercialOperationPublishExecutionResultCreateRequest":
        if self.publish_succeeded and not (self.platform_content_id or self.published_url):
            raise ValueError("platform_content_id or published_url is required when publish_succeeded is true")
        return self


class CommercialOperationPublishExecutionResultResponse(BaseModel):
    """Captured customer-machine publish execution result for one publish package."""

    operation_id: UUID
    publish_package_id: UUID
    result_status: str
    publish_succeeded: bool
    platform: str
    platform_content_id: str | None = None
    published_url: str | None = None
    publish_package: CommercialOperationPublishPackageResponse
    created_metric_snapshot: CommercialOperationPlatformMetricSnapshotResponse | None = None
    execution_result: dict[str, Any] = Field(default_factory=dict)
    evidence_links: list[dict[str, Any]] = Field(default_factory=list)
    dry_run_evidence: list[dict[str, Any]] = Field(default_factory=list)
    execution_log: list[dict[str, Any]] = Field(default_factory=list)
    review_gates: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


CommercialOperationPublishExecutionStatusLiteral = Literal[
    "queued",
    "running",
    "needs_operator",
    "succeeded",
    "failed",
    "cancelled",
]


class CommercialOperationPublishExecutionStatusUpdateRequest(BaseModel):
    """Update customer-machine publish execution progress before final result capture."""

    execution_status: CommercialOperationPublishExecutionStatusLiteral
    operator_confirmed: bool = False
    customer_machine_id: str = Field(default="customer-machine-default", min_length=1, max_length=128)
    attempt_id: UUID | None = None
    progress: int | None = Field(default=None, ge=0, le=100)
    failure_reason: str | None = Field(default=None, max_length=2000)
    operator_notes: str | None = Field(default=None, max_length=2000)
    retry_after_seconds: int | None = Field(default=None, ge=30, le=86400)
    evidence_links: list[dict[str, Any]] = Field(default_factory=list)
    execution_log: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationPublishExecutionStatusResponse(BaseModel):
    """Customer-machine publish execution progress status for one publish package."""

    operation_id: UUID
    publish_package_id: UUID
    attempt_id: UUID
    execution_status: str
    package_status: str
    customer_machine_id: str
    progress: int | None = None
    failure_reason: str | None = None
    publish_package: CommercialOperationPublishPackageResponse
    latest_attempt: dict[str, Any] = Field(default_factory=dict)
    execution_history: list[dict[str, Any]] = Field(default_factory=list)
    retry_policy: dict[str, Any] = Field(default_factory=dict)
    review_gates: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationMetricAnalysisScheduleRequest(BaseModel):
    """Configure the project-level daily metric analysis schedule."""

    enabled: bool = True
    local_time: str = Field(default="21:00", pattern=r"^\d{2}:\d{2}$")
    timezone: str = Field(default="Asia/Shanghai", min_length=1, max_length=128)
    lookback_hours: int = Field(default=24, ge=1, le=168)
    platform_scope: list[str] = Field(default_factory=list)
    metric_requirements: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_daily_local_time(self) -> "CommercialOperationMetricAnalysisScheduleRequest":
        hour_text, minute_text = self.local_time.split(":", 1)
        hour = int(hour_text)
        minute = int(minute_text)
        if hour > 23 or minute > 59:
            raise ValueError("local_time must be HH:MM in 24-hour time")
        return self


class CommercialOperationMetricAnalysisScheduleResponse(BaseModel):
    """Project-level daily metric analysis schedule and due-state contract."""

    operation_id: UUID
    schedule_status: str
    enabled: bool
    cadence: str = "daily"
    local_time: str
    timezone: str
    next_run_at: datetime | None = None
    last_run_at: datetime | None = None
    lookback_hours: int
    platform_scope: list[str] = Field(default_factory=list)
    metric_requirements: list[str] = Field(default_factory=list)
    published_package_count: int = 0
    latest_metric_snapshot: CommercialOperationPlatformMetricSnapshotResponse | None = None
    analysis_contract: dict[str, Any] = Field(default_factory=dict)
    review_gates: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationMetricAnalysisCollectedMetricRequest(BaseModel):
    """Metrics collected by a platform connector or customer-machine pullback for a scheduled analysis run."""

    publish_package_id: UUID | None = None
    platform: str | None = Field(default=None, max_length=128)
    platform_content_id: str | None = Field(default=None, max_length=255)
    source_type: str = Field(default="customer_machine_metric_pullback", max_length=64)
    collected_at: datetime | None = None
    metric_date: datetime | None = None
    metrics: dict[str, Any] = Field(default_factory=dict)
    summary: str | None = None
    evidence_links: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationMetricAnalysisRunRequest(BaseModel):
    """Run or force-run the configured daily metric analysis contract for one project."""

    force: bool = False
    collected_metrics: list[CommercialOperationMetricAnalysisCollectedMetricRequest] = Field(default_factory=list)
    operator_notes: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationMetricAnalysisRunResponse(BaseModel):
    """A scheduled metric analysis run package for the project closed loop."""

    operation_id: UUID
    run_status: str
    forced: bool = False
    due: bool = False
    schedule_status_before: str
    schedule_status_after: str
    schedule: CommercialOperationMetricAnalysisScheduleResponse
    eligible_publish_packages: list[CommercialOperationPublishPackageResponse] = Field(default_factory=list)
    created_metric_snapshots: list[CommercialOperationPlatformMetricSnapshotResponse] = Field(default_factory=list)
    usable_metric_snapshots: list[CommercialOperationPlatformMetricSnapshotResponse] = Field(default_factory=list)
    analysis_package: dict[str, Any] = Field(default_factory=dict)
    review_gates: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationMetricPullbackHandoffResponse(BaseModel):
    """Customer-machine handoff package for scheduled platform metric pullback."""

    operation_id: UUID
    handoff_status: str
    due: bool = False
    forced: bool = False
    schedule: CommercialOperationMetricAnalysisScheduleResponse
    published_packages: list[CommercialOperationPublishPackageResponse] = Field(default_factory=list)
    pullback_tasks: list[dict[str, Any]] = Field(default_factory=list)
    target_metric_keys: list[str] = Field(default_factory=list)
    evidence_requirements: list[dict[str, Any]] = Field(default_factory=list)
    client_adapter_plan: dict[str, Any] = Field(default_factory=dict)
    analysis_run_request_template: dict[str, Any] = Field(default_factory=dict)
    review_gates: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationMetricPullbackResultRequest(BaseModel):
    """Submit customer-machine or connector-collected metric pullback results."""

    force: bool = False
    adapter_mode: str = Field(default="customer_machine_manual_evidence", min_length=1, max_length=64)
    adapter_run_id: str | None = Field(default=None, max_length=128)
    collected_metrics: list[CommercialOperationMetricAnalysisCollectedMetricRequest] = Field(default_factory=list)
    operator_notes: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationMetricPullbackResultResponse(BaseModel):
    """Validated customer-machine metric pullback submission and linked analysis run."""

    operation_id: UUID
    submission_status: str
    forced: bool = False
    adapter_mode: str
    adapter_run_id: str | None = None
    handoff: CommercialOperationMetricPullbackHandoffResponse
    submitted_metric_count: int = 0
    accepted_metric_count: int = 0
    rejected_metric_count: int = 0
    accepted_metrics: list[dict[str, Any]] = Field(default_factory=list)
    rejected_metrics: list[dict[str, Any]] = Field(default_factory=list)
    metric_analysis_run: CommercialOperationMetricAnalysisRunResponse | None = None
    review_gates: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationMetricPullbackAdapterProfileResponse(BaseModel):
    """Platform-specific customer-machine metric pullback adapter profile."""

    operation_id: UUID
    adapter_profile_id: str
    platform: str
    profile_status: str
    due: bool = False
    forced: bool = False
    handoff: CommercialOperationMetricPullbackHandoffResponse
    supported_input_modes: list[str] = Field(default_factory=list)
    target_metric_keys: list[str] = Field(default_factory=list)
    field_aliases: dict[str, list[str]] = Field(default_factory=dict)
    normalization_rules: list[dict[str, Any]] = Field(default_factory=list)
    evidence_requirements: list[dict[str, Any]] = Field(default_factory=list)
    runbook: list[dict[str, Any]] = Field(default_factory=list)
    browser_assist_plan: dict[str, Any] = Field(default_factory=dict)
    export_import_contract: dict[str, Any] = Field(default_factory=dict)
    submission_template: dict[str, Any] = Field(default_factory=dict)
    review_gates: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationMetricPullbackExportImportPreviewRequest(BaseModel):
    """Preview customer-machine metric export rows before submitting them to 68M."""

    platform: str = Field(default="douyin", min_length=1, max_length=64)
    force: bool = False
    export_format: Literal["csv", "json", "manual_rows", "xlsx_rows"] = "csv"
    raw_text: str | None = Field(default=None, max_length=500_000)
    rows: list[dict[str, Any]] = Field(default_factory=list)
    evidence_links: list[dict[str, Any]] = Field(default_factory=list)
    operator_confirmed: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationMetricPullbackExportImportPreviewResponse(BaseModel):
    """Normalized metric export import preview for customer-machine submission."""

    operation_id: UUID
    platform: str
    preview_status: str
    forced: bool = False
    operator_confirmed: bool = False
    adapter_profile: CommercialOperationMetricPullbackAdapterProfileResponse
    parsed_row_count: int = 0
    accepted_metric_count: int = 0
    rejected_row_count: int = 0
    accepted_metrics: list[dict[str, Any]] = Field(default_factory=list)
    rejected_rows: list[dict[str, Any]] = Field(default_factory=list)
    submission_payload: dict[str, Any] = Field(default_factory=dict)
    review_gates: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationMetricPullbackBrowserAssistSessionRequest(BaseModel):
    """Create a guarded customer-machine browser assist metric pullback session plan."""

    platform: str = Field(default="douyin", min_length=1, max_length=64)
    force: bool = False
    operator_confirmed: bool = False
    target_publish_package_id: UUID | None = None
    open_target_url: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationMetricPullbackBrowserAssistSessionResponse(BaseModel):
    """Guarded customer-machine browser assist session plan for metric pullback."""

    operation_id: UUID
    platform: str
    browser_assist_session_id: str
    session_status: str
    forced: bool = False
    operator_confirmed: bool = False
    adapter_profile: CommercialOperationMetricPullbackAdapterProfileResponse
    target_task_count: int = 0
    target_tasks: list[dict[str, Any]] = Field(default_factory=list)
    navigation_targets: list[dict[str, Any]] = Field(default_factory=list)
    extraction_fields: list[dict[str, Any]] = Field(default_factory=list)
    evidence_plan: list[dict[str, Any]] = Field(default_factory=list)
    allowed_domain_suffixes: list[str] = Field(default_factory=list)
    forbidden_actions: list[str] = Field(default_factory=list)
    operator_checklist: list[dict[str, Any]] = Field(default_factory=list)
    submission_template: dict[str, Any] = Field(default_factory=dict)
    review_gates: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationMetricAnalysisDispatchQueueResponse(BaseModel):
    """Workspace-level dispatch queue for scheduled metric analysis pullback."""

    workspace_id: str
    dispatch_status: str
    forced: bool = False
    platform: str | None = None
    scanned_operation_count: int = 0
    due_count: int = 0
    ready_dispatch_count: int = 0
    blocked_count: int = 0
    idle_count: int = 0
    items: list[dict[str, Any]] = Field(default_factory=list)
    scheduler_poll_contract: dict[str, Any] = Field(default_factory=dict)
    review_gates: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationMetricDispatchClaimRequest(BaseModel):
    """Claim one ready metric dispatch item for customer-machine execution."""

    platform: str | None = Field(default=None, max_length=64)
    force: bool = False
    collection_mode: str | None = Field(default=None, max_length=96)
    customer_machine_id: str = Field(default="customer-machine-default", min_length=1, max_length=128)
    operator_confirmed: bool = False
    lease_seconds: int = Field(default=1800, ge=60, le=21600)
    target_operation_id: UUID | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationMetricDispatchClaimStatusRequest(BaseModel):
    """Update a customer-machine metric dispatch claim status."""

    claim_status: Literal["claimed", "running", "completed", "failed", "released"] = "running"
    progress: int | None = Field(default=None, ge=0, le=100)
    lease_seconds: int = Field(default=1800, ge=60, le=21600)
    operator_notes: str | None = None
    evidence_links: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationMetricDispatchClaimResponse(BaseModel):
    """Persisted customer-machine claim for one metric dispatch queue item."""

    workspace_id: str
    claim_id: UUID | None = None
    claim_status: str
    operation_id: UUID | None = None
    platform: str | None = None
    collection_mode: str | None = None
    customer_machine_id: str | None = None
    forced: bool = False
    operator_confirmed: bool = False
    lease_expires_at: datetime | None = None
    dispatch_item: dict[str, Any] | None = None
    claim_record: dict[str, Any] = Field(default_factory=dict)
    dispatch_queue: CommercialOperationMetricAnalysisDispatchQueueResponse | None = None
    review_gates: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationMetricDispatchClaimListResponse(BaseModel):
    """Workspace customer-machine metric dispatch claim list."""

    workspace_id: str
    claim_status: str | None = None
    items: list[dict[str, Any]] = Field(default_factory=list)
    active_count: int = 0
    expired_count: int = 0
    completed_count: int = 0
    review_gates: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationMetricDispatchCustomerPollRequest(BaseModel):
    """Customer-machine poll request for metric dispatch recovery and optional claim."""

    platform: str | None = Field(default=None, max_length=64)
    force: bool = False
    collection_mode: str | None = Field(default=None, max_length=96)
    customer_machine_id: str = Field(default="customer-machine-default", min_length=1, max_length=128)
    auto_claim: bool = False
    operator_confirmed: bool = False
    lease_seconds: int = Field(default=1800, ge=60, le=21600)
    target_operation_id: UUID | None = None
    limit: int = Field(default=20, ge=1, le=100)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationMetricDispatchCustomerPollResponse(BaseModel):
    """Customer-machine poll response with queue, claim, and recovery guidance."""

    workspace_id: str
    poll_status: str
    customer_machine_id: str
    auto_claimed: bool = False
    poll_interval_seconds: int = 300
    dispatch_queue: CommercialOperationMetricAnalysisDispatchQueueResponse
    claim_result: CommercialOperationMetricDispatchClaimResponse | None = None
    claim_list: CommercialOperationMetricDispatchClaimListResponse
    assigned_claims: list[dict[str, Any]] = Field(default_factory=list)
    expired_claims: list[dict[str, Any]] = Field(default_factory=list)
    redispatch_candidates: list[dict[str, Any]] = Field(default_factory=list)
    review_gates: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationMetricDispatchPollSchedulerRequest(BaseModel):
    """Customer-machine poll scheduler plan request."""

    platform: str | None = Field(default=None, max_length=64)
    force: bool = False
    collection_mode: str | None = Field(default=None, max_length=96)
    customer_machine_id: str = Field(default="customer-machine-default", min_length=1, max_length=128)
    scheduler_enabled: bool = True
    auto_claim: bool = False
    operator_confirmed: bool = False
    requested_poll_interval_seconds: int | None = Field(default=None, ge=30, le=21600)
    lease_seconds: int = Field(default=1800, ge=60, le=21600)
    target_operation_id: UUID | None = None
    limit: int = Field(default=20, ge=1, le=100)
    run_poll_now: bool = True
    notification_channels: list[str] = Field(default_factory=lambda: ["customer_console"])
    notify_on: list[str] = Field(
        default_factory=lambda: [
            "ready_to_claim",
            "active_claim_in_progress",
            "auto_claimed",
            "recovery_required",
            "claim_blocked",
        ]
    )
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationMetricDispatchPollSchedulerResponse(BaseModel):
    """Customer-machine poll scheduler and notification bridge response."""

    workspace_id: str
    scheduler_status: str
    scheduler_enabled: bool = True
    customer_machine_id: str
    platform: str | None = None
    auto_claim: bool = False
    operator_confirmed: bool = False
    recommended_poll_interval_seconds: int = 300
    next_poll_at: datetime | None = None
    poll_result: CommercialOperationMetricDispatchCustomerPollResponse | None = None
    notification_events: list[dict[str, Any]] = Field(default_factory=list)
    scheduler_policy: dict[str, Any] = Field(default_factory=dict)
    client_timer_payload: dict[str, Any] = Field(default_factory=dict)
    review_gates: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationProductionClosedLoopStageResponse(BaseModel):
    """One production closed-loop readiness stage."""

    stage_key: str
    title: str
    status: str
    required: bool = True
    count: int = 0
    complete_count: int = 0
    blocking_reasons: list[str] = Field(default_factory=list)
    next_action: str
    primary_record: dict[str, Any] | None = None
    evidence: list[str] = Field(default_factory=list)


class CommercialOperationProductionClosedLoopReadinessResponse(BaseModel):
    """Production E2E readiness view across project, output, publish, and metric feedback."""

    operation_id: UUID
    workspace_id: str
    readiness_status: str
    completion_ratio: float
    current_stage_key: str | None = None
    next_action: str
    ready_for_customer_machine_execution: bool = False
    ready_for_metric_feedback: bool = False
    ready_for_next_cycle: bool = False
    operation_loop_status: str
    operation_loop_current_stage_key: str | None = None
    stages: list[CommercialOperationProductionClosedLoopStageResponse] = Field(default_factory=list)
    counts: dict[str, int] = Field(default_factory=dict)
    latest_records: dict[str, dict[str, Any] | None] = Field(default_factory=dict)
    metric_schedule: CommercialOperationMetricAnalysisScheduleResponse
    metric_dispatch: CommercialOperationMetricAnalysisDispatchQueueResponse | None = None
    metric_claims: CommercialOperationMetricDispatchClaimListResponse | None = None
    acceptance_gates: list[str] = Field(default_factory=list)
    operator_next_actions: list[str] = Field(default_factory=list)
    server_next_actions: list[str] = Field(default_factory=list)
    client_next_actions: list[str] = Field(default_factory=list)
    boundaries: list[str] = Field(default_factory=list)
    generated_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationProductionClosedLoopAcceptanceOperationResponse(BaseModel):
    """One operation row in the workspace production acceptance summary."""

    operation_id: UUID
    title: str
    status: str
    readiness_status: str
    completion_ratio: float
    current_stage_key: str | None = None
    next_action: str
    ready_for_customer_machine_execution: bool = False
    ready_for_metric_feedback: bool = False
    ready_for_next_cycle: bool = False
    staleness_status: str = "none"
    waiting_seconds: int = 0
    escalation_recommended: bool = False
    blocking_reasons: list[str] = Field(default_factory=list)
    operator_next_actions: list[str] = Field(default_factory=list)


class CommercialOperationProductionClosedLoopAcceptanceSummaryResponse(BaseModel):
    """Workspace-level production closed-loop acceptance summary."""

    workspace_id: str
    acceptance_status: str
    operation_count: int = 0
    accepted_count: int = 0
    ready_for_customer_machine_execution_count: int = 0
    ready_for_metric_feedback_count: int = 0
    ready_for_next_cycle_count: int = 0
    blocked_count: int = 0
    intervention_queue_count: int = 0
    completion_percent: int = 0
    completion_level: str = "not_ready"
    score_breakdown: dict[str, int] = Field(default_factory=dict)
    remaining_gates: list[str] = Field(default_factory=list)
    next_focus: str = "create_or_import_operation_project"
    readiness_status_counts: dict[str, int] = Field(default_factory=dict)
    current_stage_counts: dict[str, int] = Field(default_factory=dict)
    staleness_status_counts: dict[str, int] = Field(default_factory=dict)
    operations: list[CommercialOperationProductionClosedLoopAcceptanceOperationResponse] = Field(default_factory=list)
    top_blockers: list[CommercialOperationProductionClosedLoopAcceptanceOperationResponse] = Field(default_factory=list)
    openclaw_provider_readiness: dict[str, Any] = Field(default_factory=dict)
    release_ready: bool = False
    release_gate_ready_count: int = 0
    release_gate_total_count: int = 0
    release_gate_status_counts: dict[str, int] = Field(default_factory=dict)
    release_gate_checklist: list[dict[str, Any]] = Field(default_factory=list)
    acceptance_gates: list[str] = Field(default_factory=list)
    boundaries: list[str] = Field(default_factory=list)
    generated_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationProductionClosedLoopDeliveryPlanGateResponse(BaseModel):
    """One actionable gate in the production closed-loop delivery plan."""

    gate_key: str
    gate_status: str
    title: str
    owner: str
    priority: int = 0
    completion_impact: int = 0
    required: bool = True
    source: str = "acceptance_summary"
    blocking_reasons: list[str] = Field(default_factory=list)
    operator_next_actions: list[str] = Field(default_factory=list)
    server_next_actions: list[str] = Field(default_factory=list)
    client_next_actions: list[str] = Field(default_factory=list)
    evidence_requirements: list[str] = Field(default_factory=list)
    related_operation_ids: list[UUID] = Field(default_factory=list)
    action_method: str | None = None
    action_endpoint: str | None = None
    external_execution_allowed: bool = False


class CommercialOperationProductionClosedLoopDeliveryPlanResponse(BaseModel):
    """Workspace-level delivery plan derived from production closed-loop acceptance."""

    workspace_id: str
    delivery_status: str
    acceptance_status: str
    completion_percent: int = 0
    completion_level: str = "not_ready"
    next_focus: str
    ready_for_handoff: bool = False
    gate_count: int = 0
    open_gate_count: int = 0
    critical_gate_count: int = 0
    gate_plan: list[CommercialOperationProductionClosedLoopDeliveryPlanGateResponse] = Field(default_factory=list)
    immediate_actions: list[CommercialOperationProductionClosedLoopDeliveryPlanGateResponse] = Field(default_factory=list)
    score_breakdown: dict[str, int] = Field(default_factory=dict)
    openclaw_provider_readiness: dict[str, Any] = Field(default_factory=dict)
    acceptance_summary: dict[str, Any] = Field(default_factory=dict)
    acceptance_gates: list[str] = Field(default_factory=list)
    boundaries: list[str] = Field(default_factory=list)
    generated_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationProductionClosedLoopDeliveryActionStepResponse(BaseModel):
    """One manual action step derived from a production delivery gate."""

    action_key: str
    gate_key: str
    operation_id: UUID | None = None
    target_console: str
    action_status: str
    title: str
    owner: str
    method: str | None = None
    endpoint: str | None = None
    requires_operator_confirmation: bool = True
    external_execution_allowed: bool = False
    server_side_external_execution: bool = False
    blocked_by: list[str] = Field(default_factory=list)
    evidence_requirements: list[str] = Field(default_factory=list)
    operator_next_actions: list[str] = Field(default_factory=list)
    server_next_actions: list[str] = Field(default_factory=list)
    client_next_actions: list[str] = Field(default_factory=list)
    payload_template: dict[str, Any] = Field(default_factory=dict)
    guardrails: list[str] = Field(default_factory=list)


class CommercialOperationProductionClosedLoopDeliveryActionPackageResponse(BaseModel):
    """One delivery gate packaged for server or customer-machine action surfaces."""

    gate_key: str
    gate_status: str
    title: str
    owner: str
    priority: int = 0
    target_console: str
    action_status: str
    action_count: int = 0
    related_operation_ids: list[UUID] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)
    recommended_action_key: str | None = None
    action_steps: list[CommercialOperationProductionClosedLoopDeliveryActionStepResponse] = Field(default_factory=list)
    external_execution_allowed: bool = False


class CommercialOperationProductionClosedLoopDeliveryActionPackageListResponse(BaseModel):
    """Workspace-level action packages for open production delivery gates."""

    workspace_id: str
    action_package_status: str
    delivery_status: str
    acceptance_status: str
    completion_percent: int = 0
    next_focus: str
    package_count: int = 0
    step_count: int = 0
    immediate_package_count: int = 0
    gate_packages: list[CommercialOperationProductionClosedLoopDeliveryActionPackageResponse] = Field(default_factory=list)
    immediate_action_packages: list[CommercialOperationProductionClosedLoopDeliveryActionPackageResponse] = Field(default_factory=list)
    delivery_plan: dict[str, Any] = Field(default_factory=dict)
    acceptance_gates: list[str] = Field(default_factory=list)
    boundaries: list[str] = Field(default_factory=list)
    generated_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationProductionClosedLoopDeliveryRemediationResponse(BaseModel):
    """One remediation mapping for a blocked production delivery gate."""

    remediation_key: str
    gate_key: str
    gate_status: str
    title: str
    owner: str
    priority: int = 0
    target_console: str
    action_status: str
    related_operation_ids: list[UUID] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)
    recommended_sequence: list[str] = Field(default_factory=list)
    primary_method: str | None = None
    primary_endpoint: str | None = None
    secondary_endpoints: list[dict[str, Any]] = Field(default_factory=list)
    expected_evidence: list[str] = Field(default_factory=list)
    existing_records_needed: list[str] = Field(default_factory=list)
    completion_gate: str
    current_evidence_status: str = "no_evidence_record"
    latest_evidence_record_id: UUID | None = None
    latest_evidence_summary: str | None = None
    source_action_key: str | None = None
    requires_operator_confirmation: bool = True
    can_be_started_from_server: bool = False
    can_be_started_from_customer_machine: bool = False
    automation_allowed: bool = False
    external_execution_allowed: bool = False
    runbook_references: list[str] = Field(default_factory=list)
    handoff_notes: list[str] = Field(default_factory=list)
    guardrails: list[str] = Field(default_factory=list)


class CommercialOperationProductionClosedLoopDeliveryRemediationMapResponse(BaseModel):
    """Workspace-level remediation map for blocked production delivery gates."""

    workspace_id: str
    remediation_status: str
    delivery_status: str
    acceptance_status: str
    completion_percent: int = 0
    next_focus: str
    remediation_count: int = 0
    immediate_remediation_count: int = 0
    remediations: list[CommercialOperationProductionClosedLoopDeliveryRemediationResponse] = Field(default_factory=list)
    immediate_remediations: list[CommercialOperationProductionClosedLoopDeliveryRemediationResponse] = Field(default_factory=list)
    action_packages: dict[str, Any] = Field(default_factory=dict)
    evidence_records: dict[str, Any] = Field(default_factory=dict)
    acceptance_gates: list[str] = Field(default_factory=list)
    boundaries: list[str] = Field(default_factory=list)
    generated_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderStatus = Literal[
    "assigned",
    "in_progress",
    "blocked",
    "completed",
    "needs_follow_up",
    "dismissed",
]


class CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderRequest(BaseModel):
    """Operator work-order status for one delivery remediation mapping."""

    remediation_key: str | None = None
    gate_key: str | None = None
    operation_id: UUID | None = None
    work_order_status: CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderStatus = "in_progress"
    assignee: str | None = Field(default=None, max_length=255)
    operator_confirmed: bool = False
    evidence_links: list[dict[str, Any]] = Field(default_factory=list)
    work_summary: str | None = Field(default=None, max_length=2000)
    operator_notes: str | None = Field(default=None, max_length=2000)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderRecordResponse(BaseModel):
    """Persisted work-order status for one delivery remediation mapping."""

    work_order_id: UUID
    workspace_id: str
    operation_id: UUID
    remediation_key: str
    gate_key: str
    work_order_status: CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderStatus
    assignee: str | None = None
    operator_confirmed: bool = False
    target_console: str
    primary_endpoint: str | None = None
    completion_gate: str
    evidence_links: list[dict[str, Any]] = Field(default_factory=list)
    work_summary: str | None = None
    operator_notes: str | None = None
    contract_snapshot: dict[str, Any] = Field(default_factory=dict)
    boundary_checks: list[str] = Field(default_factory=list)
    created_by: str | None = None
    created_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)
    boundaries: list[str] = Field(default_factory=list)


class CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderListResponse(BaseModel):
    """Workspace-level delivery remediation work-order records."""

    workspace_id: str
    work_order_count: int = 0
    latest_record: CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderRecordResponse | None = None
    records: list[CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderRecordResponse] = Field(default_factory=list)
    acceptance_gates: list[str] = Field(default_factory=list)
    boundaries: list[str] = Field(default_factory=list)
    generated_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderCoverageItemResponse(BaseModel):
    """Coverage status for one remediation item and its latest work order."""

    remediation_key: str
    gate_key: str
    gate_status: str
    title: str
    owner: str
    priority: int
    target_console: str
    coverage_status: str
    work_order_required: bool = True
    work_order_count: int = 0
    latest_work_order_id: UUID | None = None
    latest_work_order_status: str | None = None
    latest_work_order_assignee: str | None = None
    latest_work_order_operator_confirmed: bool = False
    latest_work_order_created_at: datetime | None = None
    latest_readiness_refresh_id: UUID | None = None
    latest_readiness_refresh_status: str | None = None
    latest_readiness_refresh_next_action: str | None = None
    current_evidence_status: str
    completion_gate: str
    next_action: str
    blocking_reasons: list[str] = Field(default_factory=list)
    boundaries: list[str] = Field(default_factory=list)


class CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderCoverageResponse(BaseModel):
    """Workspace-level coverage of remediation items by operator work orders."""

    workspace_id: str
    coverage_status: str
    remediation_status: str
    completion_percent: int = 0
    coverage_percent: int = 0
    remediation_count: int = 0
    work_ordered_count: int = 0
    unassigned_count: int = 0
    in_progress_count: int = 0
    completed_count: int = 0
    readiness_refreshed_count: int = 0
    blocked_count: int = 0
    next_focus: str
    items: list[CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderCoverageItemResponse] = Field(default_factory=list)
    unassigned_items: list[CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderCoverageItemResponse] = Field(default_factory=list)
    in_progress_items: list[CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderCoverageItemResponse] = Field(default_factory=list)
    acceptance_gates: list[str] = Field(default_factory=list)
    boundaries: list[str] = Field(default_factory=list)
    generated_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderAssignmentRequest(BaseModel):
    """Assign work orders for currently unassigned delivery remediation items."""

    assignee: str = Field(..., min_length=1, max_length=255)
    operator_confirmed: bool = False
    platform: str | None = None
    force_metric_due: bool = False
    limit: int = Field(default=25, ge=1, le=50)
    scan_limit: int = Field(default=50, ge=1, le=100)
    work_summary: str | None = Field(default=None, max_length=2000)
    operator_notes: str | None = Field(default=None, max_length=2000)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderAssignmentResponse(BaseModel):
    """Result of assigning missing delivery remediation work orders."""

    workspace_id: str
    assignment_status: str
    requested_count: int = 0
    created_count: int = 0
    skipped_count: int = 0
    assignee: str
    records: list[CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderRecordResponse] = Field(default_factory=list)
    coverage_after: CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderCoverageResponse
    acceptance_gates: list[str] = Field(default_factory=list)
    boundaries: list[str] = Field(default_factory=list)
    generated_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderExecutionPrepItemResponse(BaseModel):
    """Execution-prep package for one delivery remediation work order."""

    prep_key: str
    remediation_key: str
    gate_key: str
    gate_status: str
    title: str
    owner: str
    priority: int = 0
    operation_id: UUID | None = None
    prep_status: str
    coverage_status: str
    work_order_required: bool = True
    work_order_count: int = 0
    latest_work_order_id: UUID | None = None
    latest_work_order_status: str | None = None
    latest_work_order_assignee: str | None = None
    latest_work_order_operator_confirmed: bool = False
    latest_work_order: CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderRecordResponse | None = None
    latest_readiness_refresh_id: UUID | None = None
    latest_readiness_refresh_status: str | None = None
    latest_readiness_refresh_next_action: str | None = None
    target_console: str
    target_method: str
    target_endpoint: str | None = None
    completion_gate: str
    source_action_key: str | None = None
    current_evidence_status: str
    requires_customer_machine: bool = False
    requires_server_operator: bool = False
    operator_approval_required: bool = True
    operator_confirmed: bool = False
    external_execution_allowed: bool = False
    server_side_external_execution: bool = False
    evidence_requirements: list[str] = Field(default_factory=list)
    prerequisites: list[str] = Field(default_factory=list)
    operator_checklist: list[str] = Field(default_factory=list)
    execution_payload_template: dict[str, Any] = Field(default_factory=dict)
    runbook_references: list[str] = Field(default_factory=list)
    guardrails: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)
    next_action: str
    boundary_checks: list[str] = Field(default_factory=list)
    boundaries: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderExecutionPrepResponse(BaseModel):
    """Workspace-level execution-prep packages for delivery remediation work orders."""

    workspace_id: str
    prep_status: str
    coverage_status: str
    remediation_status: str
    completion_percent: int = 0
    coverage_percent: int = 0
    remediation_count: int = 0
    prep_count: int = 0
    ready_count: int = 0
    waiting_assignment_count: int = 0
    blocked_count: int = 0
    completed_count: int = 0
    readiness_refreshed_count: int = 0
    customer_machine_count: int = 0
    server_operator_count: int = 0
    next_focus: str
    items: list[CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderExecutionPrepItemResponse] = Field(default_factory=list)
    ready_items: list[CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderExecutionPrepItemResponse] = Field(default_factory=list)
    waiting_assignment_items: list[CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderExecutionPrepItemResponse] = Field(default_factory=list)
    acceptance_gates: list[str] = Field(default_factory=list)
    boundaries: list[str] = Field(default_factory=list)
    generated_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderCompletionRequest(BaseModel):
    """Complete a delivery remediation work order after approved manual execution evidence is available."""

    work_order_id: UUID | None = None
    remediation_key: str | None = None
    gate_key: str | None = None
    operation_id: UUID | None = None
    completed_by: str | None = Field(default=None, max_length=255)
    operator_confirmed: bool = False
    evidence_links: list[dict[str, Any]] = Field(default_factory=list)
    completion_summary: str | None = Field(default=None, max_length=2000)
    operator_notes: str | None = Field(default=None, max_length=2000)
    platform: str | None = None
    force_metric_due: bool = False
    limit: int = Field(default=25, ge=1, le=50)
    scan_limit: int = Field(default=50, ge=1, le=100)
    work_order_limit: int = Field(default=200, ge=1, le=500)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderCompletionResponse(BaseModel):
    """Result of completing a delivery remediation work order from execution prep."""

    workspace_id: str
    completion_status: str
    completed_record: CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderRecordResponse
    coverage_after: CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderCoverageResponse
    execution_prep_after: CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderExecutionPrepResponse
    readiness_refresh_required: bool = True
    readiness_refresh_next_action: str
    acceptance_gates: list[str] = Field(default_factory=list)
    boundaries: list[str] = Field(default_factory=list)
    generated_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderReadinessRefreshRequest(BaseModel):
    """Refresh production readiness after completed delivery remediation work orders."""

    operation_id: UUID | None = None
    remediation_key: str | None = Field(default=None, max_length=255)
    gate_key: str | None = Field(default=None, max_length=255)
    platform: str | None = Field(default=None, max_length=80)
    force_metric_due: bool = False
    operator_confirmed: bool = False
    refresh_notes: str | None = Field(default=None, max_length=2000)
    limit: int = Field(default=25, ge=1, le=50)
    scan_limit: int = Field(default=50, ge=1, le=100)
    work_order_limit: int = Field(default=200, ge=1, le=500)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderReadinessRefreshRecordResponse(BaseModel):
    """Audited readiness refresh record for completed delivery remediation work orders."""

    refresh_id: UUID
    workspace_id: str
    operation_id: UUID
    remediation_key: str | None = None
    gate_key: str | None = None
    completed_work_order_ids: list[UUID] = Field(default_factory=list)
    remediation_keys: list[str] = Field(default_factory=list)
    gate_keys: list[str] = Field(default_factory=list)
    refresh_status: str
    readiness_status: str
    current_stage_key: str | None = None
    current_stage_status: str | None = None
    next_action_key: str
    operator_confirmed: bool = False
    refresh_notes: str | None = None
    refreshed_by: str | None = None
    refreshed_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)
    boundaries: list[str] = Field(default_factory=list)


class CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderReadinessRefreshResponse(BaseModel):
    """Readiness and next-action snapshot after remediation work-order completion."""

    workspace_id: str
    operation_id: UUID
    refresh_id: UUID
    refresh_status: str
    coverage_status: str
    execution_prep_status: str
    readiness_status: str
    current_stage_key: str | None = None
    current_stage_status: str | None = None
    next_action_key: str
    completed_work_order_count: int = 0
    readiness_refreshed_count: int = 0
    completed_items: list[CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderExecutionPrepItemResponse] = Field(default_factory=list)
    coverage_after: CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderCoverageResponse
    execution_prep_after: CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderExecutionPrepResponse
    readiness: dict[str, Any] = Field(default_factory=dict)
    next_action: dict[str, Any] = Field(default_factory=dict)
    refresh_record: CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderReadinessRefreshRecordResponse
    readiness_refresh_required: bool = False
    operator_confirmed: bool = False
    refresh_notes: str | None = None
    acceptance_gates: list[str] = Field(default_factory=list)
    boundaries: list[str] = Field(default_factory=list)
    generated_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationProductionClosedLoopDeliveryAuditBlockerClearanceItemResponse(BaseModel):
    """One production audit blocker mapped to clearance ownership and work-order state."""

    blocker_key: str
    source: str
    severity: str
    title: str
    message: str
    operation_id: UUID | None = None
    operation_title: str | None = None
    gate_key: str | None = None
    remediation_key: str | None = None
    target_console: str
    target_endpoint: str | None = None
    owner: str
    priority: int = 0
    current_state: str
    coverage_status: str | None = None
    prep_status: str | None = None
    latest_work_order_id: UUID | None = None
    latest_work_order_status: str | None = None
    latest_readiness_refresh_status: str | None = None
    recommended_action: str
    expected: str | None = None
    actual: str | None = None
    can_be_resolved_by_ui: bool = False
    external_dependency_required: bool = False
    operator_approval_required: bool = True
    runbook_references: list[str] = Field(default_factory=list)
    boundaries: list[str] = Field(default_factory=list)


class CommercialOperationProductionClosedLoopDeliveryAuditBlockerClearancePlanResponse(BaseModel):
    """Production audit blocker clearance plan joined with remediation work-order state."""

    workspace_id: str
    clearance_status: str
    production_config_ready: bool = False
    acceptance_summary_ready: bool = False
    blocker_count: int = 0
    external_dependency_count: int = 0
    ui_clearable_count: int = 0
    work_ordered_count: int = 0
    ready_for_execution_count: int = 0
    readiness_refreshed_count: int = 0
    next_focus: str
    items: list[CommercialOperationProductionClosedLoopDeliveryAuditBlockerClearanceItemResponse] = Field(default_factory=list)
    production_config_findings: list[dict[str, Any]] = Field(default_factory=list)
    acceptance_summary: dict[str, Any] = Field(default_factory=dict)
    remediation_map: CommercialOperationProductionClosedLoopDeliveryRemediationMapResponse
    work_order_coverage: CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderCoverageResponse
    execution_prep: CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderExecutionPrepResponse
    acceptance_gates: list[str] = Field(default_factory=list)
    boundaries: list[str] = Field(default_factory=list)
    generated_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationProductionClosedLoopDeliveryAuditBlockerWorkOrderAssignmentRequest(BaseModel):
    """Assign remediation work orders for production audit blockers mapped to delivery gates."""

    assignee: str = Field(..., min_length=1, max_length=255)
    operator_confirmed: bool = False
    platform: str | None = Field(default=None, max_length=80)
    force_metric_due: bool = False
    limit: int = Field(default=25, ge=1, le=50)
    scan_limit: int = Field(default=50, ge=1, le=100)
    work_order_limit: int = Field(default=200, ge=1, le=500)
    include_external_dependencies: bool = True
    work_summary: str | None = Field(default=None, max_length=2000)
    operator_notes: str | None = Field(default=None, max_length=2000)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationProductionClosedLoopDeliveryAuditBlockerWorkOrderAssignmentSkippedItemResponse(BaseModel):
    """One audit blocker that was not converted into a remediation work order."""

    blocker_key: str | None = None
    source: str | None = None
    gate_key: str | None = None
    remediation_key: str | None = None
    reason: str
    external_dependency_required: bool = False


class CommercialOperationProductionClosedLoopDeliveryAuditBlockerWorkOrderAssignmentResponse(BaseModel):
    """Result of assigning delivery audit blocker clearance work orders."""

    workspace_id: str
    assignment_status: str
    blocker_count: int = 0
    assignable_blocker_count: int = 0
    requested_gate_count: int = 0
    created_count: int = 0
    skipped_count: int = 0
    assignee: str
    include_external_dependencies: bool = True
    assigned_gate_keys: list[str] = Field(default_factory=list)
    failed_gate_keys: list[str] = Field(default_factory=list)
    skipped_items: list[CommercialOperationProductionClosedLoopDeliveryAuditBlockerWorkOrderAssignmentSkippedItemResponse] = Field(default_factory=list)
    records: list[CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderRecordResponse] = Field(default_factory=list)
    clearance_plan_before: CommercialOperationProductionClosedLoopDeliveryAuditBlockerClearancePlanResponse
    clearance_plan_after: CommercialOperationProductionClosedLoopDeliveryAuditBlockerClearancePlanResponse
    coverage_after: CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderCoverageResponse
    execution_prep_after: CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderExecutionPrepResponse
    acceptance_gates: list[str] = Field(default_factory=list)
    boundaries: list[str] = Field(default_factory=list)
    generated_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookPackageResponse(BaseModel):
    """Operator runbook handoff package for one production audit blocker group."""

    package_key: str
    title: str
    blocker_keys: list[str] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)
    severity: str
    gate_key: str | None = None
    remediation_key: str | None = None
    target_console: str
    target_endpoint: str | None = None
    owner: str
    priority: int = 0
    external_dependency_required: bool = False
    can_be_resolved_by_ui: bool = False
    operator_approval_required: bool = True
    current_state: str
    coverage_status: str | None = None
    prep_status: str | None = None
    latest_work_order_id: UUID | None = None
    latest_work_order_status: str | None = None
    recommended_actions: list[str] = Field(default_factory=list)
    required_inputs: list[str] = Field(default_factory=list)
    manual_steps: list[str] = Field(default_factory=list)
    verification_commands: list[str] = Field(default_factory=list)
    evidence_requirements: list[str] = Field(default_factory=list)
    runbook_references: list[str] = Field(default_factory=list)
    handoff_notes: list[str] = Field(default_factory=list)
    boundaries: list[str] = Field(default_factory=list)


class CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookPackageListResponse(BaseModel):
    """Workspace-level production delivery audit blocker runbook handoff packages."""

    workspace_id: str
    handoff_status: str
    package_count: int = 0
    external_dependency_package_count: int = 0
    work_ordered_package_count: int = 0
    next_focus: str
    packages: list[CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookPackageResponse] = Field(default_factory=list)
    clearance_plan: CommercialOperationProductionClosedLoopDeliveryAuditBlockerClearancePlanResponse
    acceptance_gates: list[str] = Field(default_factory=list)
    boundaries: list[str] = Field(default_factory=list)
    generated_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceRequest(BaseModel):
    """Operator evidence for a production delivery audit blocker runbook package."""

    package_key: str | None = Field(default=None, max_length=500)
    gate_key: str | None = Field(default=None, max_length=255)
    operation_id: UUID | None = None
    evidence_status: Literal["submitted", "blocked", "resolved", "needs_follow_up", "dismissed"] = "submitted"
    operator_confirmed: bool = False
    evidence_links: list[dict[str, Any]] = Field(default_factory=list)
    evidence_summary: str | None = Field(default=None, max_length=2000)
    operator_notes: str | None = Field(default=None, max_length=2000)
    platform: str | None = Field(default=None, max_length=80)
    force_metric_due: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceRecordResponse(BaseModel):
    """Persisted operator evidence for one production delivery audit blocker runbook package."""

    evidence_record_id: UUID
    workspace_id: str
    operation_id: UUID
    package_key: str
    gate_key: str | None = None
    remediation_key: str | None = None
    evidence_status: Literal["submitted", "blocked", "resolved", "needs_follow_up", "dismissed"]
    operator_confirmed: bool = False
    target_console: str
    current_state: str
    latest_work_order_id: UUID | None = None
    latest_work_order_status: str | None = None
    external_dependency_required: bool = False
    evidence_links: list[dict[str, Any]] = Field(default_factory=list)
    evidence_summary: str | None = None
    operator_notes: str | None = None
    verification_commands: list[str] = Field(default_factory=list)
    required_inputs: list[str] = Field(default_factory=list)
    evidence_requirements: list[str] = Field(default_factory=list)
    runbook_references: list[str] = Field(default_factory=list)
    contract_snapshot: dict[str, Any] = Field(default_factory=dict)
    boundary_checks: list[str] = Field(default_factory=list)
    created_by: str | None = None
    created_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)
    boundaries: list[str] = Field(default_factory=list)


class CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceListResponse(BaseModel):
    """Workspace-level delivery audit blocker runbook evidence records."""

    workspace_id: str
    record_count: int = 0
    latest_record: CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceRecordResponse | None = None
    records: list[CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceRecordResponse] = Field(default_factory=list)
    acceptance_gates: list[str] = Field(default_factory=list)
    boundaries: list[str] = Field(default_factory=list)
    generated_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceCoverageItemResponse(BaseModel):
    """Evidence coverage status for one production audit blocker runbook package."""

    package_key: str
    title: str | None = None
    gate_key: str | None = None
    remediation_key: str | None = None
    target_console: str | None = None
    owner: str | None = None
    priority: int = 0
    external_dependency_required: bool = False
    latest_work_order_id: UUID | None = None
    latest_work_order_status: str | None = None
    evidence_record_count: int = 0
    latest_evidence_record_id: UUID | None = None
    latest_evidence_status: str | None = None
    latest_evidence_summary: str | None = None
    latest_evidence_created_at: datetime | None = None
    latest_evidence_operator_confirmed: bool = False
    coverage_status: str
    next_action: str
    verification_commands: list[str] = Field(default_factory=list)
    evidence_requirements: list[str] = Field(default_factory=list)
    boundaries: list[str] = Field(default_factory=list)


class CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceCoverageResponse(BaseModel):
    """Workspace-level coverage of blocker runbook packages by operator evidence."""

    workspace_id: str
    coverage_status: str
    coverage_percent: int = 0
    package_count: int = 0
    evidenced_count: int = 0
    missing_evidence_count: int = 0
    resolved_count: int = 0
    blocked_count: int = 0
    needs_follow_up_count: int = 0
    dismissed_count: int = 0
    next_focus: str
    items: list[CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceCoverageItemResponse] = Field(default_factory=list)
    missing_items: list[CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceCoverageItemResponse] = Field(default_factory=list)
    blocked_items: list[CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceCoverageItemResponse] = Field(default_factory=list)
    runbook_packages: CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookPackageListResponse
    evidence_records: CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceListResponse
    acceptance_gates: list[str] = Field(default_factory=list)
    boundaries: list[str] = Field(default_factory=list)
    generated_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceReadinessRefreshRequest(BaseModel):
    """Refresh production readiness after all blocker runbook evidence is resolved."""

    operation_id: UUID | None = None
    platform: str | None = Field(default=None, max_length=80)
    force_metric_due: bool = False
    operator_confirmed: bool = False
    refresh_notes: str | None = Field(default=None, max_length=2000)
    limit: int = Field(default=25, ge=1, le=50)
    scan_limit: int = Field(default=50, ge=1, le=100)
    work_order_limit: int = Field(default=200, ge=1, le=500)
    evidence_limit: int = Field(default=200, ge=1, le=500)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceReadinessRefreshRecordResponse(BaseModel):
    """Audited readiness refresh record for resolved blocker runbook evidence."""

    refresh_id: UUID
    workspace_id: str
    operation_id: UUID
    refresh_status: str
    coverage_status: str
    coverage_percent: int = 0
    package_count: int = 0
    resolved_count: int = 0
    missing_evidence_count: int = 0
    blocked_count: int = 0
    needs_follow_up_count: int = 0
    dismissed_count: int = 0
    readiness_status: str
    current_stage_key: str | None = None
    current_stage_status: str | None = None
    next_action_key: str
    operator_confirmed: bool = False
    refresh_notes: str | None = None
    refreshed_by: str | None = None
    refreshed_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)
    boundaries: list[str] = Field(default_factory=list)


class CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceReadinessRefreshResponse(BaseModel):
    """Readiness snapshot after resolved audit blocker runbook evidence."""

    workspace_id: str
    operation_id: UUID
    refresh_id: UUID
    refresh_status: str
    coverage_status: str
    coverage_percent: int = 0
    package_count: int = 0
    resolved_count: int = 0
    next_focus: str
    coverage_before: CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceCoverageResponse
    coverage_after: CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceCoverageResponse
    acceptance_summary_after: CommercialOperationProductionClosedLoopAcceptanceSummaryResponse
    clearance_plan_after: CommercialOperationProductionClosedLoopDeliveryAuditBlockerClearancePlanResponse
    runbook_packages_after: CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookPackageListResponse
    readiness: dict[str, Any] = Field(default_factory=dict)
    next_action: dict[str, Any] = Field(default_factory=dict)
    refresh_record: CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceReadinessRefreshRecordResponse
    operator_confirmed: bool = False
    refresh_notes: str | None = None
    acceptance_gates: list[str] = Field(default_factory=list)
    boundaries: list[str] = Field(default_factory=list)
    generated_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationProductionClosedLoopDeliveryAuditNextActionPlanActionResponse(BaseModel):
    """Owner-routed next action derived from production delivery audit blockers."""

    action_key: str
    title: str
    owner: str
    priority: int = 0
    source_blockers: list[str] = Field(default_factory=list)
    target: str
    target_console: str | None = None
    required_endpoint: str | None = None
    verification_commands: list[str] = Field(default_factory=list)
    evidence_requirements: list[str] = Field(default_factory=list)
    external_dependency_required: bool = False
    can_be_resolved_by_ui: bool = False
    operator_approval_required: bool = True
    boundaries: list[str] = Field(default_factory=list)


class CommercialOperationProductionClosedLoopDeliveryAuditNextActionPlanResponse(BaseModel):
    """Read-only production delivery audit blocker action plan."""

    workspace_id: str
    audit_status: str
    acceptance_status: str
    completion_percent: int = 0
    next_focus: str
    blocker_count: int = 0
    next_action_count: int = 0
    runbook_evidence_coverage_ready: bool = False
    runbook_evidence_readiness_refresh_required: bool = False
    blocking_reasons: list[str] = Field(default_factory=list)
    next_actions: list[CommercialOperationProductionClosedLoopDeliveryAuditNextActionPlanActionResponse] = Field(default_factory=list)
    first_action: CommercialOperationProductionClosedLoopDeliveryAuditNextActionPlanActionResponse | None = None
    acceptance_summary: CommercialOperationProductionClosedLoopAcceptanceSummaryResponse
    clearance_plan: CommercialOperationProductionClosedLoopDeliveryAuditBlockerClearancePlanResponse
    runbook_evidence_coverage: CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceCoverageResponse
    acceptance_gates: list[str] = Field(default_factory=list)
    boundaries: list[str] = Field(default_factory=list)
    generated_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationProductionClosedLoopDeliveryAuditOperatorQueueItemResponse(BaseModel):
    """Operator-workbench item derived from a delivery audit next action."""

    queue_key: str
    action_key: str
    title: str
    owner: str
    priority: int = 0
    resolution_mode: str
    resolution_status: str
    primary_console: str
    primary_label: str
    ui_anchor: str | None = None
    endpoint_method: str | None = None
    endpoint_path: str | None = None
    operator_next_step: str
    source_blockers: list[str] = Field(default_factory=list)
    evidence_requirements: list[str] = Field(default_factory=list)
    verification_commands: list[str] = Field(default_factory=list)
    external_dependency_required: bool = False
    can_be_resolved_by_ui: bool = False
    operator_approval_required: bool = True
    blocked_by_external_dependency: bool = False
    record_count: int = 0
    latest_record_id: UUID | None = None
    latest_record_status: str | None = None
    latest_record_summary: str | None = None
    latest_record_created_at: datetime | None = None
    latest_record_operator_confirmed: bool = False
    boundaries: list[str] = Field(default_factory=list)


class CommercialOperationProductionClosedLoopDeliveryAuditOperatorQueueGroupResponse(BaseModel):
    """Owner bucket for production delivery audit operator queue items."""

    owner: str
    owner_label: str
    queue_status: str
    top_priority: int = 0
    action_count: int = 0
    ui_resolvable_count: int = 0
    external_dependency_count: int = 0
    items: list[CommercialOperationProductionClosedLoopDeliveryAuditOperatorQueueItemResponse] = Field(default_factory=list)


class CommercialOperationProductionClosedLoopDeliveryAuditOperatorQueueResponse(BaseModel):
    """Read-only operator queue for production delivery audit action closure."""

    workspace_id: str
    queue_status: str
    audit_status: str
    acceptance_status: str
    completion_percent: int = 0
    owner_count: int = 0
    action_count: int = 0
    ui_resolvable_count: int = 0
    external_dependency_count: int = 0
    next_owner: str | None = None
    first_item: CommercialOperationProductionClosedLoopDeliveryAuditOperatorQueueItemResponse | None = None
    owner_groups: list[CommercialOperationProductionClosedLoopDeliveryAuditOperatorQueueGroupResponse] = Field(default_factory=list)
    source_plan: CommercialOperationProductionClosedLoopDeliveryAuditNextActionPlanResponse
    acceptance_gates: list[str] = Field(default_factory=list)
    boundaries: list[str] = Field(default_factory=list)
    generated_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


CommercialOperationProductionClosedLoopDeliveryAuditOperatorQueueRecordStatus = Literal[
    "queued",
    "in_progress",
    "blocked",
    "resolved",
    "needs_follow_up",
    "dismissed",
]


class CommercialOperationProductionClosedLoopDeliveryAuditOperatorQueueRecordRequest(BaseModel):
    """Operator status/evidence record for one production delivery audit queue item."""

    queue_key: str | None = Field(default=None, max_length=700)
    action_key: str = Field(max_length=500)
    owner: str | None = Field(default=None, max_length=120)
    operation_id: UUID | None = None
    record_status: CommercialOperationProductionClosedLoopDeliveryAuditOperatorQueueRecordStatus = "in_progress"
    operator_confirmed: bool = False
    evidence_links: list[dict[str, Any]] = Field(default_factory=list)
    evidence_summary: str | None = Field(default=None, max_length=2000)
    operator_notes: str | None = Field(default=None, max_length=2000)
    platform: str | None = Field(default=None, max_length=80)
    force_metric_due: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationProductionClosedLoopDeliveryAuditOperatorQueueRecordResponse(BaseModel):
    """Persisted operator status/evidence record for one production delivery audit queue item."""

    record_id: UUID
    workspace_id: str
    operation_id: UUID
    queue_key: str
    action_key: str
    owner: str
    record_status: CommercialOperationProductionClosedLoopDeliveryAuditOperatorQueueRecordStatus
    operator_confirmed: bool = False
    resolution_mode: str
    resolution_status: str
    primary_console: str
    primary_label: str
    endpoint_method: str | None = None
    endpoint_path: str | None = None
    blocked_by_external_dependency: bool = False
    evidence_links: list[dict[str, Any]] = Field(default_factory=list)
    evidence_summary: str | None = None
    operator_notes: str | None = None
    verification_commands: list[str] = Field(default_factory=list)
    evidence_requirements: list[str] = Field(default_factory=list)
    contract_snapshot: dict[str, Any] = Field(default_factory=dict)
    boundary_checks: list[str] = Field(default_factory=list)
    created_by: str | None = None
    created_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)
    boundaries: list[str] = Field(default_factory=list)


class CommercialOperationProductionClosedLoopDeliveryAuditOperatorQueueRecordListResponse(BaseModel):
    """Workspace-level production delivery audit operator queue records."""

    workspace_id: str
    record_count: int = 0
    latest_record: CommercialOperationProductionClosedLoopDeliveryAuditOperatorQueueRecordResponse | None = None
    records: list[CommercialOperationProductionClosedLoopDeliveryAuditOperatorQueueRecordResponse] = Field(default_factory=list)
    status_counts: dict[str, int] = Field(default_factory=dict)
    operator_confirmed_count: int = 0
    acceptance_gates: list[str] = Field(default_factory=list)
    boundaries: list[str] = Field(default_factory=list)
    generated_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationProductionClosedLoopDeliveryAuditOpenClawProviderHandoffConfigItemResponse(BaseModel):
    """One sanitized OpenClaw provider configuration requirement."""

    config_key: str
    required_state: str
    current_state: str
    configured: bool = False
    secret: bool = False
    blocking: bool = True
    operator_action: str
    evidence_requirement: str
    verification_command: str | None = None
    boundaries: list[str] = Field(default_factory=list)


class CommercialOperationProductionClosedLoopDeliveryAuditOpenClawProviderHandoffResponse(BaseModel):
    """Operator handoff for configuring and verifying the real OpenClaw publish provider."""

    workspace_id: str
    handoff_status: str
    readiness_status: str
    ready: bool = False
    provider: str
    mock: bool = True
    worker_id: UUID | None = None
    worker_name: str | None = None
    required_config_count: int = 0
    missing_config_count: int = 0
    verification_count: int = 0
    next_focus: str
    config_items: list[CommercialOperationProductionClosedLoopDeliveryAuditOpenClawProviderHandoffConfigItemResponse] = Field(default_factory=list)
    verification_commands: list[str] = Field(default_factory=list)
    manual_steps: list[str] = Field(default_factory=list)
    evidence_requirements: list[str] = Field(default_factory=list)
    restart_boundaries: list[str] = Field(default_factory=list)
    provider_readiness: dict[str, Any] = Field(default_factory=dict)
    production_config_findings: list[dict[str, Any]] = Field(default_factory=list)
    acceptance_gates: list[str] = Field(default_factory=list)
    boundaries: list[str] = Field(default_factory=list)
    generated_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


CommercialOperationProductionClosedLoopDeliveryActionEvidenceStatus = Literal[
    "submitted",
    "blocked",
    "resolved",
    "needs_follow_up",
    "dismissed",
]


class CommercialOperationProductionClosedLoopDeliveryActionEvidenceRequest(BaseModel):
    """Operator evidence for a manual production delivery action package."""

    gate_key: str
    action_key: str | None = None
    operation_id: UUID | None = None
    evidence_status: CommercialOperationProductionClosedLoopDeliveryActionEvidenceStatus = "submitted"
    operator_confirmed: bool = False
    evidence_links: list[dict[str, Any]] = Field(default_factory=list)
    evidence_summary: str | None = None
    operator_notes: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationProductionClosedLoopDeliveryActionEvidenceRecordResponse(BaseModel):
    """Persisted operator evidence for one production delivery action package."""

    evidence_record_id: UUID
    workspace_id: str
    operation_id: UUID
    gate_key: str
    action_key: str
    evidence_status: CommercialOperationProductionClosedLoopDeliveryActionEvidenceStatus
    operator_confirmed: bool = False
    target_console: str
    action_status: str
    evidence_links: list[dict[str, Any]] = Field(default_factory=list)
    evidence_summary: str | None = None
    operator_notes: str | None = None
    contract_snapshot: dict[str, Any] = Field(default_factory=dict)
    boundary_checks: list[str] = Field(default_factory=list)
    created_by: str | None = None
    created_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)
    boundaries: list[str] = Field(default_factory=list)


class CommercialOperationProductionClosedLoopDeliveryActionEvidenceListResponse(BaseModel):
    """Workspace-level delivery action package evidence records."""

    workspace_id: str
    record_count: int = 0
    latest_record: CommercialOperationProductionClosedLoopDeliveryActionEvidenceRecordResponse | None = None
    records: list[CommercialOperationProductionClosedLoopDeliveryActionEvidenceRecordResponse] = Field(default_factory=list)
    acceptance_gates: list[str] = Field(default_factory=list)
    boundaries: list[str] = Field(default_factory=list)
    generated_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationProductionClosedLoopActionResponse(BaseModel):
    """One controlled next action for the production closed loop."""

    action_key: str
    stage_key: str
    title: str
    description: str
    action_type: str
    enabled: bool = False
    requires_operator_approval: bool = True
    method: str | None = None
    endpoint: str | None = None
    target_record_id: UUID | None = None
    payload_template: dict[str, Any] = Field(default_factory=dict)
    evidence_requirements: list[str] = Field(default_factory=list)
    review_gates: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)
    expected_result: dict[str, Any] = Field(default_factory=dict)
    boundary: str


class CommercialOperationProductionClosedLoopNextActionResponse(BaseModel):
    """Controlled next-action contract derived from the production closed-loop readiness state."""

    operation_id: UUID
    workspace_id: str
    readiness_status: str
    current_stage_key: str | None = None
    selected_action_key: str
    selected_action: CommercialOperationProductionClosedLoopActionResponse
    action_queue: list[CommercialOperationProductionClosedLoopActionResponse] = Field(default_factory=list)
    operator_checklist: list[str] = Field(default_factory=list)
    server_handoff: dict[str, Any] = Field(default_factory=dict)
    client_handoff: dict[str, Any] = Field(default_factory=dict)
    acceptance_gates: list[str] = Field(default_factory=list)
    boundaries: list[str] = Field(default_factory=list)
    generated_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


CommercialOperationProductionClosedLoopActionAuditStatus = Literal[
    "reviewed",
    "confirmed",
    "submitted",
    "evidence_returned",
    "blocked",
    "cancelled",
    "failed",
]


class CommercialOperationProductionClosedLoopActionAuditCreateRequest(BaseModel):
    """Record one controlled-action review/confirmation/evidence event without executing it."""

    action_key: str = Field(min_length=1, max_length=160)
    stage_key: str | None = Field(default=None, max_length=160)
    action_status: CommercialOperationProductionClosedLoopActionAuditStatus = "confirmed"
    operator_confirmed: bool = False
    target_method: str | None = Field(default=None, max_length=16)
    target_endpoint: str | None = Field(default=None, max_length=600)
    target_record_id: UUID | None = None
    submitted_payload: dict[str, Any] = Field(default_factory=dict)
    evidence_links: list[dict[str, Any]] = Field(default_factory=list)
    evidence_summary: str | None = Field(default=None, max_length=2000)
    execution_summary: str | None = Field(default=None, max_length=2000)
    boundary_checks: list[str] = Field(default_factory=list)
    client_machine_id: str | None = Field(default=None, max_length=160)
    reviewer_notes: str | None = Field(default=None, max_length=2000)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationProductionClosedLoopActionAuditRecordResponse(BaseModel):
    """One persisted controlled-action audit event."""

    audit_id: UUID
    operation_id: UUID
    workspace_id: str
    action_key: str
    stage_key: str | None = None
    action_status: str
    validation_status: str
    blocking_reasons: list[str] = Field(default_factory=list)
    operator_confirmed: bool = False
    target_method: str | None = None
    target_endpoint: str | None = None
    target_record_id: UUID | None = None
    submitted_payload: dict[str, Any] = Field(default_factory=dict)
    evidence_links: list[dict[str, Any]] = Field(default_factory=list)
    evidence_summary: str | None = None
    execution_summary: str | None = None
    boundary_checks: list[str] = Field(default_factory=list)
    client_machine_id: str | None = None
    reviewer_notes: str | None = None
    contract_snapshot: dict[str, Any] = Field(default_factory=dict)
    result_binding_status: str | None = None
    result_record_type: str | None = None
    result_record_id: UUID | None = None
    result_status: str | None = None
    result_endpoint: str | None = None
    result_binding: dict[str, Any] = Field(default_factory=dict)
    result_bindings: list[dict[str, Any]] = Field(default_factory=list)
    readiness_refresh_status: str | None = None
    readiness_refresh: dict[str, Any] = Field(default_factory=dict)
    readiness_refreshes: list[dict[str, Any]] = Field(default_factory=list)
    result_record_validation_status: str | None = None
    result_record_validation: dict[str, Any] = Field(default_factory=dict)
    result_record_validations: list[dict[str, Any]] = Field(default_factory=list)
    created_by: str | None = None
    created_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationProductionClosedLoopActionAuditListResponse(BaseModel):
    """List of controlled-action audit events for one operation."""

    operation_id: UUID
    workspace_id: str
    audit_count: int = 0
    latest_record: CommercialOperationProductionClosedLoopActionAuditRecordResponse | None = None
    records: list[CommercialOperationProductionClosedLoopActionAuditRecordResponse] = Field(default_factory=list)
    counts_by_status: dict[str, int] = Field(default_factory=dict)
    evidence_coverage: dict[str, int | float] = Field(default_factory=dict)
    next_actions: list[str] = Field(default_factory=list)
    operator_checklist: list[dict[str, Any]] = Field(default_factory=list)
    primary_step: dict[str, Any] | None = None
    primary_step_staleness: dict[str, Any] = Field(default_factory=dict)
    boundaries: list[str] = Field(default_factory=list)
    generated_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


CommercialOperationProductionClosedLoopActionResultBindingStatus = Literal[
    "result_recorded",
    "result_failed",
    "evidence_verified",
    "binding_cancelled",
]


class CommercialOperationProductionClosedLoopActionResultBindingRequest(BaseModel):
    """Bind a controlled-action audit record to its returned business result without executing it."""

    binding_status: CommercialOperationProductionClosedLoopActionResultBindingStatus = "result_recorded"
    result_record_type: str = Field(min_length=1, max_length=120)
    result_record_id: UUID | None = None
    result_status: str | None = Field(default=None, max_length=120)
    result_endpoint: str | None = Field(default=None, max_length=600)
    evidence_links: list[dict[str, Any]] = Field(default_factory=list)
    evidence_summary: str | None = Field(default=None, max_length=2000)
    operator_confirmed: bool = False
    binding_notes: str | None = Field(default=None, max_length=2000)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationProductionClosedLoopActionResultBindingResponse(BaseModel):
    """Returned result binding for one controlled-action audit event."""

    operation_id: UUID
    workspace_id: str
    audit_id: UUID
    binding_id: UUID
    binding_status: str
    result_record_type: str
    result_record_id: UUID | None = None
    result_status: str | None = None
    result_endpoint: str | None = None
    evidence_links: list[dict[str, Any]] = Field(default_factory=list)
    evidence_summary: str | None = None
    operator_confirmed: bool = False
    binding_notes: str | None = None
    bound_by: str | None = None
    bound_at: datetime
    audit_record: CommercialOperationProductionClosedLoopActionAuditRecordResponse
    boundaries: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationProductionClosedLoopActionReadinessRefreshRequest(BaseModel):
    """Refresh readiness after a controlled-action result binding without executing the next action."""

    platform: str | None = Field(default=None, max_length=80)
    force_metric_due: bool = False
    operator_confirmed: bool = False
    refresh_notes: str | None = Field(default=None, max_length=2000)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationProductionClosedLoopActionReadinessRefreshResponse(BaseModel):
    """Readiness and next-action snapshot produced after a result binding."""

    operation_id: UUID
    workspace_id: str
    audit_id: UUID
    refresh_id: UUID
    binding_id: UUID | None = None
    refresh_status: str
    underlying_refresh_status: str | None = None
    record_validation_gate_status: str | None = None
    record_validation_required: bool = Field(
        default=False,
        description="True when readiness progress is still waiting for a verified bound result record.",
    )
    record_validation_passed: bool = False
    record_validation_blocking_reasons: list[str] = Field(default_factory=list)
    result_record_validation_status: str | None = None
    result_record_validation: dict[str, Any] = Field(default_factory=dict)
    audit_stage_key: str | None = None
    previous_action_key: str | None = None
    current_stage_key: str | None = None
    current_stage_status: str | None = None
    stage_completed_after_binding: bool = False
    next_action_key: str
    operator_confirmed: bool = False
    refresh_notes: str | None = None
    readiness: CommercialOperationProductionClosedLoopReadinessResponse
    next_action: CommercialOperationProductionClosedLoopNextActionResponse
    audit_record: CommercialOperationProductionClosedLoopActionAuditRecordResponse
    result_binding: dict[str, Any] = Field(default_factory=dict)
    operator_next_actions: list[str] = Field(default_factory=list)
    boundaries: list[str] = Field(default_factory=list)
    refreshed_by: str | None = None
    refreshed_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationProductionClosedLoopActionResultRecordValidationRequest(BaseModel):
    """Validate that a bound controlled-action result references a real project record."""

    operator_confirmed: bool = False
    validation_notes: str | None = Field(default=None, max_length=2000)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationProductionClosedLoopActionResultRecordValidationResponse(BaseModel):
    """Result record reference validation for one controlled-action result binding."""

    operation_id: UUID
    workspace_id: str
    audit_id: UUID
    validation_id: UUID
    binding_id: UUID | None = None
    validation_status: str
    result_record_type: str
    result_record_id: UUID | None = None
    record_exists: bool = False
    workspace_matches: bool = False
    operation_matches: bool = False
    status_matches: bool = False
    status_field: str | None = None
    record_status: str | None = None
    expected_statuses: list[str] = Field(default_factory=list)
    record_summary: dict[str, Any] = Field(default_factory=dict)
    supported_record_types: list[str] = Field(default_factory=list)
    operator_confirmed: bool = False
    validation_notes: str | None = None
    validated_by: str | None = None
    validated_at: datetime
    audit_record: CommercialOperationProductionClosedLoopActionAuditRecordResponse
    result_binding: dict[str, Any] = Field(default_factory=dict)
    boundaries: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


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


class CommercialOperationDigitalHumanDeliveryLinkRequest(BaseModel):
    """Link a generated digital-human delivery asset into the commercial loop."""

    digital_human_video_job_id: UUID
    delivery_asset_id: UUID | None = None
    content_draft_id: UUID | None = None
    step_key: str = Field(default="content_production", min_length=1, max_length=128)
    channel: str | None = Field(default=None, min_length=1, max_length=128)
    title: str | None = Field(default=None, min_length=1, max_length=255)
    purpose: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationDigitalHumanDeliveryLinkResponse(BaseModel):
    """Commercial loop link created from a generated digital-human video."""

    operation_id: UUID
    workspace_id: str
    link_status: Literal["created", "reused"]
    digital_human_video_job_id: UUID
    delivery_asset_id: UUID
    deliverable_ready: bool
    asset_request: CommercialOperationAssetRequestResponse
    next_actions: list[str] = Field(default_factory=list)
    boundaries: list[str] = Field(default_factory=list)


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


class CommercialOperationComfyUIRuntimeSubmitRequest(BaseModel):
    """Submit or refresh a guarded real ComfyUI job for an approved adapter dispatch."""

    client_id: str | None = Field(default=None, min_length=1, max_length=128)
    poll_history: bool = True
    reviewer_notes: str | None = None
    result_summary: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


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


class CommercialOperationComfyUIRuntimeGateCreateRequest(BaseModel):
    """Create a metadata-only ComfyUI runtime gate from a dispatched adapter dispatch."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    runtime_mode: str = Field(default="metadata_only", min_length=1, max_length=32)
    environment_payload: dict[str, Any] = Field(default_factory=dict)
    network_policy: dict[str, Any] = Field(default_factory=dict)
    queue_policy: dict[str, Any] = Field(default_factory=dict)
    secret_policy: dict[str, Any] = Field(default_factory=dict)
    approval_policy: dict[str, Any] = Field(default_factory=dict)
    validation_checks: list[dict[str, Any]] = Field(default_factory=list)
    operator_checklist: list[str] = Field(default_factory=list)
    rollback_plan: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationComfyUIRuntimeGateUpdateRequest(BaseModel):
    """Patch a metadata-only ComfyUI runtime gate before arming."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    runtime_mode: str | None = Field(default=None, min_length=1, max_length=32)
    environment_payload: dict[str, Any] | None = None
    network_policy: dict[str, Any] | None = None
    queue_policy: dict[str, Any] | None = None
    secret_policy: dict[str, Any] | None = None
    approval_policy: dict[str, Any] | None = None
    validation_checks: list[dict[str, Any]] | None = None
    operator_checklist: list[str] | None = None
    rollback_plan: dict[str, Any] | None = None
    result_summary: str | None = None
    failure_reason: str | None = None
    reviewer_notes: str | None = None
    metadata: dict[str, Any] | None = None


class CommercialOperationComfyUIRuntimeGateDecisionRequest(BaseModel):
    """Review, arm, disable, fail, or archive a ComfyUI runtime gate."""

    reviewer_notes: str | None = None
    result_summary: str | None = None
    failure_reason: str | None = None


class CommercialOperationComfyUIRuntimeGateResponse(BaseModel):
    """Commercial operation metadata-only ComfyUI runtime gate response."""

    id: UUID
    workspace_id: str
    operation_id: UUID
    adapter_dispatch_id: UUID
    connection_probe_id: UUID
    execution_plan_id: UUID
    job_request_id: UUID
    preflight_id: UUID
    handoff_id: UUID
    adapter_config_id: UUID | None
    asset_request_id: UUID
    step_key: str
    title: str
    gate_status: str
    runtime_mode: str
    target_url: str | None
    queue_name: str | None
    workflow_name: str
    environment_payload: dict[str, Any]
    network_policy: dict[str, Any]
    queue_policy: dict[str, Any]
    secret_policy: dict[str, Any]
    approval_policy: dict[str, Any]
    validation_checks: list[dict[str, Any]]
    operator_checklist: list[str]
    rollback_plan: dict[str, Any]
    gate_payload: dict[str, Any]
    result_summary: str | None
    failure_reason: str | None
    reviewer_notes: str | None
    planned_by: str | None
    updated_by: str | None
    approved_by: str | None
    armed_by: str | None
    disabled_by: str | None
    archived_by: str | None
    approved_at: datetime | None
    rejected_at: datetime | None
    armed_at: datetime | None
    disabled_at: datetime | None
    failed_at: datetime | None
    archived_at: datetime | None
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(
        cls,
        gate: CommercialOperationComfyUIRuntimeGate,
    ) -> "CommercialOperationComfyUIRuntimeGateResponse":
        return cls(
            id=gate.id,
            workspace_id=gate.workspace_id,
            operation_id=gate.operation_id,
            adapter_dispatch_id=gate.adapter_dispatch_id,
            connection_probe_id=gate.connection_probe_id,
            execution_plan_id=gate.execution_plan_id,
            job_request_id=gate.job_request_id,
            preflight_id=gate.preflight_id,
            handoff_id=gate.handoff_id,
            adapter_config_id=gate.adapter_config_id,
            asset_request_id=gate.asset_request_id,
            step_key=gate.step_key,
            title=gate.title,
            gate_status=gate.gate_status,
            runtime_mode=gate.runtime_mode,
            target_url=gate.target_url,
            queue_name=gate.queue_name,
            workflow_name=gate.workflow_name,
            environment_payload=gate.environment_payload,
            network_policy=gate.network_policy,
            queue_policy=gate.queue_policy,
            secret_policy=gate.secret_policy,
            approval_policy=gate.approval_policy,
            validation_checks=gate.validation_checks,
            operator_checklist=gate.operator_checklist,
            rollback_plan=gate.rollback_plan,
            gate_payload=gate.gate_payload,
            result_summary=gate.result_summary,
            failure_reason=gate.failure_reason,
            reviewer_notes=gate.reviewer_notes,
            planned_by=gate.planned_by,
            updated_by=gate.updated_by,
            approved_by=gate.approved_by,
            armed_by=gate.armed_by,
            disabled_by=gate.disabled_by,
            archived_by=gate.archived_by,
            approved_at=gate.approved_at,
            rejected_at=gate.rejected_at,
            armed_at=gate.armed_at,
            disabled_at=gate.disabled_at,
            failed_at=gate.failed_at,
            archived_at=gate.archived_at,
            metadata=gate.gate_metadata,
            created_at=gate.created_at,
            updated_at=gate.updated_at,
        )


class CommercialOperationComfyUIRuntimeGateListResponse(BaseModel):
    """Commercial operation metadata-only ComfyUI runtime gate list response."""

    operation_id: UUID
    items: list[CommercialOperationComfyUIRuntimeGateResponse]


class CommercialOperationComfyUIRuntimeDryRunCreateRequest(BaseModel):
    """Create a metadata-only ComfyUI runtime dry-run from an armed runtime gate."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    dry_run_mode: str = Field(default="metadata_only", min_length=1, max_length=32)
    adapter_contract: dict[str, Any] = Field(default_factory=dict)
    dry_run_request: dict[str, Any] = Field(default_factory=dict)
    expected_response: dict[str, Any] = Field(default_factory=dict)
    runtime_policy: dict[str, Any] = Field(default_factory=dict)
    validation_checks: list[dict[str, Any]] = Field(default_factory=list)
    operator_checklist: list[str] = Field(default_factory=list)
    rollback_plan: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationComfyUIRuntimeDryRunUpdateRequest(BaseModel):
    """Patch a metadata-only ComfyUI runtime dry-run before validation."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    dry_run_mode: str | None = Field(default=None, min_length=1, max_length=32)
    adapter_contract: dict[str, Any] | None = None
    dry_run_request: dict[str, Any] | None = None
    expected_response: dict[str, Any] | None = None
    runtime_policy: dict[str, Any] | None = None
    validation_checks: list[dict[str, Any]] | None = None
    operator_checklist: list[str] | None = None
    rollback_plan: dict[str, Any] | None = None
    result_summary: str | None = None
    failure_reason: str | None = None
    reviewer_notes: str | None = None
    metadata: dict[str, Any] | None = None


class CommercialOperationComfyUIRuntimeDryRunDecisionRequest(BaseModel):
    """Review, validate, fail, cancel, or archive a ComfyUI runtime dry-run."""

    reviewer_notes: str | None = None
    result_summary: str | None = None
    failure_reason: str | None = None


class CommercialOperationComfyUIRuntimeDryRunResponse(BaseModel):
    """Commercial operation metadata-only ComfyUI runtime dry-run response."""

    id: UUID
    workspace_id: str
    operation_id: UUID
    runtime_gate_id: UUID
    adapter_dispatch_id: UUID
    connection_probe_id: UUID
    execution_plan_id: UUID
    job_request_id: UUID
    preflight_id: UUID
    handoff_id: UUID
    adapter_config_id: UUID | None
    asset_request_id: UUID
    step_key: str
    title: str
    dry_run_status: str
    dry_run_mode: str
    target_url: str | None
    queue_name: str | None
    workflow_name: str
    adapter_contract: dict[str, Any]
    dry_run_request: dict[str, Any]
    expected_response: dict[str, Any]
    runtime_policy: dict[str, Any]
    validation_checks: list[dict[str, Any]]
    operator_checklist: list[str]
    rollback_plan: dict[str, Any]
    dry_run_payload: dict[str, Any]
    result_summary: str | None
    failure_reason: str | None
    reviewer_notes: str | None
    planned_by: str | None
    updated_by: str | None
    approved_by: str | None
    validated_by: str | None
    cancelled_by: str | None
    archived_by: str | None
    approved_at: datetime | None
    rejected_at: datetime | None
    validated_at: datetime | None
    failed_at: datetime | None
    cancelled_at: datetime | None
    archived_at: datetime | None
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(
        cls,
        dry_run: CommercialOperationComfyUIRuntimeDryRun,
    ) -> "CommercialOperationComfyUIRuntimeDryRunResponse":
        return cls(
            id=dry_run.id,
            workspace_id=dry_run.workspace_id,
            operation_id=dry_run.operation_id,
            runtime_gate_id=dry_run.runtime_gate_id,
            adapter_dispatch_id=dry_run.adapter_dispatch_id,
            connection_probe_id=dry_run.connection_probe_id,
            execution_plan_id=dry_run.execution_plan_id,
            job_request_id=dry_run.job_request_id,
            preflight_id=dry_run.preflight_id,
            handoff_id=dry_run.handoff_id,
            adapter_config_id=dry_run.adapter_config_id,
            asset_request_id=dry_run.asset_request_id,
            step_key=dry_run.step_key,
            title=dry_run.title,
            dry_run_status=dry_run.dry_run_status,
            dry_run_mode=dry_run.dry_run_mode,
            target_url=dry_run.target_url,
            queue_name=dry_run.queue_name,
            workflow_name=dry_run.workflow_name,
            adapter_contract=dry_run.adapter_contract,
            dry_run_request=dry_run.dry_run_request,
            expected_response=dry_run.expected_response,
            runtime_policy=dry_run.runtime_policy,
            validation_checks=dry_run.validation_checks,
            operator_checklist=dry_run.operator_checklist,
            rollback_plan=dry_run.rollback_plan,
            dry_run_payload=dry_run.dry_run_payload,
            result_summary=dry_run.result_summary,
            failure_reason=dry_run.failure_reason,
            reviewer_notes=dry_run.reviewer_notes,
            planned_by=dry_run.planned_by,
            updated_by=dry_run.updated_by,
            approved_by=dry_run.approved_by,
            validated_by=dry_run.validated_by,
            cancelled_by=dry_run.cancelled_by,
            archived_by=dry_run.archived_by,
            approved_at=dry_run.approved_at,
            rejected_at=dry_run.rejected_at,
            validated_at=dry_run.validated_at,
            failed_at=dry_run.failed_at,
            cancelled_at=dry_run.cancelled_at,
            archived_at=dry_run.archived_at,
            metadata=dry_run.dry_run_metadata,
            created_at=dry_run.created_at,
            updated_at=dry_run.updated_at,
        )


class CommercialOperationComfyUIRuntimeDryRunListResponse(BaseModel):
    """Commercial operation metadata-only ComfyUI runtime dry-run list response."""

    operation_id: UUID
    items: list[CommercialOperationComfyUIRuntimeDryRunResponse]


class CommercialOperationComfyUIRuntimeActivationCreateRequest(BaseModel):
    """Create a metadata-only ComfyUI runtime activation request from a validated dry-run."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    activation_mode: str = Field(default="metadata_only", min_length=1, max_length=32)
    server_switch_name: str = Field(default="COMFYUI_RUNTIME_ENABLED", min_length=1, max_length=128)
    activation_request: dict[str, Any] = Field(default_factory=dict)
    switch_audit: dict[str, Any] = Field(default_factory=dict)
    runtime_guardrails: dict[str, Any] = Field(default_factory=dict)
    validation_checks: list[dict[str, Any]] = Field(default_factory=list)
    operator_checklist: list[str] = Field(default_factory=list)
    rollback_plan: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationComfyUIRuntimeActivationUpdateRequest(BaseModel):
    """Patch a metadata-only ComfyUI runtime activation request before scheduling."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    activation_mode: str | None = Field(default=None, min_length=1, max_length=32)
    server_switch_name: str | None = Field(default=None, min_length=1, max_length=128)
    activation_request: dict[str, Any] | None = None
    switch_audit: dict[str, Any] | None = None
    runtime_guardrails: dict[str, Any] | None = None
    validation_checks: list[dict[str, Any]] | None = None
    operator_checklist: list[str] | None = None
    rollback_plan: dict[str, Any] | None = None
    result_summary: str | None = None
    failure_reason: str | None = None
    reviewer_notes: str | None = None
    metadata: dict[str, Any] | None = None


class CommercialOperationComfyUIRuntimeActivationDecisionRequest(BaseModel):
    """Review, schedule, fail, cancel, or archive a ComfyUI runtime activation request."""

    reviewer_notes: str | None = None
    result_summary: str | None = None
    failure_reason: str | None = None


class CommercialOperationComfyUIRuntimeActivationResponse(BaseModel):
    """Commercial operation metadata-only ComfyUI runtime activation response."""

    id: UUID
    workspace_id: str
    operation_id: UUID
    runtime_dry_run_id: UUID
    runtime_gate_id: UUID
    adapter_dispatch_id: UUID
    connection_probe_id: UUID
    execution_plan_id: UUID
    job_request_id: UUID
    preflight_id: UUID
    handoff_id: UUID
    adapter_config_id: UUID | None
    asset_request_id: UUID
    step_key: str
    title: str
    activation_status: str
    activation_mode: str
    target_url: str | None
    queue_name: str | None
    workflow_name: str
    server_switch_name: str
    activation_request: dict[str, Any]
    switch_audit: dict[str, Any]
    runtime_guardrails: dict[str, Any]
    validation_checks: list[dict[str, Any]]
    operator_checklist: list[str]
    rollback_plan: dict[str, Any]
    activation_payload: dict[str, Any]
    result_summary: str | None
    failure_reason: str | None
    reviewer_notes: str | None
    planned_by: str | None
    updated_by: str | None
    approved_by: str | None
    scheduled_by: str | None
    cancelled_by: str | None
    archived_by: str | None
    approved_at: datetime | None
    rejected_at: datetime | None
    scheduled_at: datetime | None
    failed_at: datetime | None
    cancelled_at: datetime | None
    archived_at: datetime | None
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(
        cls,
        activation: CommercialOperationComfyUIRuntimeActivation,
    ) -> "CommercialOperationComfyUIRuntimeActivationResponse":
        return cls(
            id=activation.id,
            workspace_id=activation.workspace_id,
            operation_id=activation.operation_id,
            runtime_dry_run_id=activation.runtime_dry_run_id,
            runtime_gate_id=activation.runtime_gate_id,
            adapter_dispatch_id=activation.adapter_dispatch_id,
            connection_probe_id=activation.connection_probe_id,
            execution_plan_id=activation.execution_plan_id,
            job_request_id=activation.job_request_id,
            preflight_id=activation.preflight_id,
            handoff_id=activation.handoff_id,
            adapter_config_id=activation.adapter_config_id,
            asset_request_id=activation.asset_request_id,
            step_key=activation.step_key,
            title=activation.title,
            activation_status=activation.activation_status,
            activation_mode=activation.activation_mode,
            target_url=activation.target_url,
            queue_name=activation.queue_name,
            workflow_name=activation.workflow_name,
            server_switch_name=activation.server_switch_name,
            activation_request=activation.activation_request,
            switch_audit=activation.switch_audit,
            runtime_guardrails=activation.runtime_guardrails,
            validation_checks=activation.validation_checks,
            operator_checklist=activation.operator_checklist,
            rollback_plan=activation.rollback_plan,
            activation_payload=activation.activation_payload,
            result_summary=activation.result_summary,
            failure_reason=activation.failure_reason,
            reviewer_notes=activation.reviewer_notes,
            planned_by=activation.planned_by,
            updated_by=activation.updated_by,
            approved_by=activation.approved_by,
            scheduled_by=activation.scheduled_by,
            cancelled_by=activation.cancelled_by,
            archived_by=activation.archived_by,
            approved_at=activation.approved_at,
            rejected_at=activation.rejected_at,
            scheduled_at=activation.scheduled_at,
            failed_at=activation.failed_at,
            cancelled_at=activation.cancelled_at,
            archived_at=activation.archived_at,
            metadata=activation.activation_metadata,
            created_at=activation.created_at,
            updated_at=activation.updated_at,
        )


class CommercialOperationComfyUIRuntimeActivationListResponse(BaseModel):
    """Commercial operation metadata-only ComfyUI runtime activation list response."""

    operation_id: UUID
    items: list[CommercialOperationComfyUIRuntimeActivationResponse]


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


CommercialOperationLoopStageStatusLiteral = Literal[
    "complete",
    "in_progress",
    "review_required",
    "blocked",
    "missing",
]


class CommercialOperationLoopStageResponse(BaseModel):
    """One readable stage in the commercial operation loop protocol."""

    stage_key: str
    title: str
    owner: str
    status: CommercialOperationLoopStageStatusLiteral
    summary: str
    next_action: str
    blocked_reasons: list[str] = Field(default_factory=list)
    related_records: list[dict[str, Any]] = Field(default_factory=list)
    operator_actions: list[str] = Field(default_factory=list)
    server_actions: list[str] = Field(default_factory=list)
    client_actions: list[str] = Field(default_factory=list)


class CommercialOperationLoopSummaryResponse(BaseModel):
    """Server/customer-console operation loop summary."""

    operation_id: UUID
    workspace_id: str
    title: str
    objective: str
    loop_status: str
    current_stage_key: str | None
    next_action: str
    completion_ratio: float = Field(ge=0, le=1)
    stages: list[CommercialOperationLoopStageResponse]
    counts: dict[str, int]
    execution_protocol: dict[str, Any]
    readiness: list[dict[str, Any]]
    boundaries: list[str]
    generated_at: datetime


CommercialOperationAgentSkillStatusLiteral = Literal[
    "complete",
    "active",
    "needs_review",
    "blocked",
    "waiting",
]


class CommercialOperationAgentSkillResponse(BaseModel):
    """One commercial-operation skill routed to an Agent and optional Tool."""

    skill_key: str
    display_name: str
    owner_agent: str
    tool_name: str | None = None
    stage_key: str
    status: CommercialOperationAgentSkillStatusLiteral
    summary: str
    next_action: str
    inputs: list[str] = Field(default_factory=list)
    outputs: list[str] = Field(default_factory=list)
    boundary: str


class CommercialOperationAgentDecisionResponse(BaseModel):
    """Readable controller decision for the current commercial-operation loop."""

    decision_key: str
    agent_name: str
    skill_key: str
    decision_type: str
    status: str
    rationale: str
    next_action: str
    evidence: list[str] = Field(default_factory=list)


class CommercialOperationSpecialistTrackResponse(BaseModel):
    """One specialist track available below the global commercial-operation Agent."""

    track_key: str
    display_name: str
    owner_agent: str
    stage_key: str | None = None
    status: str
    priority: int = Field(ge=0)
    trigger_signals: list[str] = Field(default_factory=list)
    required_inputs: list[str] = Field(default_factory=list)
    expected_outputs: list[str] = Field(default_factory=list)
    boundary: str
    execution_boundary: str | None = None
    available_actions: list[str] = Field(default_factory=list)
    quality_gates: list[str] = Field(default_factory=list)
    blocked_by: list[str] = Field(default_factory=list)
    production_intervention_recommended_action: dict[str, Any] = Field(default_factory=dict)
    production_delivery_recommended_gate: dict[str, Any] = Field(default_factory=dict)
    next_action: str


class CommercialOperationRoutingDecisionResponse(BaseModel):
    """Global commercial-operation Agent routing decision."""

    decision_key: str
    controller_agent: str
    decision_mode: str = "deterministic_stage_and_signal_router"
    confidence: float = Field(default=0.0, ge=0, le=1)
    current_stage: str | None
    recommended_track: str
    selected_track_status: str | None = None
    selected_skill_key: str | None = None
    selected_agents: list[str] = Field(default_factory=list)
    required_knowledge_collections: list[str] = Field(default_factory=list)
    required_inputs: list[str] = Field(default_factory=list)
    blocked_by: list[str] = Field(default_factory=list)
    reason_codes: list[str] = Field(default_factory=list)
    quality_gates: list[str] = Field(default_factory=list)
    next_executable_contract: dict[str, Any] = Field(default_factory=dict)
    production_intervention_required: bool = False
    production_intervention_recommended_action: dict[str, Any] = Field(default_factory=dict)
    production_intervention_queue_summary: dict[str, Any] = Field(default_factory=dict)
    production_delivery_plan_required: bool = False
    production_delivery_recommended_gate: dict[str, Any] = Field(default_factory=dict)
    production_delivery_plan_summary: dict[str, Any] = Field(default_factory=dict)
    rationale: str
    next_action: str
    evidence: list[str] = Field(default_factory=list)


class CommercialOperationAgentSkillOrchestrationResponse(BaseModel):
    """Agent/Skill orchestration view for server and customer-machine consoles."""

    operation_id: UUID
    workspace_id: str
    controller_agent: dict[str, Any]
    orchestration_status: str
    next_skill_key: str | None
    next_action: str
    completion_ratio: float = Field(ge=0, le=1)
    skills: list[CommercialOperationAgentSkillResponse]
    routing_decision: CommercialOperationRoutingDecisionResponse
    specialist_tracks: list[CommercialOperationSpecialistTrackResponse] = Field(default_factory=list)
    production_intervention_queue: dict[str, Any] = Field(default_factory=dict)
    production_delivery_plan: dict[str, Any] = Field(default_factory=dict)
    decisions: list[CommercialOperationAgentDecisionResponse]
    boundaries: list[str]
    generated_at: datetime


CommercialOperationMainAgentAdvanceStatusLiteral = Literal[
    "created",
    "updated",
    "reused",
    "dry_run",
    "blocked",
    "noop",
]


class CommercialOperationMainAgentAdvanceRequest(BaseModel):
    """Advance one safe, reviewable step in the commercial operation loop."""

    dry_run: bool = False
    operator_note: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationMainAgentAdvanceResponse(BaseModel):
    """Main Agent closed-loop advancement result."""

    operation_id: UUID
    workspace_id: str
    advance_status: CommercialOperationMainAgentAdvanceStatusLiteral
    dry_run: bool
    advanced_track: str
    before_stage_key: str | None
    after_stage_key: str | None
    routing_decision: CommercialOperationRoutingDecisionResponse
    created_records: list[dict[str, Any]] = Field(default_factory=list)
    updated_records: list[dict[str, Any]] = Field(default_factory=list)
    reused_records: list[dict[str, Any]] = Field(default_factory=list)
    blocked_by: list[str] = Field(default_factory=list)
    operator_next_actions: list[str] = Field(default_factory=list)
    server_next_actions: list[str] = Field(default_factory=list)
    client_next_actions: list[str] = Field(default_factory=list)
    execution_boundary: str
    operation_loop: dict[str, Any] = Field(default_factory=dict)
    boundaries: list[str] = Field(default_factory=list)
    generated_at: datetime


CommercialOperationVideoAgentRouteLiteral = Literal[
    "auto",
    "digital_human_video",
    "commercial_content",
    "asset_brief",
]


class CommercialOperationVideoAgentOrchestrationRequest(BaseModel):
    """Route a commercial operation into the video-specialist agent chain."""

    route_hint: CommercialOperationVideoAgentRouteLiteral = "auto"
    objective: str | None = Field(default=None, min_length=1, max_length=8000)
    script: str | None = Field(default=None, min_length=1, max_length=20000)
    channel: str = Field(default="short_video", min_length=1, max_length=128)
    style: str = Field(default="realistic commercial operator vlog", min_length=1, max_length=255)
    provider: str | None = Field(default=None, max_length=64)
    source_video_uri: str | None = Field(default=None, min_length=1, max_length=2000)
    scene_image_uri: str | None = Field(default=None, min_length=1, max_length=2000)
    reference_video_uri: str | None = Field(default=None, min_length=1, max_length=2000)
    avatar_asset_id: UUID | None = None
    material_asset_ids: list[UUID] = Field(default_factory=list)
    reference_asset_ids: list[UUID] = Field(default_factory=list)
    target_channels: list[str] = Field(default_factory=list)
    voice_profile: dict[str, Any] = Field(default_factory=dict)
    aspect_ratio: str = Field(default="9:16", max_length=32)
    duration_seconds: float | None = Field(default=None, ge=1.0, le=3600.0)
    needs_ai_virtual_person: bool = True
    allow_real_person_cutout: bool = False
    allow_comfyui_prompt_submission: bool = False
    query: str | None = Field(default=None, min_length=1)
    knowledge_collection: str | None = Field(default=None, min_length=1, max_length=128)
    source_id: str | None = Field(default=None, min_length=1, max_length=255)
    search_mode: SearchMode | None = None
    dense_top_k: int | None = Field(default=None, ge=1, le=100)
    keyword_top_k: int | None = Field(default=None, ge=1, le=100)
    final_top_k: int | None = Field(default=None, ge=1, le=50)
    create_digital_human_job: bool = True
    llm_planning_enabled: bool = True
    prepare_shot_execution_plan: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class CommercialOperationVideoAgentOrchestrationResponse(BaseModel):
    """Commercial main-agent routing result for a digital-human video flow."""

    operation_id: UUID
    workspace_id: str
    controller_agent: dict[str, Any]
    route_decision: dict[str, Any]
    rag_context: dict[str, Any]
    sub_agents: list[dict[str, Any]]
    digital_human_request: dict[str, Any]
    digital_human_job: dict[str, Any] | None = None
    video_agent_plan: dict[str, Any] = Field(default_factory=dict)
    video_analysis_result: dict[str, Any] | None = None
    workflow_selection: dict[str, Any] = Field(default_factory=dict)
    execution_package: dict[str, Any] = Field(default_factory=dict)
    runtime_evidence: dict[str, Any] = Field(default_factory=dict)
    next_actions: list[str] = Field(default_factory=list)
    boundaries: list[str] = Field(default_factory=list)
    generated_at: datetime
