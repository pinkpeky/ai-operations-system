"""Browser page content tests."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.providers.playwright_provider import PlaywrightLocalProvider
from app.browser.services import BrowserService


@pytest.mark.asyncio
async def test_browser_get_page_content_returns_html(fake_playwright, tmp_path, session: AsyncSession) -> None:  # type: ignore[no-untyped-def]
    """get_page_content action 应返回当前页面 HTML。"""

    service = BrowserService(session, provider=PlaywrightLocalProvider(screenshot_dir=tmp_path))
    browser_session = await service.create_browser_session(workspace_id="workspace-content", user_id=None)
    await service.execute_action(
        workspace_id="workspace-content",
        session_id=browser_session.id,
        action_type="navigate",
        target="https://example.com",
    )
    action = await service.execute_action(
        workspace_id="workspace-content",
        session_id=browser_session.id,
        action_type="get_page_content",
    )

    assert action.status == "completed"
    assert action.output_payload is not None
    assert "Example Domain" in action.output_payload["data"]["content"]
    assert action.page_title == "Example Domain"
