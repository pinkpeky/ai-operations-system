"""Browser provider tests."""

import pytest

from app.browser.providers import MockBrowserProvider, PlaywrightBrowserProvider


@pytest.mark.asyncio
async def test_mock_browser_provider_returns_stable_success() -> None:
    """Mock provider should return deterministic success without real browser."""

    provider = MockBrowserProvider()

    session = await provider.create_session(metadata={"purpose": "test"})
    action = await provider.navigate(target="https://example.com", input_payload={"wait": "none"})
    screenshot = await provider.screenshot(target=None, input_payload={})

    assert session.success is True
    assert session.data["provider_session_id"].startswith("mock-")
    assert action.success is True
    assert action.message == "mock browser navigate success"
    assert screenshot.data["screenshot"] == "mock://browser/screenshot.png"


@pytest.mark.asyncio
async def test_playwright_provider_is_placeholder_only() -> None:
    """Playwright provider should fail gracefully in Phase 17."""

    provider = PlaywrightBrowserProvider()

    result = await provider.navigate(target="https://example.com", input_payload={})

    assert result.success is False
    assert "placeholder" in str(result.error)
