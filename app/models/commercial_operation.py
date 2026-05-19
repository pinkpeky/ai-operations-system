"""Commercial operation ORM models."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import DateTime, JSON, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, IdTimestampMixin
from app.models.enums import CommercialOperationPriority, CommercialOperationRiskLevel, CommercialOperationStatus


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
