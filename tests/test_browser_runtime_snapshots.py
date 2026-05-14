"""Browser runtime snapshot storage tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.remote.services import BrowserWorkerService
from app.browser.services.browser_runtime_observability_service import BrowserRuntimeObservabilityService
from app.core.config import Settings
from app.models.browser_runtime import BrowserRuntimeSession


@pytest.mark.asyncio
async def test_browser_runtime_page_and_screenshot_snapshots(session: AsyncSession, tmp_path) -> None:  # type: ignore[no-untyped-def]
    """Page snapshots should persist HTML/text, screenshots should only reference existing images."""

    worker = await BrowserWorkerService(session).register_worker(
        workspace_id="workspace-runtime-snapshots",
        worker_name="runtime-worker",
        worker_type="playwright",
        base_url="http://worker",
        capabilities={"browser_runtime": True, "browser": "chromium"},
        metadata={},
    )
    runtime_session = BrowserRuntimeSession(
        workspace_id="workspace-runtime-snapshots",
        worker_id=worker.id,
        provider="remote",
        browser="chromium",
        session_status="active",
        runtime_metadata={"current_url": "https://example.com", "page_title": "Example Domain"},
    )
    session.add(runtime_session)
    await session.commit()
    await session.refresh(runtime_session)

    service = BrowserRuntimeObservabilityService(session, settings=Settings(BROWSER_RUNTIME_SNAPSHOT_DIR=str(tmp_path)))
    page_snapshot = await service.capture_page_snapshot(
        runtime_session=runtime_session,
        page_data={
            "current_url": "https://example.com",
            "page_title": "Example Domain",
            "content": "<html><body><h1>Example Domain</h1></body></html>",
        },
        commit=True,
    )
    screenshot_snapshot = await service.capture_screenshot_snapshot(
        runtime_session=runtime_session,
        screenshot_path="storage/browser_screenshots/workspace/session/shot.png",
        metadata={"full_page": True},
        commit=True,
    )

    assert page_snapshot.snapshot_type == "page"
    assert Path(page_snapshot.html_path or "").exists()
    assert Path(page_snapshot.text_path or "").read_text(encoding="utf-8") == "Example Domain"
    assert screenshot_snapshot.snapshot_type == "screenshot"
    assert screenshot_snapshot.screenshot_path.endswith("shot.png")
