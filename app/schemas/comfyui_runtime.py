"""ComfyUI runtime adapter contract schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


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
