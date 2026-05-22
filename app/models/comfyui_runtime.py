"""ComfyUI runtime operational audit models."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import Boolean, JSON, String, Text, Uuid
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


class ComfyUIRuntimeConfigChangeRequest(IdTimestampMixin, Base):
    """Workspace-scoped, metadata-only ComfyUI runtime configuration change request."""

    __tablename__ = "comfyui_runtime_config_change_requests"

    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    user_id: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True)
    change_status: Mapped[str] = mapped_column(String(64), default="draft", index=True, nullable=False)
    provider: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    readiness_status: Mapped[str] = mapped_column(String(64), default="blocked", index=True, nullable=False)
    read_only_probe_ready: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    external_request_attempted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    runtime_calls_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    config_mutation_performed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    current_configuration: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    requested_changes: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    runbook_steps: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    recovery_actions: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    disabled_actions: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    runbook_payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    change_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    operator_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewer_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    request_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict, nullable=False)


class ComfyUIRuntimeManualApplyEvidence(IdTimestampMixin, Base):
    """Workspace-scoped evidence for a human-applied ComfyUI runtime configuration change."""

    __tablename__ = "comfyui_runtime_manual_apply_evidence"

    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    user_id: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True)
    config_change_request_id: Mapped[UUID] = mapped_column(Uuid(), index=True, nullable=False)
    before_snapshot_id: Mapped[UUID | None] = mapped_column(Uuid(), index=True, nullable=True)
    after_snapshot_id: Mapped[UUID | None] = mapped_column(Uuid(), index=True, nullable=True)
    evidence_status: Mapped[str] = mapped_column(String(64), default="draft", index=True, nullable=False)
    provider: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    readiness_status_before: Mapped[str] = mapped_column(String(64), default="blocked", index=True, nullable=False)
    readiness_status_after: Mapped[str] = mapped_column(String(64), default="blocked", index=True, nullable=False)
    read_only_probe_ready_before: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    read_only_probe_ready_after: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    external_request_attempted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    runtime_calls_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    api_config_mutation_performed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    manual_config_applied: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    service_restart_reported: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    config_change_request_payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    current_configuration_before: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    current_configuration_after: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    requested_changes: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    manual_apply_steps: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    restart_evidence: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    verification_results: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    diagnostics_payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    rollback_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    verification_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    operator_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewer_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict, nullable=False)
