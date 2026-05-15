"""OpenClaw adapter ORM models.

Phase 28 只记录 mock OpenClaw worker adapter 调用，不接真实 OpenClaw 或任何平台自动化。
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class OpenClawActionLog(Base):
    """OpenClaw action 结构化日志。"""

    __tablename__ = "openclaw_action_logs"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4, comment="OpenClaw action log ID")
    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Workspace ID")
    worker_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("browser_workers.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
        comment="Browser worker ID",
    )
    action_type: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="OpenClaw action type")
    target: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Action target")
    input_payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False, comment="Action input payload")
    output_payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False, comment="Action output payload")
    success: Mapped[bool] = mapped_column(Boolean, index=True, nullable=False, default=False, comment="Whether action succeeded")
    error: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Action error")
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="Action duration milliseconds")
    provider: Mapped[str] = mapped_column(String(64), index=True, nullable=False, default="mock", comment="OpenClaw provider")
    mock: Mapped[bool] = mapped_column(Boolean, index=True, nullable=False, default=True, comment="Whether this was a mock action")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
