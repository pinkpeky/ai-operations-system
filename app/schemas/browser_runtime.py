"""Phase 34 Browser Runtime API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.browser_runtime import BrowserRuntimeSession


class BrowserRuntimeSessionCreateRequest(BaseModel):
    """Create a remote browser runtime session."""

    browser: str = Field(default="chromium", min_length=1, max_length=64)
    worker_id: UUID | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class BrowserRuntimeNavigateRequest(BaseModel):
    """Navigate request."""

    url: str = Field(min_length=1)


class BrowserRuntimeScreenshotRequest(BaseModel):
    """Screenshot request."""

    full_page: bool = True
    screenshot_name: str | None = Field(default=None, max_length=128)


class BrowserRuntimeSessionResponse(BaseModel):
    """Remote browser runtime session response."""

    id: UUID
    workspace_id: str
    worker_id: UUID
    provider: str
    browser: str
    session_status: str
    created_at: datetime
    updated_at: datetime
    last_activity_at: datetime | None
    metadata: dict[str, Any]
    current_url: str | None = None
    page_title: str | None = None
    screenshot_path: str | None = None

    @classmethod
    def from_model(cls, runtime_session: BrowserRuntimeSession) -> "BrowserRuntimeSessionResponse":
        """Build response from ORM model."""

        metadata = runtime_session.runtime_metadata or {}
        return cls(
            id=runtime_session.id,
            workspace_id=runtime_session.workspace_id,
            worker_id=runtime_session.worker_id,
            provider=runtime_session.provider,
            browser=runtime_session.browser,
            session_status=runtime_session.session_status,
            created_at=runtime_session.created_at,
            updated_at=runtime_session.updated_at,
            last_activity_at=runtime_session.last_activity_at,
            metadata=metadata,
            current_url=metadata.get("current_url"),
            page_title=metadata.get("page_title"),
            screenshot_path=metadata.get("last_screenshot_path"),
        )


class BrowserRuntimeSessionListResponse(BaseModel):
    """List response."""

    items: list[BrowserRuntimeSessionResponse]


class BrowserRuntimePageResponse(BaseModel):
    """Current page response."""

    session: BrowserRuntimeSessionResponse
    title: str | None = None
    url: str | None = None
    content: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
