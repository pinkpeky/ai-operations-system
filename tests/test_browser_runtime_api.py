"""Browser Runtime API tests."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api.routes import browser_runtime as browser_runtime_routes
from app.core.errors import AppError, app_error_handler
from app.db.postgres import get_session
from app.models.browser_runtime import BrowserRuntimeSession


class FakeBrowserRuntimeSessionService:
    def __init__(self, *_: object, **__: object) -> None:
        self.session = BrowserRuntimeSession(
            id=uuid4(),
            workspace_id="workspace-runtime-api",
            worker_id=uuid4(),
            provider="remote",
            browser="chromium",
            session_status="active",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            last_activity_at=datetime.now(UTC),
            runtime_metadata={"remote_session_id": "remote-api", "current_url": None},
        )

    async def create_session(self, **_: object) -> BrowserRuntimeSession:
        return self.session

    async def list_sessions(self, **_: object) -> list[BrowserRuntimeSession]:
        return [self.session]

    async def get_session(self, **_: object) -> BrowserRuntimeSession:
        return self.session

    async def navigate(self, **_: object) -> BrowserRuntimeSession:
        self.session.runtime_metadata = {**self.session.runtime_metadata, "current_url": "https://example.com"}
        return self.session

    async def screenshot(self, **_: object) -> BrowserRuntimeSession:
        self.session.runtime_metadata = {**self.session.runtime_metadata, "last_screenshot_path": "storage/browser_screenshots/example.png"}
        return self.session

    async def get_page(self, **_: object) -> dict:
        return {"page_title": "Example Domain", "current_url": "https://example.com", "content": "<h1>Example Domain</h1>"}

    async def close_session(self, **_: object) -> BrowserRuntimeSession:
        self.session.session_status = "closed"
        return self.session


@pytest.mark.asyncio
async def test_browser_runtime_api_flow(monkeypatch) -> None:
    app = FastAPI()
    app.add_exception_handler(AppError, app_error_handler)
    app.include_router(browser_runtime_routes.router, prefix="/api/v1")
    monkeypatch.setattr(browser_runtime_routes, "BrowserRuntimeSessionService", FakeBrowserRuntimeSessionService)

    async def override_get_session():  # type: ignore[no-untyped-def]
        yield object()

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        headers = {"X-Workspace-Id": "workspace-runtime-api", "X-User-Id": "user-runtime"}
        created = await client.post("/api/v1/browser-runtime/sessions", headers=headers, json={"browser": "chromium"})
        session_id = created.json()["id"]
        listed = await client.get("/api/v1/browser-runtime/sessions", headers=headers)
        navigated = await client.post(
            f"/api/v1/browser-runtime/sessions/{session_id}/navigate",
            headers=headers,
            json={"url": "https://example.com"},
        )
        screenshot = await client.post(
            f"/api/v1/browser-runtime/sessions/{session_id}/screenshot",
            headers=headers,
            json={"full_page": True},
        )
        page = await client.get(f"/api/v1/browser-runtime/sessions/{session_id}/page", headers=headers)
        closed = await client.post(f"/api/v1/browser-runtime/sessions/{session_id}/close", headers=headers)

    assert created.status_code == 201
    assert len(listed.json()["items"]) == 1
    assert navigated.json()["current_url"] == "https://example.com"
    assert screenshot.json()["screenshot_path"].endswith("example.png")
    assert "Example Domain" in page.json()["content"]
    assert closed.json()["session_status"] == "closed"
