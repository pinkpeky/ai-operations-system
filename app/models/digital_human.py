"""Digital human production ORM models."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import Boolean, Float, ForeignKey, Integer, JSON, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, IdTimestampMixin


class DigitalHumanAsset(IdTimestampMixin, Base):
    """Workspace-scoped person/material asset for digital human production."""

    __tablename__ = "digital_human_assets"

    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    user_id: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True)
    asset_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    asset_status: Mapped[str] = mapped_column(String(64), default="available", index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_uri: Mapped[str] = mapped_column(String(1024), nullable=False)
    file_name: Mapped[str | None] = mapped_column(String(512), nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    checksum: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True)
    consent_status: Mapped[str] = mapped_column(String(64), default="unverified", index=True, nullable=False)
    usage_scope: Mapped[str | None] = mapped_column(String(255), nullable=True)
    operator_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    asset_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict, nullable=False)


class DigitalHumanVideoJob(IdTimestampMixin, Base):
    """Workspace-scoped digital human video job plan and provider handoff state."""

    __tablename__ = "digital_human_video_jobs"

    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    user_id: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True)
    job_status: Mapped[str] = mapped_column(String(64), default="draft", index=True, nullable=False)
    provider: Mapped[str] = mapped_column(String(64), default="mock", index=True, nullable=False)
    execution_mode: Mapped[str] = mapped_column(String(64), default="plan_only", index=True, nullable=False)
    avatar_asset_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("digital_human_assets.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    material_asset_ids: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    reference_asset_ids: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    objective: Mapped[str] = mapped_column(Text, nullable=False)
    script: Mapped[str] = mapped_column(Text, nullable=False)
    target_channels: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    voice_profile: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    aspect_ratio: Mapped[str] = mapped_column(String(32), default="9:16", nullable=False)
    duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    scene_plan: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    provider_request: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    provider_response: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    outputs: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    approval_status: Mapped[str] = mapped_column(String(64), default="pending", index=True, nullable=False)
    consent_required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    consent_status: Mapped[str] = mapped_column(String(64), default="unverified", index=True, nullable=False)
    external_request_attempted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    provider_calls_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    result_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    operator_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    job_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict, nullable=False)
