"""Browser runtime observability schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.browser_runtime import BrowserRuntimeEvent, BrowserRuntimeReplay, BrowserRuntimeSnapshot


class BrowserRuntimeEventResponse(BaseModel):
    """Timeline event response."""

    id: UUID
    workspace_id: str
    runtime_session_id: UUID
    worker_id: UUID | None
    event_type: str
    status: str
    message: str | None
    payload: dict[str, Any]
    duration_ms: int | None
    error: str | None
    created_at: datetime

    @classmethod
    def from_model(cls, event: BrowserRuntimeEvent) -> "BrowserRuntimeEventResponse":
        return cls(
            id=event.id,
            workspace_id=event.workspace_id,
            runtime_session_id=event.runtime_session_id,
            worker_id=event.worker_id,
            event_type=event.event_type,
            status=event.status,
            message=event.message,
            payload=event.payload or {},
            duration_ms=event.duration_ms,
            error=event.error,
            created_at=event.created_at,
        )


class BrowserRuntimeEventListResponse(BaseModel):
    """Timeline list response."""

    items: list[BrowserRuntimeEventResponse]


class BrowserRuntimeSnapshotResponse(BaseModel):
    """Snapshot response."""

    id: UUID
    workspace_id: str
    runtime_session_id: UUID
    snapshot_type: str
    url: str | None
    page_title: str | None
    html_path: str | None
    text_path: str | None
    screenshot_path: str | None
    metadata: dict[str, Any]
    created_at: datetime

    @classmethod
    def from_model(cls, snapshot: BrowserRuntimeSnapshot) -> "BrowserRuntimeSnapshotResponse":
        return cls(
            id=snapshot.id,
            workspace_id=snapshot.workspace_id,
            runtime_session_id=snapshot.runtime_session_id,
            snapshot_type=snapshot.snapshot_type,
            url=snapshot.url,
            page_title=snapshot.page_title,
            html_path=snapshot.html_path,
            text_path=snapshot.text_path,
            screenshot_path=snapshot.screenshot_path,
            metadata=snapshot.snapshot_metadata or {},
            created_at=snapshot.created_at,
        )


class BrowserRuntimeSnapshotListResponse(BaseModel):
    """Snapshot list response."""

    items: list[BrowserRuntimeSnapshotResponse]


class BrowserRuntimeReplayCreateRequest(BaseModel):
    """Create replay metadata request."""

    metadata: dict[str, Any] = Field(default_factory=dict)


class BrowserRuntimeReplayResponse(BaseModel):
    """Replay metadata response."""

    id: UUID
    workspace_id: str
    runtime_session_id: UUID
    replay_status: str
    replay_steps: list[dict[str, Any]]
    source_event_ids: list[str]
    source_snapshot_ids: list[str]
    metadata: dict[str, Any]
    created_at: datetime

    @classmethod
    def from_model(cls, replay: BrowserRuntimeReplay) -> "BrowserRuntimeReplayResponse":
        return cls(
            id=replay.id,
            workspace_id=replay.workspace_id,
            runtime_session_id=replay.runtime_session_id,
            replay_status=replay.replay_status,
            replay_steps=replay.replay_steps or [],
            source_event_ids=replay.source_event_ids or [],
            source_snapshot_ids=replay.source_snapshot_ids or [],
            metadata=replay.replay_metadata or {},
            created_at=replay.created_at,
        )


class BrowserRuntimeReplayExportResponse(BaseModel):
    """Replay export response."""

    replay: BrowserRuntimeReplayResponse
    export_path: str
    export: dict[str, Any]
