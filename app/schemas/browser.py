"""Browser Adapter API 数据模型。"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.browser import (
    BrowserAction,
    BrowserActionLog,
    BrowserHumanControlEvent,
    BrowserHumanControlSession,
    BrowserProfile,
    BrowserProfileUsageLog,
    BrowserSecurityAuditLog,
    BrowserSession,
    BrowserUIAccessSession,
)


class BrowserSessionCreateRequest(BaseModel):
    """创建 browser session 请求。"""

    metadata: dict[str, Any] = Field(default_factory=dict)
    profile_id: UUID | None = None
    use_persistent_profile: bool = False


class BrowserSessionResponse(BaseModel):
    """Browser session 响应。"""

    id: UUID
    workspace_id: str
    user_id: str | None
    provider: str
    browser_id: str | None = None
    page_id: str | None = None
    profile_id: UUID | None = None
    profile_path: str | None = None
    persistent_context_enabled: bool = False
    human_control_status: str | None = None
    human_control_session_id: UUID | None = None
    paused_at: datetime | None = None
    resumed_at: datetime | None = None
    provider_session_metadata: dict[str, Any] = Field(default_factory=dict)
    status: str
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, session: BrowserSession) -> "BrowserSessionResponse":
        """从 ORM 构造响应。"""

        return cls(
            id=session.id,
            workspace_id=session.workspace_id,
            user_id=session.user_id,
            provider=session.provider,
            browser_id=session.browser_id,
            page_id=session.page_id,
            profile_id=session.profile_id,
            profile_path=session.profile_path,
            persistent_context_enabled=session.persistent_context_enabled,
            human_control_status=session.human_control_status,
            human_control_session_id=session.human_control_session_id,
            paused_at=session.paused_at,
            resumed_at=session.resumed_at,
            provider_session_metadata=session.provider_session_metadata,
            status=session.status,
            metadata=session.session_metadata,
            created_at=session.created_at,
            updated_at=session.updated_at,
        )


class BrowserSessionListResponse(BaseModel):
    """Browser session 列表响应。"""

    items: list[BrowserSessionResponse]


class BrowserProfileCreateRequest(BaseModel):
    """创建持久化 browser profile 请求。"""

    profile_name: str = Field(min_length=1, max_length=128)
    profile_type: str = Field(default="persistent", min_length=1, max_length=64)
    provider: str = Field(default="remote", min_length=1, max_length=64)
    metadata: dict[str, Any] = Field(default_factory=dict)


class BrowserProfileLockRequest(BaseModel):
    """手动锁定 profile 请求。"""

    session_id: UUID


class BrowserProfileReleaseRequest(BaseModel):
    """手动释放 profile 请求。"""

    session_id: UUID | None = None


class BrowserProfileResponse(BaseModel):
    """Browser profile 响应。"""

    id: UUID
    workspace_id: str
    user_id: str | None
    profile_name: str
    profile_type: str
    provider: str
    profile_path: str
    status: str
    locked_by_session_id: UUID | None
    locked_at: datetime | None
    last_used_at: datetime | None
    health_status: str
    last_health_check_at: datetime | None
    last_error: str | None
    usage_count: int
    corrupted_at: datetime | None
    backup_path: str | None
    last_backup_at: datetime | None
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, profile: BrowserProfile) -> "BrowserProfileResponse":
        """从 ORM 构造 profile 响应。"""

        return cls(
            id=profile.id,
            workspace_id=profile.workspace_id,
            user_id=profile.user_id,
            profile_name=profile.profile_name,
            profile_type=profile.profile_type,
            provider=profile.provider,
            profile_path=profile.profile_path,
            status=profile.status,
            locked_by_session_id=profile.locked_by_session_id,
            locked_at=profile.locked_at,
            last_used_at=profile.last_used_at,
            health_status=profile.health_status,
            last_health_check_at=profile.last_health_check_at,
            last_error=profile.last_error,
            usage_count=profile.usage_count,
            corrupted_at=profile.corrupted_at,
            backup_path=profile.backup_path,
            last_backup_at=profile.last_backup_at,
            metadata=profile.profile_metadata,
            created_at=profile.created_at,
            updated_at=profile.updated_at,
        )


class BrowserProfileListResponse(BaseModel):
    """Browser profile 列表响应。"""

    items: list[BrowserProfileResponse]


class BrowserProfileHealthCheckResponse(BaseModel):
    """Profile health check response."""

    profile: BrowserProfileResponse
    healthy: bool
    health_status: str
    error: str | None = None


class BrowserProfileHealthSummaryResponse(BaseModel):
    """Profile health summary response."""

    workspace_id: str
    total_profiles: int
    healthy_count: int
    warning_count: int
    corrupted_count: int
    stale_count: int
    deleted_count: int


class BrowserProfileRecoverLocksResponse(BaseModel):
    """Stale lock recovery response."""

    workspace_id: str
    recovered_count: int
    checked_count: int
    recovered_profile_ids: list[str]


class BrowserProfileBackupResponse(BaseModel):
    """Profile backup/restore response."""

    workspace_id: str
    profile_id: str
    backup_path: str | None
    success: bool
    error: str | None = None
    retained_backups: int = 0


class BrowserProfileBackupListResponse(BaseModel):
    """Profile backup list response."""

    items: list[str]


class BrowserProfileRestoreRequest(BaseModel):
    """Profile restore request."""

    backup_path: str


class BrowserProfileCleanupRequest(BaseModel):
    """Profile cleanup request."""

    include_deleted: bool = True
    include_corrupted: bool = True
    include_unused: bool = True
    dry_run: bool = True


class BrowserProfileCleanupResponse(BaseModel):
    """Profile cleanup response."""

    workspace_id: str
    dry_run: bool
    deleted_profiles: int
    corrupted_profiles: int
    unused_profiles: int
    matched_profiles: int
    removed_paths: int
    bytes_freed: int


class BrowserProfileUsageLogResponse(BaseModel):
    """Profile usage log response."""

    id: UUID
    workspace_id: str
    profile_id: UUID
    session_id: UUID | None
    action: str
    success: bool
    error: str | None
    metadata: dict[str, Any]
    created_at: datetime

    @classmethod
    def from_model(cls, log: BrowserProfileUsageLog) -> "BrowserProfileUsageLogResponse":
        return cls(
            id=log.id,
            workspace_id=log.workspace_id,
            profile_id=log.profile_id,
            session_id=log.session_id,
            action=log.action,
            success=log.success,
            error=log.error,
            metadata=log.log_metadata,
            created_at=log.created_at,
        )


class BrowserProfileUsageLogListResponse(BaseModel):
    """Profile usage log list response."""

    items: list[BrowserProfileUsageLogResponse]


class BrowserHumanControlRequest(BaseModel):
    """请求人工接管浏览器控制。"""

    browser_session_id: UUID
    reason: str | None = Field(default=None, max_length=2048)
    metadata: dict[str, Any] = Field(default_factory=dict)


class BrowserHumanControlApproveRequest(BaseModel):
    """批准人工接管请求。"""

    metadata: dict[str, Any] = Field(default_factory=dict)


class BrowserHumanControlStartRequest(BaseModel):
    """启动人工接管窗口。"""

    metadata: dict[str, Any] = Field(default_factory=dict)


class BrowserHumanControlCompleteRequest(BaseModel):
    """完成人工接管请求。"""

    note: str | None = Field(default=None, max_length=4096)
    metadata: dict[str, Any] = Field(default_factory=dict)


class BrowserHumanControlCancelRequest(BaseModel):
    """取消人工接管请求。"""

    reason: str | None = Field(default=None, max_length=2048)


class BrowserHumanControlSessionResponse(BaseModel):
    """人工接管 session 响应。"""

    id: UUID
    workspace_id: str
    browser_session_id: UUID
    profile_id: UUID | None
    worker_id: UUID | None
    status: str
    reason: str | None
    requested_by: str | None
    approved_by: str | None
    started_at: datetime | None
    completed_at: datetime | None
    expires_at: datetime | None
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, control_session: BrowserHumanControlSession) -> "BrowserHumanControlSessionResponse":
        """从 ORM 构造人工接管 session 响应。"""

        return cls(
            id=control_session.id,
            workspace_id=control_session.workspace_id,
            browser_session_id=control_session.browser_session_id,
            profile_id=control_session.profile_id,
            worker_id=control_session.worker_id,
            status=control_session.status,
            reason=control_session.reason,
            requested_by=control_session.requested_by,
            approved_by=control_session.approved_by,
            started_at=control_session.started_at,
            completed_at=control_session.completed_at,
            expires_at=control_session.expires_at,
            metadata=control_session.control_metadata,
            created_at=control_session.created_at,
            updated_at=control_session.updated_at,
        )


class BrowserHumanControlSessionListResponse(BaseModel):
    """人工接管 session 列表响应。"""

    items: list[BrowserHumanControlSessionResponse]


class BrowserHumanControlEventResponse(BaseModel):
    """人工接管事件响应。"""

    id: UUID
    workspace_id: str
    control_session_id: UUID
    event_type: str
    message: str | None
    payload: dict[str, Any]
    created_at: datetime

    @classmethod
    def from_model(cls, event: BrowserHumanControlEvent) -> "BrowserHumanControlEventResponse":
        """从 ORM 构造人工接管事件响应。"""

        return cls(
            id=event.id,
            workspace_id=event.workspace_id,
            control_session_id=event.control_session_id,
            event_type=event.event_type,
            message=event.message,
            payload=event.payload,
            created_at=event.created_at,
        )


class BrowserHumanControlEventListResponse(BaseModel):
    """人工接管事件列表响应。"""

    items: list[BrowserHumanControlEventResponse]


class BrowserUIAccessCreateRequest(BaseModel):
    """创建 UI Access Placeholder 请求。"""

    browser_session_id: UUID
    human_control_session_id: UUID | None = None
    scopes: list[Literal["view", "control", "screenshot", "devtools_placeholder"]] = Field(default_factory=lambda: ["view"])
    one_time: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class BrowserUIAccessRevokeRequest(BaseModel):
    """Revoke UI access request."""

    reason: str | None = None


class BrowserUIAccessResponse(BaseModel):
    """UI Access Placeholder 响应，token 只在创建接口返回一次。"""

    id: UUID
    workspace_id: str
    browser_session_id: UUID
    human_control_session_id: UUID | None
    worker_id: UUID | None
    remote_control_url: str
    live_view_url: str
    devtools_url: str | None
    scopes: list[str]
    one_time: bool
    used_at: datetime | None
    revoked_reason: str | None
    client_ip: str | None
    user_agent: str | None
    status: str
    expires_at: datetime
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime
    access_token: str | None = None

    @classmethod
    def from_model(cls, access_session: BrowserUIAccessSession, *, access_token: str | None = None) -> "BrowserUIAccessResponse":
        """从 ORM 构造 UI access 响应，不暴露 token hash。"""

        return cls(
            id=access_session.id,
            workspace_id=access_session.workspace_id,
            browser_session_id=access_session.browser_session_id,
            human_control_session_id=access_session.human_control_session_id,
            worker_id=access_session.worker_id,
            remote_control_url=access_session.remote_control_url,
            live_view_url=access_session.live_view_url,
            devtools_url=access_session.devtools_url,
            scopes=access_session.scopes or [],
            one_time=access_session.one_time,
            used_at=access_session.used_at,
            revoked_reason=access_session.revoked_reason,
            client_ip=access_session.client_ip,
            user_agent=access_session.user_agent,
            status=access_session.status,
            expires_at=access_session.expires_at,
            metadata=access_session.access_metadata,
            created_at=access_session.created_at,
            updated_at=access_session.updated_at,
            access_token=access_token,
        )


class BrowserUIAccessExpireResponse(BaseModel):
    """UI access 批量过期响应。"""

    expired_count: int
    items: list[BrowserUIAccessResponse]


class BrowserUIAccessValidateResponse(BaseModel):
    """UI access token 校验响应。"""

    access_session_id: UUID
    valid: bool
    status: str | None
    reason: str | None = None
    scope: str | None = None
    placeholder: bool = True


class BrowserSecurityPolicyCheckRequest(BaseModel):
    """Browser action policy check request."""

    action_type: str
    target: str | None = None
    session_id: UUID | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class BrowserSecurityPolicyCheckResponse(BaseModel):
    """Browser action policy check response."""

    allowed: bool
    reason: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class BrowserSecurityAuditLogResponse(BaseModel):
    """Browser security audit log response."""

    id: UUID
    workspace_id: str
    actor_type: str
    actor_id: str | None
    event_type: str
    target_type: str
    target_id: str | None
    success: bool
    error: str | None
    ip_address: str | None
    user_agent: str | None
    metadata: dict[str, Any]
    created_at: datetime

    @classmethod
    def from_model(cls, log: BrowserSecurityAuditLog) -> "BrowserSecurityAuditLogResponse":
        return cls(
            id=log.id,
            workspace_id=log.workspace_id,
            actor_type=log.actor_type,
            actor_id=log.actor_id,
            event_type=log.event_type,
            target_type=log.target_type,
            target_id=log.target_id,
            success=log.success,
            error=log.error,
            ip_address=log.ip_address,
            user_agent=log.user_agent,
            metadata=log.audit_metadata,
            created_at=log.created_at,
        )


class BrowserSecurityAuditLogListResponse(BaseModel):
    """Browser security audit log list response."""

    items: list[BrowserSecurityAuditLogResponse]


class BrowserActionRequest(BaseModel):
    """执行 browser action 请求。"""

    session_id: UUID
    action_type: Literal["navigate", "click", "type_text", "scroll", "screenshot", "get_page_content"]
    target: str | None = Field(default=None)
    selector: str | None = Field(default=None)
    text: str | None = Field(default=None)
    screenshot_name: str | None = Field(default=None)
    input_payload: dict[str, Any] = Field(default_factory=dict)


class BrowserActionResponse(BaseModel):
    """Browser action 响应。"""

    id: UUID
    workspace_id: str
    session_id: UUID
    action_type: str
    target: str | None
    selector: str | None
    target_url: str | None
    screenshot_path: str | None
    page_title: str | None
    input_payload: dict[str, Any]
    output_payload: dict[str, Any] | None
    status: str
    error: str | None
    duration_ms: int | None
    created_at: datetime

    @classmethod
    def from_model(cls, action: BrowserAction) -> "BrowserActionResponse":
        """从 ORM 构造响应。"""

        return cls(
            id=action.id,
            workspace_id=action.workspace_id,
            session_id=action.session_id,
            action_type=action.action_type,
            target=action.target,
            selector=action.selector,
            target_url=action.target_url,
            screenshot_path=action.screenshot_path,
            page_title=action.page_title,
            input_payload=action.input_payload,
            output_payload=action.output_payload,
            status=action.status,
            error=action.error,
            duration_ms=action.duration_ms,
            created_at=action.created_at,
        )


class BrowserActionListResponse(BaseModel):
    """Browser action 列表响应。"""

    session_id: UUID
    items: list[BrowserActionResponse]


class BrowserActionLogResponse(BaseModel):
    """Browser action log 响应。"""

    id: UUID
    workspace_id: str
    session_id: UUID
    action_id: UUID | None
    level: str
    message: str
    metadata: dict[str, Any]
    created_at: datetime

    @classmethod
    def from_model(cls, log: BrowserActionLog) -> "BrowserActionLogResponse":
        """从 ORM 构造响应。"""

        return cls(
            id=log.id,
            workspace_id=log.workspace_id,
            session_id=log.session_id,
            action_id=log.action_id,
            level=log.level,
            message=log.message,
            metadata=log.log_metadata,
            created_at=log.created_at,
        )


class BrowserActionLogListResponse(BaseModel):
    """Browser action log 列表响应。"""

    session_id: UUID
    items: list[BrowserActionLogResponse]


class ScreenshotCleanupRequest(BaseModel):
    """Manual screenshot cleanup request."""

    workspace_id: str | None = Field(default=None, description="Optional workspace override; defaults to current header workspace")
    older_than_days: int | None = Field(default=None, ge=1, le=3650)
    dry_run: bool = Field(default=True, description="Preview cleanup without deleting files")


class ScreenshotCleanupResponse(BaseModel):
    """Screenshot cleanup response."""

    workspace_id: str
    root_dir: str
    older_than_days: int
    dry_run: bool
    matched_files: int
    deleted_files: int
    bytes_freed: int
