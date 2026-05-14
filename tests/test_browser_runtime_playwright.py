"""Playwright browser runtime provider tests."""

from __future__ import annotations

import pytest

from worker_client.browser_runtime.playwright_provider import PlaywrightBrowserRuntimeProvider
from worker_client.browser_runtime.schemas import BrowserRuntimeCreateSessionRequest, BrowserRuntimeScreenshotRequest


@pytest.mark.asyncio
async def test_playwright_browser_runtime_basic_flow(fake_playwright, tmp_path) -> None:  # type: ignore[no-untyped-def]
    provider = PlaywrightBrowserRuntimeProvider(
        headless=True,
        screenshot_dir=str(tmp_path / "screenshots"),
        profile_dir=str(tmp_path / "profiles"),
    )

    created = await provider.create_session(
        BrowserRuntimeCreateSessionRequest(workspace_id="workspace-playwright-runtime", browser="chromium")
    )
    session_id = created.remote_session_id or ""
    navigated = await provider.navigate(session_id=session_id, url="https://example.com")
    shot = await provider.screenshot(session_id=session_id, request=BrowserRuntimeScreenshotRequest(full_page=True))
    page = await provider.get_page(session_id=session_id)
    closed = await provider.close_session(session_id=session_id)

    assert created.success is True
    assert navigated.data["page_title"] == "Example Domain"
    assert shot.data["screenshot_base64"]
    assert "Example Domain" in (page.content or "")
    assert closed.success is True
