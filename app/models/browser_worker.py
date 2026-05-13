"""Remote Browser Worker ORM 模型。

Phase 19 只建立 AI Server 与 Browser Worker 的基础协议、注册、心跳与动作映射。
本阶段不会部署真实外部 worker，也不会实现平台自动化、登录、代理池或指纹绕过。
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import BrowserWorkerActionStatus, BrowserWorkerAuthStatus, BrowserWorkerSessionStatus, BrowserWorkerStatus


class BrowserWorker(Base):
    """按 workspace 隔离的 remote browser worker 注册记录。"""

    __tablename__ = "browser_workers"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4, comment="Worker ID")
    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Workspace ID")
    worker_name: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Worker name")
    worker_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False, comment="Worker type")
    base_url: Mapped[str] = mapped_column(Text, nullable=False, comment="Worker API base URL")
    status: Mapped[str] = mapped_column(
        String(32),
        index=True,
        nullable=False,
        default=BrowserWorkerStatus.OFFLINE.value,
        comment="Worker status",
    )
    capabilities: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False, comment="Worker capabilities")
    last_heartbeat_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    worker_secret_hash: Mapped[str | None] = mapped_column(
        String(128),
        index=True,
        nullable=True,
        comment="Hash of the worker secret; plaintext is returned only once",
    )
    api_key_hash: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Reserved worker API key hash")
    last_auth_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    auth_status: Mapped[str] = mapped_column(
        String(32),
        index=True,
        nullable=False,
        default=BrowserWorkerAuthStatus.UNVERIFIED.value,
        comment="Worker auth status",
    )
    allowed_actions: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False, comment="Allowed action types")
    allowed_domains: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False, comment="Allowed target domains")
    max_sessions: Mapped[int] = mapped_column(Integer, default=5, nullable=False, comment="Max concurrent sessions")
    active_sessions: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="Active session count")
    max_actions_per_minute: Mapped[int] = mapped_column(Integer, default=60, nullable=False, comment="Action rate limit hint")
    current_load: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="Current scheduling load")
    priority: Mapped[int] = mapped_column(Integer, default=100, nullable=False, comment="Worker selection priority")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Last worker error message")
    worker_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
        comment="Worker metadata",
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    sessions: Mapped[list["BrowserWorkerSession"]] = relationship(back_populates="worker", cascade="save-update, merge")
    actions: Mapped[list["BrowserWorkerAction"]] = relationship(back_populates="worker", cascade="save-update, merge")


class BrowserWorkerSession(Base):
    """本地 BrowserSession 与 remote worker session 的映射。"""

    __tablename__ = "browser_worker_sessions"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4, comment="Worker session ID")
    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Workspace ID")
    worker_id: Mapped[UUID] = mapped_column(
        ForeignKey("browser_workers.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="Worker ID",
    )
    remote_session_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Remote session ID")
    local_browser_session_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("browser_sessions.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
        comment="Local browser session ID",
    )
    status: Mapped[str] = mapped_column(
        String(32),
        index=True,
        nullable=False,
        default=BrowserWorkerSessionStatus.ACTIVE.value,
        comment="Worker session status",
    )
    session_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
        comment="Worker session metadata",
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    worker: Mapped[BrowserWorker] = relationship(back_populates="sessions")
    actions: Mapped[list["BrowserWorkerAction"]] = relationship(back_populates="worker_session", cascade="save-update, merge")


class BrowserWorkerAction(Base):
    """Remote worker action 调度记录。"""

    __tablename__ = "browser_worker_actions"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4, comment="Worker action ID")
    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Workspace ID")
    worker_id: Mapped[UUID] = mapped_column(
        ForeignKey("browser_workers.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="Worker ID",
    )
    worker_session_id: Mapped[UUID] = mapped_column(
        ForeignKey("browser_worker_sessions.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="Worker session ID",
    )
    local_action_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("browser_actions.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
        comment="Local browser action ID",
    )
    remote_action_id: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True, comment="Remote action ID")
    action_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False, comment="Action type")
    status: Mapped[str] = mapped_column(
        String(32),
        index=True,
        nullable=False,
        default=BrowserWorkerActionStatus.PENDING.value,
        comment="Worker action status",
    )
    request_payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False, comment="Remote request")
    response_payload: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True, comment="Remote response")
    error: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Remote action error")
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="Action duration milliseconds")
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="Actual retry attempts")
    max_retries: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="Max retry attempts")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    worker: Mapped[BrowserWorker] = relationship(back_populates="actions")
    worker_session: Mapped[BrowserWorkerSession] = relationship(back_populates="actions")
