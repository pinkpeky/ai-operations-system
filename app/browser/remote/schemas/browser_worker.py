"""Remote Browser Worker API 与 mock runtime schema。"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.browser_worker import BrowserWorker, BrowserWorkerSession

WorkerStatus = Literal["online", "offline", "busy", "error"]


class BrowserWorkerRegisterRequest(BaseModel):
    """注册 browser worker 请求。"""

    worker_name: str = Field(min_length=1, max_length=128)
    worker_type: str = Field(min_length=1, max_length=64)
    base_url: str = Field(min_length=1)
    capabilities: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    max_sessions: int = Field(default=5, ge=1, le=100)
    max_actions_per_minute: int = Field(default=60, ge=1, le=10000)
    priority: int = Field(default=100, ge=0, le=1000)
    allowed_actions: list[str] | None = None
    allowed_domains: list[str] | None = None
    generate_secret: bool = True


class BrowserWorkerHeartbeatRequest(BaseModel):
    """Worker heartbeat 请求。"""

    status: WorkerStatus
    capabilities: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class BrowserWorkerResponse(BaseModel):
    """Worker API 响应。"""

    id: UUID
    workspace_id: str
    worker_name: str
    worker_type: str
    base_url: str
    status: str
    capabilities: dict[str, Any]
    last_heartbeat_at: datetime | None
    last_seen: datetime | None
    last_auth_at: datetime | None
    auth_status: str
    allowed_actions: list[str]
    allowed_domains: list[str]
    max_sessions: int
    active_sessions: int
    max_actions_per_minute: int
    current_load: int
    priority: int
    error_message: str | None
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime
    worker_secret: str | None = None

    @classmethod
    def from_model(cls, worker: BrowserWorker, *, worker_secret: str | None = None) -> "BrowserWorkerResponse":
        """从 ORM 构造响应。"""

        return cls(
            id=worker.id,
            workspace_id=worker.workspace_id,
            worker_name=worker.worker_name,
            worker_type=worker.worker_type,
            base_url=worker.base_url,
            status=worker.status,
            capabilities=worker.capabilities,
            last_heartbeat_at=worker.last_heartbeat_at,
            last_seen=worker.last_heartbeat_at,
            last_auth_at=worker.last_auth_at,
            auth_status=worker.auth_status,
            allowed_actions=worker.allowed_actions or [],
            allowed_domains=worker.allowed_domains or [],
            max_sessions=worker.max_sessions,
            active_sessions=worker.active_sessions,
            max_actions_per_minute=worker.max_actions_per_minute,
            current_load=worker.current_load,
            priority=worker.priority,
            error_message=worker.error_message,
            metadata=worker.worker_metadata,
            created_at=worker.created_at,
            updated_at=worker.updated_at,
            worker_secret=worker_secret,
        )


class BrowserWorkerRotateSecretResponse(BrowserWorkerResponse):
    """Worker secret rotation response. Plaintext secret is returned once."""

    worker_secret: str


class BrowserWorkerRevokeRequest(BaseModel):
    """Worker revoke request."""

    reason: str | None = None


class BrowserWorkerListResponse(BaseModel):
    """Worker 列表响应。"""

    items: list[BrowserWorkerResponse]


class BrowserWorkerHealthSummaryResponse(BaseModel):
    """Worker health/capacity summary."""

    workspace_id: str
    total_workers: int
    online_workers: int
    offline_workers: int
    busy_workers: int
    error_workers: int
    stale_workers: int
    active_sessions: int
    max_sessions: int
    available_workers: int
    heartbeat_timeout_seconds: int
    workers: list[BrowserWorkerResponse]


class BrowserWorkerSessionResponse(BaseModel):
    """Worker session mapping response."""

    id: UUID
    workspace_id: str
    worker_id: UUID
    remote_session_id: str
    local_browser_session_id: UUID | None
    status: str
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, session: BrowserWorkerSession) -> "BrowserWorkerSessionResponse":
        """Build API response from ORM model."""

        return cls(
            id=session.id,
            workspace_id=session.workspace_id,
            worker_id=session.worker_id,
            remote_session_id=session.remote_session_id,
            local_browser_session_id=session.local_browser_session_id,
            status=session.status,
            metadata=session.session_metadata,
            created_at=session.created_at,
            updated_at=session.updated_at,
        )


class BrowserWorkerSessionListResponse(BaseModel):
    """Worker session list response."""

    items: list[BrowserWorkerSessionResponse]


class BrowserSessionCleanupRequest(BaseModel):
    """Manual stale browser session cleanup request."""

    session_timeout_seconds: int | None = Field(default=None, ge=1, le=86400)
    close_stale_sessions: bool = True


class BrowserSessionCleanupResponse(BaseModel):
    """Manual stale browser session cleanup response."""

    workspace_id: str
    stale_sessions: int
    offline_worker_sessions: int
    closed_sessions: int
    failed_sessions: int
    log_count: int


class BrowserWorkerMarkOfflineRequest(BaseModel):
    """Manual mark-offline request."""

    error_message: str | None = None


class BrowserWorkerRuntimeSessionRequest(BaseModel):
    """Mock worker runtime 创建 session 请求。"""

    workspace_id: str | None = None
    local_browser_session_id: str | None = None
    profile_id: str | None = None
    profile_path: str | None = None
    use_persistent_profile: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class BrowserWorkerRuntimeSessionResponse(BaseModel):
    """Mock worker runtime session 响应。"""

    success: bool
    remote_session_id: str | None = None
    message: str
    data: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None


class BrowserWorkerRuntimeActionRequest(BaseModel):
    """Mock worker runtime action 请求。"""

    remote_session_id: str
    action_type: str
    target: str | None = None
    input_payload: dict[str, Any] = Field(default_factory=dict)


class BrowserWorkerActionResponse(BaseModel):
    """Mock worker runtime action 响应。"""

    success: bool
    remote_action_id: str | None = None
    message: str
    data: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None


class BrowserWorkerRuntimeHealthResponse(BaseModel):
    """Mock worker runtime health 响应。"""

    success: bool
    worker_type: str
    reachable: bool
    capabilities: dict[str, Any]
    message: str
    error: str | None = None


class BrowserWorkerHumanControlRequest(BaseModel):
    """Mock worker runtime human-control request."""

    remote_session_id: str
    control_session_id: str | None = None
    browser_session_id: str | None = None
    profile_id: str | None = None
    reason: str | None = None
    note: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class BrowserWorkerHumanControlResponse(BaseModel):
    """Mock worker runtime human-control response."""

    success: bool
    remote_session_id: str
    status: str
    message: str
    data: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None


class BrowserWorkerUIAccessCapabilitiesResponse(BaseModel):
    """Mock worker runtime UI access placeholder capabilities."""

    vnc: bool = False
    novnc: bool = False
    devtools: bool = False
    placeholder: bool = True
