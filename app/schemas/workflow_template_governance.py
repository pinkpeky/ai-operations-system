"""Workflow template governance API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.workflow import (
    WorkflowTemplateAuditLog,
    WorkflowTemplateCompatibilityMatrix,
    WorkflowTemplatePromotion,
    WorkflowTemplateReview,
)
from app.schemas.workflow_template import WorkflowTemplateResponse


ReviewStatusLiteral = Literal["pending", "approved", "rejected", "changes_requested"]


class WorkflowTemplateReviewCreateRequest(BaseModel):
    template_id: UUID
    template_version_id: UUID
    reviewer_id: str | None = Field(default=None, max_length=128)
    review_notes: str | None = None
    risk_assessment: dict[str, Any] = Field(default_factory=dict)


class WorkflowTemplateReviewActionRequest(BaseModel):
    review_notes: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class WorkflowTemplateReviewResponse(BaseModel):
    id: UUID
    workspace_id: str
    template_id: UUID
    template_version_id: UUID
    reviewer_id: str | None
    review_status: str
    review_notes: str | None
    risk_assessment: dict[str, Any]
    compatibility_report: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, review: WorkflowTemplateReview) -> "WorkflowTemplateReviewResponse":
        return cls(
            id=review.id,
            workspace_id=review.workspace_id,
            template_id=review.template_id,
            template_version_id=review.template_version_id,
            reviewer_id=review.reviewer_id,
            review_status=review.review_status,
            review_notes=review.review_notes,
            risk_assessment=review.risk_assessment or {},
            compatibility_report=review.compatibility_report or {},
            created_at=review.created_at,
            updated_at=review.updated_at,
        )


class WorkflowTemplateReviewListResponse(BaseModel):
    items: list[WorkflowTemplateReviewResponse]


class WorkflowTemplatePromotionResponse(BaseModel):
    id: UUID
    workspace_id: str
    template_id: UUID
    from_version_id: UUID | None
    to_version_id: UUID | None
    promotion_type: str
    promotion_reason: str | None
    promoted_by: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, promotion: WorkflowTemplatePromotion) -> "WorkflowTemplatePromotionResponse":
        return cls(
            id=promotion.id,
            workspace_id=promotion.workspace_id,
            template_id=promotion.template_id,
            from_version_id=promotion.from_version_id,
            to_version_id=promotion.to_version_id,
            promotion_type=promotion.promotion_type,
            promotion_reason=promotion.promotion_reason,
            promoted_by=promotion.promoted_by,
            created_at=promotion.created_at,
            updated_at=promotion.updated_at,
        )


class WorkflowTemplateAuditLogResponse(BaseModel):
    id: UUID
    workspace_id: str
    template_id: UUID | None
    template_version_id: UUID | None
    action: str
    actor_id: str | None
    previous_state: dict[str, Any]
    new_state: dict[str, Any]
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, log: WorkflowTemplateAuditLog) -> "WorkflowTemplateAuditLogResponse":
        return cls(
            id=log.id,
            workspace_id=log.workspace_id,
            template_id=log.template_id,
            template_version_id=log.template_version_id,
            action=log.action,
            actor_id=log.actor_id,
            previous_state=log.previous_state or {},
            new_state=log.new_state or {},
            metadata=log.audit_metadata or {},
            created_at=log.created_at,
            updated_at=log.updated_at,
        )


class WorkflowTemplateAuditLogListResponse(BaseModel):
    items: list[WorkflowTemplateAuditLogResponse]


class WorkflowTemplateCompatibilityMatrixResponse(BaseModel):
    id: UUID
    workspace_id: str
    template_version_id: UUID
    runtime_capability: str
    supported: bool
    notes: str | None
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, row: WorkflowTemplateCompatibilityMatrix) -> "WorkflowTemplateCompatibilityMatrixResponse":
        return cls(
            id=row.id,
            workspace_id=row.workspace_id,
            template_version_id=row.template_version_id,
            runtime_capability=row.runtime_capability,
            supported=row.supported,
            notes=row.notes,
            metadata=row.matrix_metadata or {},
            created_at=row.created_at,
            updated_at=row.updated_at,
        )


class WorkflowTemplateCompatibilityMatrixListResponse(BaseModel):
    items: list[WorkflowTemplateCompatibilityMatrixResponse]


class WorkflowTemplateMarketplaceItem(BaseModel):
    template: WorkflowTemplateResponse
    badges: list[str]
    metrics: dict[str, Any]
    governance_status: str
    latest_review_status: str | None = None


class WorkflowTemplateMarketplaceResponse(BaseModel):
    items: list[WorkflowTemplateMarketplaceItem]


class WorkflowTemplateLifecycleRequest(BaseModel):
    reason: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
