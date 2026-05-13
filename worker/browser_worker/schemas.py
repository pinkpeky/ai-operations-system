"""Browser Worker API schema。"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class WorkerHealthResponse(BaseModel):
    """Worker health response."""

    success: bool
    worker_type: str
    reachable: bool
    capabilities: dict[str, Any]
    message: str
    error: str | None = None


class WorkerSessionRequest(BaseModel):
    """Create session request."""

    workspace_id: str | None = None
    local_browser_session_id: str | None = None
    profile_id: str | None = None
    profile_path: str | None = None
    use_persistent_profile: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class WorkerSessionResponse(BaseModel):
    """Create/close session response."""

    success: bool
    remote_session_id: str | None = None
    message: str
    data: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None


class WorkerActionRequest(BaseModel):
    """Execute browser action request."""

    remote_session_id: str
    action_type: str
    target: str | None = None
    input_payload: dict[str, Any] = Field(default_factory=dict)


class WorkerActionResponse(BaseModel):
    """Execute browser action response."""

    success: bool
    remote_action_id: str | None = None
    message: str
    data: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None


class WorkerHumanControlRequest(BaseModel):
    """Metadata-level human control request."""

    remote_session_id: str
    control_session_id: str | None = None
    browser_session_id: str | None = None
    profile_id: str | None = None
    reason: str | None = None
    note: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class WorkerHumanControlResponse(BaseModel):
    """Metadata-level human control response."""

    success: bool
    remote_session_id: str
    status: str
    message: str
    data: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None


class WorkerUIAccessCapabilitiesResponse(BaseModel):
    """UI access placeholder capabilities response."""

    vnc: bool = False
    novnc: bool = False
    devtools: bool = False
    placeholder: bool = True
