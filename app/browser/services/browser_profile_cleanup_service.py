"""Browser Profile 清理服务。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
import logging
from pathlib import Path
import shutil
from typing import Any
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.models.browser import BrowserProfile, BrowserProfileUsageLog
from app.models.enums import BrowserProfileHealthStatus, BrowserProfileStatus

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class ProfileCleanupResult:
    """Profile cleanup result."""

    workspace_id: str
    dry_run: bool
    deleted_profiles: int
    corrupted_profiles: int
    unused_profiles: int
    matched_profiles: int
    removed_paths: int
    bytes_freed: int


class BrowserProfileCleanupService:
    """清理 deleted/corrupted/unused profiles 的持久化目录。"""

    def __init__(self, session: AsyncSession, *, settings: Settings | None = None) -> None:
        self.session = session
        self.settings = settings or get_settings()

    async def cleanup_deleted_profiles(self, *, workspace_id: str, dry_run: bool = True) -> ProfileCleanupResult:
        return await self.cleanup_profiles(workspace_id=workspace_id, include_deleted=True, include_corrupted=False, include_unused=False, dry_run=dry_run)

    async def cleanup_corrupted_profiles(self, *, workspace_id: str, dry_run: bool = True) -> ProfileCleanupResult:
        return await self.cleanup_profiles(workspace_id=workspace_id, include_deleted=False, include_corrupted=True, include_unused=False, dry_run=dry_run)

    async def cleanup_unused_profiles(self, *, workspace_id: str, dry_run: bool = True) -> ProfileCleanupResult:
        return await self.cleanup_profiles(workspace_id=workspace_id, include_deleted=False, include_corrupted=False, include_unused=True, dry_run=dry_run)

    async def cleanup_profiles(
        self,
        *,
        workspace_id: str,
        include_deleted: bool = True,
        include_corrupted: bool = True,
        include_unused: bool = True,
        dry_run: bool = True,
    ) -> ProfileCleanupResult:
        """按策略清理 profile 目录，默认 dry-run。"""

        candidates = await self._candidate_profiles(
            workspace_id=workspace_id,
            include_deleted=include_deleted,
            include_corrupted=include_corrupted,
            include_unused=include_unused,
        )
        deleted_count = 0
        corrupted_count = 0
        unused_count = 0
        removed_paths = 0
        bytes_freed = 0
        now = datetime.now(UTC)

        for profile in candidates:
            if profile.status == BrowserProfileStatus.LOCKED.value:
                continue
            if profile.status == BrowserProfileStatus.DELETED.value:
                deleted_count += 1
            elif profile.status == BrowserProfileStatus.CORRUPTED.value:
                corrupted_count += 1
            else:
                unused_count += 1
            profile_path = self._resolve_under_root(profile.profile_path)
            size = self._dir_size(profile_path)
            if profile_path.exists():
                if not dry_run:
                    shutil.rmtree(profile_path)
                    removed_paths += 1
                    bytes_freed += size
                elif size > 0:
                    bytes_freed += size
            profile.profile_metadata = {
                **(profile.profile_metadata or {}),
                "last_cleanup_at": now.isoformat(),
                "last_cleanup_dry_run": dry_run,
            }
            await self._log_usage(
                workspace_id=workspace_id,
                profile_id=profile.id,
                action="cleanup",
                success=True,
                metadata={"dry_run": dry_run, "profile_path": str(profile_path), "bytes": size},
            )
        await self.session.commit()
        logger.info(
            "Browser profile cleanup completed",
            extra={"workspace_id": workspace_id, "matched_profiles": len(candidates), "dry_run": dry_run},
        )
        return ProfileCleanupResult(
            workspace_id=workspace_id,
            dry_run=dry_run,
            deleted_profiles=deleted_count,
            corrupted_profiles=corrupted_count,
            unused_profiles=unused_count,
            matched_profiles=len(candidates),
            removed_paths=removed_paths,
            bytes_freed=bytes_freed,
        )

    async def _candidate_profiles(
        self,
        *,
        workspace_id: str,
        include_deleted: bool,
        include_corrupted: bool,
        include_unused: bool,
    ) -> list[BrowserProfile]:
        conditions = []
        if include_deleted:
            conditions.append(BrowserProfile.status == BrowserProfileStatus.DELETED.value)
        if include_corrupted:
            conditions.append(BrowserProfile.status == BrowserProfileStatus.CORRUPTED.value)
            conditions.append(BrowserProfile.health_status == BrowserProfileHealthStatus.CORRUPTED.value)
        if include_unused:
            threshold = datetime.now(UTC) - timedelta(days=self.settings.browser_profile_unused_days)
            conditions.append(
                (BrowserProfile.status == BrowserProfileStatus.AVAILABLE.value)
                & (BrowserProfile.last_used_at.is_not(None))
                & (BrowserProfile.last_used_at < threshold)
            )
        if not conditions:
            return []
        statement = select(BrowserProfile).where(BrowserProfile.workspace_id == workspace_id, or_(*conditions))
        result = await self.session.execute(statement)
        unique: dict[UUID, BrowserProfile] = {}
        for profile in result.scalars().all():
            unique[profile.id] = profile
        return list(unique.values())

    async def _log_usage(
        self,
        *,
        workspace_id: str,
        profile_id: UUID,
        action: str,
        success: bool,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.session.add(
            BrowserProfileUsageLog(
                workspace_id=workspace_id,
                profile_id=profile_id,
                action=action,
                success=success,
                log_metadata=metadata or {},
            )
        )
        await self.session.flush()

    def _resolve_under_root(self, value: str) -> Path:
        path = Path(value)
        if not path.is_absolute():
            path = Path.cwd() / path
        root = Path(self.settings.browser_profile_root)
        if not root.is_absolute():
            root = Path.cwd() / root
        resolved_path = path.resolve()
        resolved_root = root.resolve()
        if not str(resolved_path).startswith(str(resolved_root)):
            raise ValueError("Profile path is outside profile root")
        return resolved_path

    def _dir_size(self, path: Path) -> int:
        if not path.exists():
            return 0
        return sum(file.stat().st_size for file in path.rglob("*") if file.is_file())
