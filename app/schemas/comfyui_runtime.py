"""ComfyUI runtime adapter contract schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.comfyui_runtime import ComfyUIRuntimeDiagnosticSnapshot


class ComfyUIRuntimeHealthResponse(BaseModel):
    """Disabled-by-default ComfyUI runtime contract health response."""

    success: bool = True
    provider: str
    enabled: bool
    reachable: bool = False
    guarded: bool = True
    mock: bool = True
    network_allowed: bool = False
    external_request_attempted: bool = False
    runtime_calls_enabled: bool = False
    read_only_probe_enabled: bool = False
    read_only_probe_attempted: bool = False
    health_path: str | None = None
    allowed_health_paths: list[str] = Field(default_factory=list)
    probe_status_code: int | None = None
    probe_latency_ms: float | None = None
    base_url: str
    allowed_hosts: list[str] = Field(default_factory=list)
    timeout_seconds: float
    workspace_id: str | None = None
    error: str | None = None
    raw: dict[str, Any] = Field(default_factory=dict)


class ComfyUIRuntimeCapabilitiesResponse(BaseModel):
    """ComfyUI runtime adapter contract capabilities response."""

    success: bool = True
    provider: str
    enabled: bool
    guarded: bool = True
    mock: bool = True
    base_url: str
    allowed_hosts: list[str] = Field(default_factory=list)
    health_path: str | None = None
    allowed_health_paths: list[str] = Field(default_factory=list)
    read_only_probe_enabled: bool = False
    available_actions: list[str] = Field(default_factory=list)
    disabled_actions: list[str] = Field(default_factory=list)
    guardrails: list[str] = Field(default_factory=list)
    required_configuration: list[str] = Field(default_factory=list)
    workspace_id: str | None = None
    raw: dict[str, Any] = Field(default_factory=dict)


class ComfyUIRuntimeDiagnosticCheck(BaseModel):
    """One no-network readiness check for the guarded ComfyUI runtime."""

    key: str
    status: str
    label: str
    detail: str
    current_value: Any = None
    expected_value: Any = None
    remediation: str | None = None


class ComfyUIRuntimeDiagnosticsResponse(BaseModel):
    """No-network ComfyUI runtime readiness diagnostics for operators."""

    success: bool = True
    provider: str
    enabled: bool
    guarded: bool = True
    network_allowed: bool = False
    read_only_probe_enabled: bool = False
    base_url: str
    parsed_host: str | None = None
    scheme_allowed: bool = False
    host_allowed: bool = False
    allowed_hosts: list[str] = Field(default_factory=list)
    health_path: str
    health_path_allowed: bool = False
    allowed_health_paths: list[str] = Field(default_factory=list)
    read_only_probe_ready: bool = False
    external_request_attempted: bool = False
    runtime_calls_enabled: bool = False
    readiness_status: str
    blocking_reasons: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    diagnostics: list[ComfyUIRuntimeDiagnosticCheck] = Field(default_factory=list)
    forbidden_actions: list[str] = Field(default_factory=list)
    workspace_id: str | None = None
    raw: dict[str, Any] = Field(default_factory=dict)


class ComfyUIRuntimeDiagnosticSnapshotCreateRequest(BaseModel):
    """Create a persisted no-network ComfyUI runtime diagnostic snapshot."""

    operator_note: str | None = Field(default=None, max_length=2000)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ComfyUIRuntimeDiagnosticSnapshotResponse(BaseModel):
    """Persisted ComfyUI runtime diagnostic snapshot response."""

    success: bool = True
    id: UUID
    workspace_id: str
    user_id: str | None = None
    provider: str
    enabled: bool
    guarded: bool
    network_allowed: bool
    read_only_probe_enabled: bool
    base_url: str
    parsed_host: str | None = None
    scheme_allowed: bool
    host_allowed: bool
    allowed_hosts: list[str] = Field(default_factory=list)
    health_path: str
    health_path_allowed: bool
    allowed_health_paths: list[str] = Field(default_factory=list)
    read_only_probe_ready: bool
    readiness_status: str
    external_request_attempted: bool
    runtime_calls_enabled: bool
    blocking_reasons: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    diagnostics: list[dict[str, Any]] = Field(default_factory=list)
    forbidden_actions: list[str] = Field(default_factory=list)
    snapshot_payload: dict[str, Any] = Field(default_factory=dict)
    operator_note: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(
        cls,
        snapshot: ComfyUIRuntimeDiagnosticSnapshot,
    ) -> "ComfyUIRuntimeDiagnosticSnapshotResponse":
        return cls(
            id=snapshot.id,
            workspace_id=snapshot.workspace_id,
            user_id=snapshot.user_id,
            provider=snapshot.provider,
            enabled=snapshot.enabled,
            guarded=snapshot.guarded,
            network_allowed=snapshot.network_allowed,
            read_only_probe_enabled=snapshot.read_only_probe_enabled,
            base_url=snapshot.base_url,
            parsed_host=snapshot.parsed_host,
            scheme_allowed=snapshot.scheme_allowed,
            host_allowed=snapshot.host_allowed,
            allowed_hosts=snapshot.allowed_hosts or [],
            health_path=snapshot.health_path,
            health_path_allowed=snapshot.health_path_allowed,
            allowed_health_paths=snapshot.allowed_health_paths or [],
            read_only_probe_ready=snapshot.read_only_probe_ready,
            readiness_status=snapshot.readiness_status,
            external_request_attempted=snapshot.external_request_attempted,
            runtime_calls_enabled=snapshot.runtime_calls_enabled,
            blocking_reasons=snapshot.blocking_reasons or [],
            recommended_actions=snapshot.recommended_actions or [],
            diagnostics=snapshot.diagnostics or [],
            forbidden_actions=snapshot.forbidden_actions or [],
            snapshot_payload=snapshot.snapshot_payload or {},
            operator_note=snapshot.operator_note,
            metadata=snapshot.snapshot_metadata or {},
            created_at=snapshot.created_at,
            updated_at=snapshot.updated_at,
        )


class ComfyUIRuntimeDiagnosticSnapshotListResponse(BaseModel):
    """List response for persisted ComfyUI runtime diagnostic snapshots."""

    success: bool = True
    workspace_id: str
    items: list[ComfyUIRuntimeDiagnosticSnapshotResponse] = Field(default_factory=list)
