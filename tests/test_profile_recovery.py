"""Browser profile stale lock recovery tests."""

from datetime import UTC, datetime, timedelta
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.services import BrowserProfileHealthService, BrowserProfileService, BrowserService
from app.core.config import Settings


async def test_recover_stale_lock_releases_profile(session: AsyncSession, tmp_path: Path) -> None:
    """超时 lock 应恢复为 available 并记录 recovery usage log。"""

    settings = Settings(BROWSER_PROVIDER="mock", BROWSER_PROFILE_ROOT=str(tmp_path / "profiles"), BROWSER_PROFILE_LOCK_TIMEOUT_SECONDS=1)
    profile_service = BrowserProfileService(session, settings=settings)
    profile = await profile_service.create_profile(
        workspace_id="workspace-recovery",
        user_id="user-recovery",
        profile_name="recover-profile",
    )
    browser_session = await BrowserService(session, settings=settings).create_browser_session(
        workspace_id="workspace-recovery",
        user_id="user-recovery",
        profile_id=profile.id,
        use_persistent_profile=True,
    )
    locked = await profile_service.get_profile(workspace_id="workspace-recovery", profile_id=profile.id)
    assert locked is not None
    locked.locked_at = datetime.now(UTC) - timedelta(seconds=10)
    await session.commit()

    result = await BrowserProfileHealthService(session, settings=settings).recover_stale_locks(workspace_id="workspace-recovery")
    recovered = await profile_service.get_profile(workspace_id="workspace-recovery", profile_id=profile.id)
    logs = await BrowserProfileHealthService(session, settings=settings).list_usage_logs(
        workspace_id="workspace-recovery",
        profile_id=profile.id,
    )

    assert browser_session.profile_id == profile.id
    assert result.recovered_count == 1
    assert recovered is not None
    assert recovered.status == "available"
    assert recovered.locked_by_session_id is None
    assert any(log.action == "recovery" for log in logs)
