"""In-memory session manager for the customer-machine browser runtime."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass(slots=True)
class BrowserRuntimeSessionRecord:
    """Process-local Playwright session record."""

    session_id: str
    workspace_id: str | None
    browser: str
    playwright: Any
    browser_instance: Any | None
    context: Any
    page: Any
    metadata: dict[str, Any] = field(default_factory=dict)
    current_url: str | None = None
    page_title: str | None = None
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    last_activity_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


class BrowserRuntimeSessionManager:
    """Store runtime sessions in process memory."""

    def __init__(self) -> None:
        self.sessions: dict[str, BrowserRuntimeSessionRecord] = {}

    def add(self, record: BrowserRuntimeSessionRecord) -> None:
        self.sessions[record.session_id] = record

    def get(self, session_id: str) -> BrowserRuntimeSessionRecord | None:
        return self.sessions.get(session_id)

    def remove(self, session_id: str) -> BrowserRuntimeSessionRecord | None:
        return self.sessions.pop(session_id, None)

    def touch(self, record: BrowserRuntimeSessionRecord) -> None:
        record.last_activity_at = datetime.now(UTC).isoformat()

    def list(self) -> list[BrowserRuntimeSessionRecord]:
        return list(self.sessions.values())
