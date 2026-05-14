"""Browser runtime observability API tests."""

from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api.routes import browser_runtime as browser_runtime_routes
from app.core.errors import AppError, app_error_handler
from app.db.postgres import get_session


class FakeBrowserRuntimeObservabilityService:
    def __init__(self, *_: object, **__: object) -> None:
        self.session_id = uuid4()
        self.replay_id = uuid4()

    async def list_events(self, **_: object) -> list[SimpleNamespace]:
        return [
            SimpleNamespace(
                id=uuid4(),
                workspace_id="workspace-runtime-api",
                runtime_session_id=self.session_id,
                worker_id=uuid4(),
                event_type="navigate_completed",
                status="completed",
                message="ok",
                payload={"url": "https://example.com"},
                duration_ms=12,
                error=None,
                created_at=datetime.now(UTC),
            )
        ]

    async def list_snapshots(self, **_: object) -> list[SimpleNamespace]:
        return [
            SimpleNamespace(
                id=uuid4(),
                workspace_id="workspace-runtime-api",
                runtime_session_id=self.session_id,
                snapshot_type="page",
                url="https://example.com",
                page_title="Example Domain",
                html_path="storage/browser_runtime_snapshots/page.html",
                text_path="storage/browser_runtime_snapshots/page.txt",
                screenshot_path=None,
                snapshot_metadata={"source": "test"},
                created_at=datetime.now(UTC),
            )
        ]

    async def create_replay(self, **_: object) -> SimpleNamespace:
        return self._replay()

    async def get_replay(self, **_: object) -> SimpleNamespace:
        return self._replay()

    async def export_replay_json(self, **_: object) -> tuple[SimpleNamespace, str, dict]:
        replay = self._replay()
        return replay, "storage/browser_runtime_snapshots/replay.json", {"replay_id": str(replay.id)}

    def _replay(self) -> SimpleNamespace:
        return SimpleNamespace(
            id=self.replay_id,
            workspace_id="workspace-runtime-api",
            runtime_session_id=self.session_id,
            replay_status="created",
            replay_steps=[{"event_type": "navigate_completed"}],
            source_event_ids=["event-1"],
            source_snapshot_ids=["snapshot-1"],
            replay_metadata={"note": "metadata-only replay"},
            created_at=datetime.now(UTC),
        )


@pytest.mark.asyncio
async def test_browser_runtime_observability_api(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Observability endpoints should expose events, snapshots, and replay metadata."""

    app = FastAPI()
    app.add_exception_handler(AppError, app_error_handler)
    app.include_router(browser_runtime_routes.router, prefix="/api/v1")
    monkeypatch.setattr(browser_runtime_routes, "BrowserRuntimeObservabilityService", FakeBrowserRuntimeObservabilityService)

    async def override_get_session():  # type: ignore[no-untyped-def]
        yield object()

    app.dependency_overrides[get_session] = override_get_session
    session_id = uuid4()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        headers = {"X-Workspace-Id": "workspace-runtime-api", "X-User-Id": "user-runtime"}
        events = await client.get(f"/api/v1/browser-runtime/sessions/{session_id}/events", headers=headers)
        snapshots = await client.get(f"/api/v1/browser-runtime/sessions/{session_id}/snapshots", headers=headers)
        replay = await client.post(
            f"/api/v1/browser-runtime/sessions/{session_id}/replay",
            headers=headers,
            json={"metadata": {"reason": "debug"}},
        )
        replay_id = replay.json()["id"]
        exported = await client.get(f"/api/v1/browser-runtime/replays/{replay_id}/export", headers=headers)

    assert events.status_code == 200
    assert events.json()["items"][0]["event_type"] == "navigate_completed"
    assert snapshots.json()["items"][0]["snapshot_type"] == "page"
    assert replay.status_code == 201
    assert exported.json()["export_path"].endswith("replay.json")
