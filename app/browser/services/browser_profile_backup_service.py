"""Browser Profile 备份与恢复服务。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import logging
from pathlib import Path
import shutil
from typing import Any
from uuid import UUID
import zipfile

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.models.browser import BrowserProfile, BrowserProfileUsageLog
from app.models.enums import BrowserProfileStatus

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class ProfileBackupResult:
    """Profile backup operation result."""

    workspace_id: str
    profile_id: str
    backup_path: str | None
    success: bool
    error: str | None = None
    retained_backups: int = 0


class BrowserProfileBackupService:
    """负责 profile zip 备份、恢复、列表和清理。"""

    def __init__(self, session: AsyncSession, *, settings: Settings | None = None) -> None:
        self.session = session
        self.settings = settings or get_settings()

    async def create_backup(self, *, workspace_id: str, profile_id: UUID) -> ProfileBackupResult:
        """将 profile 目录压缩为 zip，并按最大备份数清理旧备份。"""

        if not self.settings.browser_profile_backup_enabled:
            return ProfileBackupResult(workspace_id=workspace_id, profile_id=str(profile_id), backup_path=None, success=False, error="profile backup disabled")
        profile = await self._get_profile(workspace_id=workspace_id, profile_id=profile_id)
        if profile is None:
            raise ValueError("Browser profile not found")
        source_dir = self._resolve_under_root(profile.profile_path, self.settings.browser_profile_root)
        if not source_dir.exists() or not source_dir.is_dir():
            profile.last_error = "profile path does not exist for backup"
            await self._log_usage(workspace_id=workspace_id, profile_id=profile.id, action="backup", success=False, error=profile.last_error)
            await self.session.commit()
            return ProfileBackupResult(workspace_id=workspace_id, profile_id=str(profile_id), backup_path=None, success=False, error=profile.last_error)

        backup_dir = self._backup_dir(workspace_id=workspace_id, profile_id=profile_id)
        backup_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
        backup_path = backup_dir / f"profile-{timestamp}.zip"
        self._zip_directory(source_dir=source_dir, zip_path=backup_path)
        profile.backup_path = str(backup_path)
        profile.last_backup_at = datetime.now(UTC)
        profile.last_error = None
        retained = self.cleanup_backups_sync(workspace_id=workspace_id, profile_id=profile_id)
        await self._log_usage(
            workspace_id=workspace_id,
            profile_id=profile.id,
            action="backup",
            success=True,
            metadata={"backup_path": str(backup_path), "retained_backups": retained},
        )
        await self.session.commit()
        await self.session.refresh(profile)
        logger.info("Browser profile backup created", extra={"workspace_id": workspace_id, "profile_id": str(profile.id), "backup_path": str(backup_path)})
        return ProfileBackupResult(
            workspace_id=workspace_id,
            profile_id=str(profile_id),
            backup_path=str(backup_path),
            success=True,
            retained_backups=retained,
        )

    async def list_backups(self, *, workspace_id: str, profile_id: UUID) -> list[str]:
        """列出 profile 备份 zip。"""

        profile = await self._get_profile(workspace_id=workspace_id, profile_id=profile_id, include_deleted=True)
        if profile is None:
            raise ValueError("Browser profile not found")
        return [str(path) for path in self._backup_files(workspace_id=workspace_id, profile_id=profile_id)]

    async def restore_backup(self, *, workspace_id: str, profile_id: UUID, backup_path: str) -> ProfileBackupResult:
        """从指定 zip 恢复 profile 目录。"""

        profile = await self._get_profile(workspace_id=workspace_id, profile_id=profile_id, include_deleted=True)
        if profile is None:
            raise ValueError("Browser profile not found")
        if profile.status == BrowserProfileStatus.LOCKED.value:
            raise ValueError("Cannot restore a locked browser profile")
        backup = Path(backup_path)
        if not backup.is_absolute():
            backup = Path.cwd() / backup
        backup = backup.resolve()
        backup_root = self._backup_dir(workspace_id=workspace_id, profile_id=profile_id).resolve()
        if not str(backup).startswith(str(backup_root)) or not backup.exists() or backup.suffix != ".zip":
            raise ValueError("Invalid profile backup path")
        target_dir = self._resolve_under_root(profile.profile_path, self.settings.browser_profile_root)
        if target_dir.exists():
            shutil.rmtree(target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(backup, "r") as archive:
            archive.extractall(target_dir)
        profile.last_error = None
        await self._log_usage(
            workspace_id=workspace_id,
            profile_id=profile.id,
            action="restore",
            success=True,
            metadata={"backup_path": str(backup), "profile_path": str(target_dir)},
        )
        await self.session.commit()
        return ProfileBackupResult(workspace_id=workspace_id, profile_id=str(profile_id), backup_path=str(backup), success=True)

    def cleanup_backups_sync(self, *, workspace_id: str, profile_id: UUID) -> int:
        """同步清理超出保留数量的旧备份，返回剩余数量。"""

        backups = self._backup_files(workspace_id=workspace_id, profile_id=profile_id)
        max_backups = self.settings.browser_profile_max_backups
        for old_backup in backups[max_backups:]:
            old_backup.unlink(missing_ok=True)
        return len(self._backup_files(workspace_id=workspace_id, profile_id=profile_id))

    async def cleanup_backups(self, *, workspace_id: str, profile_id: UUID) -> int:
        """异步入口：清理旧备份并写 usage log。"""

        profile = await self._get_profile(workspace_id=workspace_id, profile_id=profile_id, include_deleted=True)
        if profile is None:
            raise ValueError("Browser profile not found")
        retained = self.cleanup_backups_sync(workspace_id=workspace_id, profile_id=profile_id)
        await self._log_usage(
            workspace_id=workspace_id,
            profile_id=profile.id,
            action="backup_cleanup",
            success=True,
            metadata={"retained_backups": retained},
        )
        await self.session.commit()
        return retained

    async def _get_profile(self, *, workspace_id: str, profile_id: UUID, include_deleted: bool = False) -> BrowserProfile | None:
        statement = select(BrowserProfile).where(BrowserProfile.workspace_id == workspace_id, BrowserProfile.id == profile_id)
        if not include_deleted:
            statement = statement.where(BrowserProfile.status != BrowserProfileStatus.DELETED.value)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def _log_usage(
        self,
        *,
        workspace_id: str,
        profile_id: UUID,
        action: str,
        success: bool,
        error: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.session.add(
            BrowserProfileUsageLog(
                workspace_id=workspace_id,
                profile_id=profile_id,
                action=action,
                success=success,
                error=error,
                log_metadata=metadata or {},
            )
        )
        await self.session.flush()

    def _backup_dir(self, *, workspace_id: str, profile_id: UUID) -> Path:
        safe_workspace_id = self._safe_name(workspace_id)
        return (Path.cwd() / self.settings.browser_profile_backup_root / safe_workspace_id / str(profile_id)).resolve()

    def _backup_files(self, *, workspace_id: str, profile_id: UUID) -> list[Path]:
        backup_dir = self._backup_dir(workspace_id=workspace_id, profile_id=profile_id)
        if not backup_dir.exists():
            return []
        return sorted(backup_dir.glob("*.zip"), key=lambda path: path.stat().st_mtime, reverse=True)

    def _resolve_under_root(self, value: str, root_value: str) -> Path:
        path = Path(value)
        if not path.is_absolute():
            path = Path.cwd() / path
        root = Path(root_value)
        if not root.is_absolute():
            root = Path.cwd() / root
        resolved_path = path.resolve()
        resolved_root = root.resolve()
        if not str(resolved_path).startswith(str(resolved_root)):
            raise ValueError("Profile path is outside profile root")
        return resolved_path

    def _zip_directory(self, *, source_dir: Path, zip_path: Path) -> None:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
            for file_path in source_dir.rglob("*"):
                if file_path.is_file():
                    archive.write(file_path, file_path.relative_to(source_dir))

    def _safe_name(self, value: str) -> str:
        return "".join(char if char.isalnum() or char in {"-", "_", "."} else "-" for char in value).strip("-") or "item"
