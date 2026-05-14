"""Remote Browser Runtime ORM models.

Phase 34 adds a browser runtime session table that tracks AI Server -> remote
customer-machine worker sessions independently from the older Browser Adapter
session table. It is intentionally narrow and does not model platform login,
stealth, proxy, or account automation features.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import BrowserRuntimeSessionStatus


class BrowserRuntimeSession(Base):
    """Workspace-scoped remote browser runtime session."""

    __tablename__ = "browser_runtime_sessions"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4, comment="Runtime session ID")
    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Workspace ID")
    worker_id: Mapped[UUID] = mapped_column(
        ForeignKey("browser_workers.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="Selected remote worker ID",
    )
    provider: Mapped[str] = mapped_column(String(64), index=True, nullable=False, default="remote", comment="Runtime provider")
    browser: Mapped[str] = mapped_column(String(64), index=True, nullable=False, default="chromium", comment="Browser engine")
    session_status: Mapped[str] = mapped_column(
        String(32),
        index=True,
        nullable=False,
        default=BrowserRuntimeSessionStatus.ACTIVE.value,
        comment="Runtime session status",
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    last_activity_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True, nullable=True)
    runtime_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
        comment="Remote runtime session metadata",
    )


class BrowserRuntimeEvent(Base):
    """Timeline event for one browser runtime session."""

    __tablename__ = "browser_runtime_events"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4, comment="Timeline event ID")
    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Workspace ID")
    runtime_session_id: Mapped[UUID] = mapped_column(
        ForeignKey("browser_runtime_sessions.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="Browser runtime session ID",
    )
    worker_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("browser_workers.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
        comment="Worker ID at event time",
    )
    event_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False, comment="Timeline event type")
    status: Mapped[str] = mapped_column(String(32), index=True, nullable=False, default="completed", comment="Event status")
    message: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Human-readable message")
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False, comment="Structured event payload")
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="Action duration in milliseconds")
    error: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Structured error message")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True, nullable=False)


class BrowserRuntimeSnapshot(Base):
    """Stored page/screenshot/error snapshot metadata."""

    __tablename__ = "browser_runtime_snapshots"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4, comment="Snapshot ID")
    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Workspace ID")
    runtime_session_id: Mapped[UUID] = mapped_column(
        ForeignKey("browser_runtime_sessions.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="Browser runtime session ID",
    )
    snapshot_type: Mapped[str] = mapped_column(String(32), index=True, nullable=False, comment="page/screenshot/error/final")
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    page_title: Mapped[str | None] = mapped_column(Text, nullable=True)
    html_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    text_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    screenshot_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    snapshot_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
        comment="Snapshot metadata",
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True, nullable=False)


class BrowserRuntimeReplay(Base):
    """Replay metadata export record.

    Phase 35A replay does not re-execute browser actions. It only captures a
    readable timeline and snapshot manifest for debugging.
    """

    __tablename__ = "browser_runtime_replays"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4, comment="Replay ID")
    workspace_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False, comment="Workspace ID")
    runtime_session_id: Mapped[UUID] = mapped_column(
        ForeignKey("browser_runtime_sessions.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        comment="Browser runtime session ID",
    )
    replay_status: Mapped[str] = mapped_column(String(32), index=True, nullable=False, default="created")
    replay_steps: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    source_event_ids: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    source_snapshot_ids: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    replay_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
        comment="Replay metadata",
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True, nullable=False)
