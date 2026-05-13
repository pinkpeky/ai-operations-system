"""OpenClaw API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.openclaw import OpenClawActionLog


class OpenClawActionRequest(BaseModel):
    """OpenClaw action 请求。

    当前只走 mock worker runtime，不调用真实 OpenClaw。
    """

    action_type: str = Field(min_length=1, max_length=128)
    target: str | None = None
    input_payload: dict[str, Any] = Field(default_factory=dict)
    profile_id: str | None = None
    browser_session_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    worker_id: UUID | None = None


class OpenClawActionResponse(BaseModel):
    """OpenClaw action 响应。"""

    success: bool
    action_type: str
    output_payload: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    duration_ms: int | None = None
    provider: str
    mock: bool
    worker_id: UUID | None = None
    log_id: UUID | None = None


class OpenClawHealthResponse(BaseModel):
    """OpenClaw health 响应。"""

    success: bool = True
    provider: str
    enabled: bool
    reachable: bool
    worker_id: UUID | None = None
    worker_name: str | None = None
    mock: bool = True
    version: str | None = None
    error: str | None = None
    raw: dict[str, Any] = Field(default_factory=dict)


class OpenClawCapabilitiesResponse(BaseModel):
    """OpenClaw capabilities 响应。"""

    success: bool = True
    provider: str
    enabled: bool
    worker_id: UUID | None = None
    worker_name: str | None = None
    mock: bool = True
    capabilities: dict[str, Any] = Field(default_factory=dict)
    actions: list[str] = Field(default_factory=list)
    error: str | None = None
    raw: dict[str, Any] = Field(default_factory=dict)


class OpenClawActionLogResponse(BaseModel):
    """OpenClaw action log 响应。"""

    id: UUID
    workspace_id: str
    worker_id: UUID | None
    action_type: str
    target: str | None
    input_payload: dict[str, Any]
    output_payload: dict[str, Any]
    success: bool
    error: str | None
    duration_ms: int | None
    provider: str
    mock: bool
    created_at: datetime

    @classmethod
    def from_model(cls, log: OpenClawActionLog) -> "OpenClawActionLogResponse":
        """从 ORM 构造响应。"""

        return cls(
            id=log.id,
            workspace_id=log.workspace_id,
            worker_id=log.worker_id,
            action_type=log.action_type,
            target=log.target,
            input_payload=log.input_payload,
            output_payload=log.output_payload,
            success=log.success,
            error=log.error,
            duration_ms=log.duration_ms,
            provider=log.provider,
            mock=log.mock,
            created_at=log.created_at,
        )
