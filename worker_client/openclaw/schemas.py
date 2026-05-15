"""Worker Client OpenClaw mock runtime schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class OpenClawActionRequest(BaseModel):
    """OpenClaw action 请求。

    当前阶段只定义协议，不调用真实 OpenClaw，也不执行任何平台自动化。
    """

    action_type: str = Field(min_length=1, max_length=128)
    target: str | None = None
    input_payload: dict[str, Any] = Field(default_factory=dict)
    profile_id: str | None = None
    browser_session_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class OpenClawActionResponse(BaseModel):
    """OpenClaw action 响应。"""

    success: bool
    action_type: str
    output_payload: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    duration_ms: int
    provider: str = "mock"
    mock: bool = True


class OpenClawHealthResponse(BaseModel):
    """OpenClaw runtime health 响应。"""

    success: bool
    provider: str
    reachable: bool
    enabled: bool
    mock: bool
    version: str | None = None
    error: str | None = None


class OpenClawCapabilitiesResponse(BaseModel):
    """OpenClaw runtime capabilities 响应。"""

    success: bool
    provider: str
    mock: bool
    capabilities: dict[str, Any] = Field(default_factory=dict)
    actions: list[str] = Field(default_factory=list)
    error: str | None = None
