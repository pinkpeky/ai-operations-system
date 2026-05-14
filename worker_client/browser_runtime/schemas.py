"""Schemas for the customer-machine remote Browser Runtime API."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class BrowserRuntimeCreateSessionRequest(BaseModel):
    """Create a Playwright browser runtime session."""

    workspace_id: str | None = None
    browser: Literal["chromium"] = "chromium"
    profile_id: str | None = None
    profile_path: str | None = None
    use_persistent_context: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class BrowserRuntimeNavigateRequest(BaseModel):
    """Navigate the remote page to a URL."""

    url: str = Field(min_length=1)


class BrowserRuntimeScreenshotRequest(BaseModel):
    """Capture a screenshot."""

    full_page: bool = True
    screenshot_name: str | None = None


class BrowserRuntimeSessionResponse(BaseModel):
    """Session create/close response."""

    success: bool
    remote_session_id: str | None = None
    session_id: str | None = None
    message: str
    data: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None


class BrowserRuntimeActionResponse(BaseModel):
    """Action response."""

    success: bool
    remote_action_id: str | None = None
    message: str
    data: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None


class BrowserRuntimePageResponse(BaseModel):
    """Current page response."""

    success: bool
    message: str
    title: str | None = None
    url: str | None = None
    content: str | None = None
    data: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
