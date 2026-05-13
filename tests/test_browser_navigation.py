"""Browser navigation runtime tests."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.providers.playwright_provider import PlaywrightLocalProvider
from app.browser.services import BrowserService


@pytest.mark.asyncio
async def test_browser_navigation_records_runtime_fields(fake_playwright, tmp_path, session: AsyncSession) -> None:  # type: ignore[no-untyped-def]
    """navigate action 应记录 target_url、page_title 和 provider metadata。"""

    service = BrowserService(session, provider=PlaywrightLocalProvider(screenshot_dir=tmp_path))
    browser_session = await service.create_browser_session(workspace_id="workspace-nav", user_id="user-a")
    action = await service.execute_action(
        workspace_id="workspace-nav",
        session_id=browser_session.id,
        action_type="navigate",
        target="https://example.com",
    )
    logs = await service.list_logs(workspace_id="workspace-nav", session_id=browser_session.id)

    assert browser_session.provider == "playwright_local"
    assert browser_session.browser_id
    assert browser_session.page_id
    assert browser_session.provider_session_metadata["headless"] is True
    assert action.status == "completed"
    assert action.target_url == "https://example.com"
    assert action.page_title == "Example Domain"
    assert any(log.log_metadata.get("provider") == "playwright_local" for log in logs)
