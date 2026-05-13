"""Playwright Local Provider 单元测试。"""

import pytest

from app.browser.providers.playwright_provider import PlaywrightLocalProvider


@pytest.mark.asyncio
async def test_playwright_provider_creates_session_and_navigates(fake_playwright, tmp_path) -> None:  # type: ignore[no-untyped-def]
    """PlaywrightLocalProvider 应能创建 session 并导航到 example.com。"""

    provider = PlaywrightLocalProvider(screenshot_dir=tmp_path)

    created = await provider.create_session(metadata={"workspace_id": "workspace-a", "session_id": "session-a"})
    navigated = await provider.navigate(
        target="https://example.com",
        input_payload={},
        session_metadata=created.data["provider_session_metadata"],
    )

    assert created.success is True
    assert created.data["browser_id"]
    assert created.data["page_id"]
    assert created.data["provider_session_metadata"]["browser_type"] == "chromium"
    assert navigated.success is True
    assert navigated.data["target_url"] == "https://example.com"
    assert navigated.data["page_title"] == "Example Domain"


@pytest.mark.asyncio
async def test_playwright_provider_blocks_unsafe_url(fake_playwright, tmp_path) -> None:  # type: ignore[no-untyped-def]
    """Phase 18 不允许访问社媒或任意外部站点。"""

    provider = PlaywrightLocalProvider(screenshot_dir=tmp_path)
    created = await provider.create_session(metadata={"workspace_id": "workspace-a", "session_id": "session-a"})

    result = await provider.navigate(
        target="https://tiktok.com",
        input_payload={},
        session_metadata=created.data["provider_session_metadata"],
    )

    assert result.success is False
    assert "only allows example.com" in str(result.error)
