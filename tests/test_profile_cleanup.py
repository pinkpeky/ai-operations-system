"""Browser profile cleanup tests."""

from datetime import UTC, datetime, timedelta
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.services import BrowserProfileCleanupService, BrowserProfileService
from app.core.config import Settings


async def test_profile_cleanup_removes_deleted_profile_path(session: AsyncSession, tmp_path: Path) -> None:
    """非 dry-run cleanup 应删除 deleted profile 目录。"""

    settings = Settings(BROWSER_PROFILE_ROOT=str(tmp_path / "profiles"))
    service = BrowserProfileService(session, settings=settings)
    profile = await service.create_profile(
        workspace_id="workspace-clean-profile",
        user_id="user-clean",
        profile_name="clean-profile",
    )
    profile_path = Path(profile.profile_path)
    profile_path.mkdir(parents=True, exist_ok=True)
    (profile_path / "state.txt").write_text("state", encoding="utf-8")
    await service.delete_profile(workspace_id="workspace-clean-profile", profile_id=profile.id)

    result = await BrowserProfileCleanupService(session, settings=settings).cleanup_profiles(
        workspace_id="workspace-clean-profile",
        dry_run=False,
    )

    assert result.deleted_profiles == 1
    assert result.removed_paths == 1
    assert not profile_path.exists()


async def test_profile_cleanup_matches_unused_profiles(session: AsyncSession, tmp_path: Path) -> None:
    """超过 unused days 的 available profile 应可被 cleanup 匹配。"""

    settings = Settings(BROWSER_PROFILE_ROOT=str(tmp_path / "profiles"), BROWSER_PROFILE_UNUSED_DAYS=1)
    profile = await BrowserProfileService(session, settings=settings).create_profile(
        workspace_id="workspace-unused-profile",
        user_id="user-clean",
        profile_name="unused-profile",
    )
    Path(profile.profile_path).mkdir(parents=True, exist_ok=True)
    profile.last_used_at = datetime.now(UTC) - timedelta(days=3)
    await session.commit()

    result = await BrowserProfileCleanupService(session, settings=settings).cleanup_profiles(
        workspace_id="workspace-unused-profile",
        include_deleted=False,
        include_corrupted=False,
        include_unused=True,
        dry_run=True,
    )

    assert result.unused_profiles == 1
    assert result.matched_profiles == 1
