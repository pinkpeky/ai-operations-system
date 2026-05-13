"""Browser profile backup tests."""

from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.services import BrowserProfileBackupService, BrowserProfileService
from app.core.config import Settings


async def test_profile_backup_creates_zip_and_records_metadata(session: AsyncSession, tmp_path: Path) -> None:
    """backup 应写入 zip，并更新 profile backup metadata。"""

    settings = Settings(
        BROWSER_PROFILE_ROOT=str(tmp_path / "profiles"),
        BROWSER_PROFILE_BACKUP_ROOT=str(tmp_path / "profile_backups"),
        BROWSER_PROFILE_MAX_BACKUPS=3,
    )
    profile = await BrowserProfileService(session, settings=settings).create_profile(
        workspace_id="workspace-backup",
        user_id="user-backup",
        profile_name="backup-profile",
    )
    profile_path = Path(profile.profile_path)
    profile_path.mkdir(parents=True, exist_ok=True)
    (profile_path / "state.txt").write_text("persistent state", encoding="utf-8")

    result = await BrowserProfileBackupService(session, settings=settings).create_backup(
        workspace_id="workspace-backup",
        profile_id=profile.id,
    )
    backups = await BrowserProfileBackupService(session, settings=settings).list_backups(
        workspace_id="workspace-backup",
        profile_id=profile.id,
    )

    assert result.success is True
    assert result.backup_path is not None
    assert Path(result.backup_path).exists()
    assert len(backups) == 1
