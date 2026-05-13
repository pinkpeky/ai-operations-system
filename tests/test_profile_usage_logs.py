"""Browser profile usage log tests."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.services import BrowserProfileHealthService, BrowserProfileService, BrowserService
from app.core.config import Settings


async def test_profile_usage_logs_capture_session_lifecycle(session: AsyncSession, tmp_path) -> None:  # type: ignore[no-untyped-def]
    """profile-backed session 应记录 lock/session_start/session_close/release。"""

    settings = Settings(BROWSER_PROVIDER="mock", BROWSER_PROFILE_ROOT=str(tmp_path / "profiles"))
    profile = await BrowserProfileService(session, settings=settings).create_profile(
        workspace_id="workspace-usage",
        user_id="user-usage",
        profile_name="usage-profile",
    )
    browser_service = BrowserService(session, settings=settings)
    browser_session = await browser_service.create_browser_session(
        workspace_id="workspace-usage",
        user_id="user-usage",
        profile_id=profile.id,
        use_persistent_profile=True,
    )
    await browser_service.close_browser_session(workspace_id="workspace-usage", session_id=browser_session.id)

    logs = await BrowserProfileHealthService(session, settings=settings).list_usage_logs(
        workspace_id="workspace-usage",
        profile_id=profile.id,
    )
    actions = {log.action for log in logs}

    assert {"lock", "session_start", "session_close", "release"}.issubset(actions)
    refreshed = await BrowserProfileService(session, settings=settings).get_profile(
        workspace_id="workspace-usage",
        profile_id=profile.id,
    )
    assert refreshed is not None
    assert refreshed.usage_count == 1
