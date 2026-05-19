"""Commercial operation API schemas."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from app.models.commercial_operation import CommercialOperation


CommercialOperationStatusLiteral = Literal["draft", "planning", "ready", "active", "paused", "completed", "archived"]
CommercialOperationPriorityLiteral = Literal["low", "normal", "high"]
CommercialOperationRiskLiteral = Literal["low", "medium", "high"]


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
