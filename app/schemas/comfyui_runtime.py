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
    available_actions: list[str] = Field(default_factory=list)
    disabled_actions: list[str] = Field(default_factory=list)
    guardrails: list[str] = Field(default_factory=list)
    required_configuration: list[str] = Field(default_factory=list)
    workspace_id: str | None = None
    raw: dict[str, Any] = Field(default_factory=dict)
