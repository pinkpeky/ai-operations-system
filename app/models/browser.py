"""Browser Adapter ORM 模型。

Phase 17 只记录 mock browser session/action/log。表结构为未来
Playwright/OpenClaw provider 预留，但当前阶段不会启动真实浏览器。
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import (
    BrowserActionStatus,
    BrowserHumanControlStatus,
    BrowserProfileHealthStatus,
    BrowserProfileStatus,
    BrowserSessionStatus,
    BrowserUIAccessStatus,
)


class BrowserProfile(Base):
    """按 workspace 隔离的持久化 Browser Profile 记录。"""

    __tablename__ = "browser_profiles"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4, comment="Browser profile ID")
    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Workspace ID")
    user_id: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="User ID")
    profile_name: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Profile name")
    profile_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False, default="persistent", comment="Profile type")
    provider: Mapped[str] = mapped_column(String(64), index=True, nullable=False, default="remote", comment="Browser provider")
    profile_path: Mapped[str] = mapped_column(Text, nullable=False, comment="Worker-side profile path")
    status: Mapped[str] = mapped_column(
        String(32),
        index=True,
        nullable=False,
        default=BrowserProfileStatus.AVAILABLE.value,
        comment="Profile status",
    )
    locked_by_session_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("browser_sessions.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
        comment="Browser session that currently locks this profile",
    )
    locked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    health_status: Mapped[str] = mapped_column(
        String(32),
        index=True,
        nullable=False,
        default=BrowserProfileHealthStatus.HEALTHY.value,
        comment="Profile health status",
    )
    last_health_check_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Last profile health/runtime error")
    usage_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment="Profile usage count")
    corrupted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    backup_path: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Latest profile backup path")
    last_backup_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    profile_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
        comment="Profile metadata",
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    sessions: Mapped[list["BrowserSession"]] = relationship(
        back_populates="profile",
        foreign_keys="BrowserSession.profile_id",
        cascade="save-update, merge",
    )
    usage_logs: Mapped[list["BrowserProfileUsageLog"]] = relationship(back_populates="profile", cascade="save-update, merge")


class BrowserProfileUsageLog(Base):
    """Profile 使用、恢复、备份和清理的结构化日志。"""

    __tablename__ = "browser_profile_usage_logs"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4, comment="Profile usage log ID")
    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Workspace ID")
    profile_id: Mapped[UUID] = mapped_column(
        ForeignKey("browser_profiles.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="Browser profile ID",
    )
    session_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("browser_sessions.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
        comment="Browser session ID",
    )
    action: Mapped[str] = mapped_column(String(64), index=True, nullable=False, comment="Profile lifecycle action")
    success: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, comment="Whether action succeeded")
    error: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Action error")
    log_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
        comment="Usage log metadata",
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    profile: Mapped[BrowserProfile] = relationship(back_populates="usage_logs")


class BrowserSession(Base):
    """按 workspace 隔离的 browser session 记录。"""

    __tablename__ = "browser_sessions"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4, comment="Browser session ID")
    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Workspace ID")
    user_id: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="User ID")
    provider: Mapped[str] = mapped_column(String(64), index=True, nullable=False, default="mock", comment="Browser provider")
    browser_id: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Provider browser ID")
    page_id: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Provider page ID")
    profile_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("browser_profiles.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
        comment="Persistent browser profile ID",
    )
    profile_path: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Worker-side persistent profile path")
    persistent_context_enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether this session uses a persistent context",
    )
    human_control_status: Mapped[str | None] = mapped_column(
        String(32),
        index=True,
        nullable=True,
        comment="Current human-in-the-loop control status",
    )
    human_control_session_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("browser_human_control_sessions.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
        comment="Current human control session ID",
    )
    paused_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    provider_session_metadata: Mapped[dict[str, Any]] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
        comment="Provider session metadata",
    )
    status: Mapped[str] = mapped_column(
        String(32),
        index=True,
        nullable=False,
        default=BrowserSessionStatus.ACTIVE.value,
        comment="Browser session status",
    )
    session_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
        comment="Session metadata",
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    actions: Mapped[list["BrowserAction"]] = relationship(back_populates="session", cascade="save-update, merge")
    logs: Mapped[list["BrowserActionLog"]] = relationship(back_populates="session", cascade="save-update, merge")
    profile: Mapped[BrowserProfile | None] = relationship(
        back_populates="sessions",
        foreign_keys=[profile_id],
    )


class BrowserHumanControlSession(Base):
    """人工接管浏览器控制的会话记录。"""

    __tablename__ = "browser_human_control_sessions"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4, comment="Human control session ID")
    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Workspace ID")
    browser_session_id: Mapped[UUID] = mapped_column(
        ForeignKey("browser_sessions.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="Browser session ID",
    )
    profile_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("browser_profiles.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
        comment="Browser profile ID",
    )
    worker_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("browser_workers.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
        comment="Remote browser worker ID",
    )
    status: Mapped[str] = mapped_column(
        String(32),
        index=True,
        nullable=False,
        default=BrowserHumanControlStatus.REQUESTED.value,
        comment="Human control status",
    )
    reason: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Reason for requesting human control")
    requested_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True)
    approved_by: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True, nullable=True)
    control_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
        comment="Human control metadata",
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class BrowserHumanControlEvent(Base):
    """人工接管状态流转和说明事件。"""

    __tablename__ = "browser_human_control_events"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4, comment="Human control event ID")
    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Workspace ID")
    control_session_id: Mapped[UUID] = mapped_column(
        ForeignKey("browser_human_control_sessions.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="Human control session ID",
    )
    event_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False, comment="Human control event type")
    message: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Event message")
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False, comment="Event payload")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class BrowserUIAccessSession(Base):
    """浏览器 UI 接管占位访问会话。

    当前仅保存 placeholder URL 与一次性 token hash，不提供真实 VNC/noVNC/DevTools UI。
    """

    __tablename__ = "browser_ui_access_sessions"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4, comment="UI access session ID")
    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Workspace ID")
    browser_session_id: Mapped[UUID] = mapped_column(
        ForeignKey("browser_sessions.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="Browser session ID",
    )
    human_control_session_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("browser_human_control_sessions.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
        comment="Human control session ID",
    )
    worker_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("browser_workers.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
        comment="Remote browser worker ID",
    )
    access_token_hash: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="SHA-256 access token hash")
    remote_control_url: Mapped[str] = mapped_column(Text, nullable=False, comment="Placeholder remote control URL")
    live_view_url: Mapped[str] = mapped_column(Text, nullable=False, comment="Placeholder live view URL")
    devtools_url: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Placeholder DevTools URL")
    scopes: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False, comment="Allowed UI access scopes")
    one_time: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, comment="Whether token is single-use")
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, comment="First successful use time")
    revoked_reason: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Reason for token revocation")
    client_ip: Mapped[str | None] = mapped_column(String(128), nullable=True, comment="Client IP that requested the token")
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Client user agent that requested the token")
    status: Mapped[str] = mapped_column(
        String(32),
        index=True,
        nullable=False,
        default=BrowserUIAccessStatus.REQUESTED.value,
        comment="UI access status",
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    access_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
        comment="UI access metadata",
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class BrowserSecurityAuditLog(Base):
    """Browser security audit log for worker auth, UI access and policy checks."""

    __tablename__ = "browser_security_audit_logs"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4, comment="Audit log ID")
    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Workspace ID")
    actor_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False, comment="Actor type")
    actor_id: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Actor ID")
    event_type: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Security event type")
    target_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False, comment="Target type")
    target_id: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Target ID")
    success: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, comment="Whether event succeeded")
    error: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Security error")
    ip_address: Mapped[str | None] = mapped_column(String(128), nullable=True, comment="Client or worker IP")
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Client or worker user agent")
    audit_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
        comment="Structured audit metadata",
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class BrowserAction(Base):
    """session 内执行的一次 browser action。"""

    __tablename__ = "browser_actions"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4, comment="Browser action ID")
    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Workspace ID")
    session_id: Mapped[UUID] = mapped_column(
        ForeignKey("browser_sessions.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="Browser session ID",
    )
    action_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False, comment="Action type")
    target: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Action target")
    selector: Mapped[str | None] = mapped_column(Text, nullable=True, comment="DOM selector")
    target_url: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Navigation target URL")
    screenshot_path: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Screenshot file path")
    page_title: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Page title after action")
    input_payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False, comment="Action input")
    output_payload: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True, comment="Action output")
    status: Mapped[str] = mapped_column(
        String(32),
        index=True,
        nullable=False,
        default=BrowserActionStatus.PENDING.value,
        comment="Action status",
    )
    error: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Action error")
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="Action duration in milliseconds")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    session: Mapped[BrowserSession] = relationship(back_populates="actions")
    logs: Mapped[list["BrowserActionLog"]] = relationship(back_populates="action", cascade="save-update, merge")


class BrowserActionLog(Base):
    """browser session/action 产生的结构化日志。"""

    __tablename__ = "browser_action_logs"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4, comment="Browser log ID")
    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Workspace ID")
    session_id: Mapped[UUID] = mapped_column(
        ForeignKey("browser_sessions.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="Browser session ID",
    )
    action_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("browser_actions.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
        comment="Browser action ID",
    )
    level: Mapped[str] = mapped_column(String(32), index=True, nullable=False, comment="Log level")
    message: Mapped[str] = mapped_column(Text, nullable=False, comment="Log message")
    log_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
        comment="Log metadata",
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    session: Mapped[BrowserSession] = relationship(back_populates="logs")
    action: Mapped[BrowserAction | None] = relationship(back_populates="logs")
