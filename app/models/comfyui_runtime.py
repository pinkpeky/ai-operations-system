"""ComfyUI runtime operational audit models."""

from __future__ import annotations

from typing import Any

from sqlalchemy import Boolean, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, IdTimestampMixin


class ComfyUIRuntimeDiagnosticSnapshot(IdTimestampMixin, Base):
    """Workspace-scoped no-network diagnostic snapshot for ComfyUI runtime readiness."""

    __tablename__ = "comfyui_runtime_diagnostic_snapshots"

    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    user_id: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True)
    provider: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    guarded: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    network_allowed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    read_only_probe_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    base_url: Mapped[str] = mapped_column(String(512), nullable=False)
    parsed_host: Mapped[str | None] = mapped_column(String(255), index=True, nullable=True)
    scheme_allowed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    host_allowed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    allowed_hosts: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    health_path: Mapped[str] = mapped_column(String(255), nullable=False)
    health_path_allowed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    allowed_health_paths: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    read_only_probe_ready: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    readiness_status: Mapped[str] = mapped_column(String(64), default="blocked", index=True, nullable=False)
    external_request_attempted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    runtime_calls_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    blocking_reasons: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    recommended_actions: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    diagnostics: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    forbidden_actions: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    snapshot_payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    operator_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    snapshot_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict, nullable=False)
