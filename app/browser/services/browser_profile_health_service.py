"""Browser Profile 健康检查与 stale lock 恢复服务。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
import logging
from pathlib import Path
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.models.browser import BrowserProfile, BrowserProfileUsageLog, BrowserSession
from app.models.browser_worker import BrowserWorker, BrowserWorkerSession
from app.models.enums import (
    BrowserProfileHealthStatus,
    BrowserProfileStatus,
    BrowserSessionStatus,
    BrowserWorkerSessionStatus,
    BrowserWorkerStatus,
)

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class ProfileHealthCheckResult:
    """单个 profile 健康检查结果。"""

    profile: BrowserProfile
    healthy: bool
    health_status: str
    error: str | None = None


@dataclass(slots=True)
class StaleLockRecoveryResult:
    """stale lock 恢复结果。"""

    workspace_id: str
    recovered_count: int
    checked_count: int
    recovered_profile_ids: list[str]


@dataclass(slots=True)
class ProfileHealthSummary:
    """当前 workspace 的 profile 健康状态汇总。"""

    workspace_id: str
    total_profiles: int
    healthy_count: int
    warning_count: int
    corrupted_count: int
    stale_count: int
    deleted_count: int


class BrowserProfileHealthService:
    """负责 profile 健康状态、使用次数和 stale lock 恢复。"""

    def __init__(self, session: AsyncSession, *, settings: Settings | None = None) -> None:
        self.session = session
        self.settings = settings or get_settings()

    async def check_profile_health(self, *, workspace_id: str, profile_id: UUID) -> ProfileHealthCheckResult:
        """检查 profile 路径、状态和 lock 是否健康。"""

        profile = await self._get_profile(workspace_id=workspace_id, profile_id=profile_id, include_deleted=True)
        if profile is None:
            raise ValueError("Browser profile not found")
        if profile.status == BrowserProfileStatus.DELETED.value:
            await self._set_health(profile, BrowserProfileHealthStatus.DELETED.value, error=None)
            await self.session.commit()
            await self.session.refresh(profile)
            return ProfileHealthCheckResult(profile=profile, healthy=False, health_status=profile.health_status)
        if not self.validate_profile_path(profile=profile):
            profile.status = BrowserProfileStatus.CORRUPTED.value
            await self._set_health(profile, BrowserProfileHealthStatus.CORRUPTED.value, error="profile path does not exist")
            await self._log_usage(
                workspace_id=workspace_id,
                profile_id=profile.id,
                session_id=profile.locked_by_session_id,
                action="health_check",
                success=False,
                error="profile path does not exist",
                metadata={"profile_path": profile.profile_path},
            )
            await self.session.commit()
            await self.session.refresh(profile)
            return ProfileHealthCheckResult(
                profile=profile,
                healthy=False,
                health_status=profile.health_status,
                error=profile.last_error,
            )
        if profile.status == BrowserProfileStatus.LOCKED.value and self._is_lock_stale(profile):
            await self._set_health(profile, BrowserProfileHealthStatus.STALE.value, error="profile lock is stale")
            await self.session.commit()
            await self.session.refresh(profile)
            return ProfileHealthCheckResult(profile=profile, healthy=False, health_status=profile.health_status, error=profile.last_error)
        if profile.status == BrowserProfileStatus.CORRUPTED.value:
            await self._set_health(profile, BrowserProfileHealthStatus.CORRUPTED.value, error=profile.last_error)
            await self.session.commit()
            await self.session.refresh(profile)
            return ProfileHealthCheckResult(profile=profile, healthy=False, health_status=profile.health_status, error=profile.last_error)

        await self._set_health(profile, BrowserProfileHealthStatus.HEALTHY.value, error=None)
        await self._log_usage(
            workspace_id=workspace_id,
            profile_id=profile.id,
            session_id=profile.locked_by_session_id,
            action="health_check",
            success=True,
            metadata={"profile_path": profile.profile_path},
        )
        await self.session.commit()
        await self.session.refresh(profile)
        return ProfileHealthCheckResult(profile=profile, healthy=True, health_status=profile.health_status)

    async def mark_profile_corrupted(self, *, workspace_id: str, profile_id: UUID, error: str | None = None) -> BrowserProfile:
        """标记 profile 为 corrupted。"""

        profile = await self._get_profile(workspace_id=workspace_id, profile_id=profile_id, include_deleted=True)
        if profile is None:
            raise ValueError("Browser profile not found")
        profile.status = BrowserProfileStatus.CORRUPTED.value
        profile.corrupted_at = datetime.now(UTC)
        await self._set_health(profile, BrowserProfileHealthStatus.CORRUPTED.value, error=error)
        await self._log_usage(
            workspace_id=workspace_id,
            profile_id=profile.id,
            session_id=profile.locked_by_session_id,
            action="corrupted",
            success=False,
            error=error,
        )
        await self.session.commit()
        await self.session.refresh(profile)
        logger.error("Browser profile marked corrupted", extra={"workspace_id": workspace_id, "profile_id": str(profile.id), "error": error})
        return profile

    async def mark_profile_warning(self, *, workspace_id: str, profile_id: UUID, error: str | None = None) -> BrowserProfile:
        """标记 profile 为 warning，但不改变生命周期 status。"""

        profile = await self._get_profile(workspace_id=workspace_id, profile_id=profile_id, include_deleted=True)
        if profile is None:
            raise ValueError("Browser profile not found")
        await self._set_health(profile, BrowserProfileHealthStatus.WARNING.value, error=error)
        await self._log_usage(
            workspace_id=workspace_id,
            profile_id=profile.id,
            session_id=profile.locked_by_session_id,
            action="warning",
            success=False,
            error=error,
        )
        await self.session.commit()
        await self.session.refresh(profile)
        return profile

    async def recover_stale_lock(self, *, workspace_id: str, profile_id: UUID, reason: str | None = None) -> BrowserProfile:
        """恢复单个 stale lock，让 profile 重新变为 available。"""

        profile = await self._get_profile(workspace_id=workspace_id, profile_id=profile_id, include_deleted=True)
        if profile is None:
            raise ValueError("Browser profile not found")
        previous_session_id = profile.locked_by_session_id
        profile.status = BrowserProfileStatus.AVAILABLE.value
        profile.locked_by_session_id = None
        profile.locked_at = None
        profile.last_used_at = datetime.now(UTC)
        await self._set_health(profile, BrowserProfileHealthStatus.STALE.value, error=reason or "stale lock recovered")
        await self._log_usage(
            workspace_id=workspace_id,
            profile_id=profile.id,
            session_id=previous_session_id,
            action="recovery",
            success=True,
            metadata={"reason": reason or "stale lock recovered"},
        )
        await self.session.commit()
        await self.session.refresh(profile)
        logger.info("Browser profile stale lock recovered", extra={"workspace_id": workspace_id, "profile_id": str(profile.id)})
        return profile

    async def recover_stale_locks(self, *, workspace_id: str) -> StaleLockRecoveryResult:
        """批量恢复超时、closed/failed session 或 offline worker 持有的 lock。"""

        statement = select(BrowserProfile).where(
            BrowserProfile.workspace_id == workspace_id,
            BrowserProfile.status == BrowserProfileStatus.LOCKED.value,
        )
        result = await self.session.execute(statement)
        profiles = list(result.scalars().all())
        recovered_ids: list[str] = []
        for profile in profiles:
            reason = await self._recovery_reason(profile)
            if reason is None:
                continue
            previous_session_id = profile.locked_by_session_id
            profile.status = BrowserProfileStatus.AVAILABLE.value
            profile.locked_by_session_id = None
            profile.locked_at = None
            profile.last_used_at = datetime.now(UTC)
            await self._set_health(profile, BrowserProfileHealthStatus.STALE.value, error=reason)
            await self._log_usage(
                workspace_id=workspace_id,
                profile_id=profile.id,
                session_id=previous_session_id,
                action="recovery",
                success=True,
                metadata={"reason": reason},
            )
            recovered_ids.append(str(profile.id))
        await self.session.commit()
        logger.info("Browser profile stale lock recovery completed", extra={"workspace_id": workspace_id, "recovered_count": len(recovered_ids)})
        return StaleLockRecoveryResult(
            workspace_id=workspace_id,
            recovered_count=len(recovered_ids),
            checked_count=len(profiles),
            recovered_profile_ids=recovered_ids,
        )

    def validate_profile_path(self, *, profile: BrowserProfile) -> bool:
        """验证 profile path 是否存在且在 profile root 下。"""

        path = self._resolve_profile_path(profile.profile_path)
        root = self._resolve_profile_path(self.settings.browser_profile_root)
        try:
            return path.exists() and str(path).startswith(str(root))
        except Exception:
            return False

    def validate_profile_runtime(self, *, profile: BrowserProfile) -> bool:
        """轻量校验 runtime 目录可读写，不启动真实浏览器。"""

        path = self._resolve_profile_path(profile.profile_path)
        try:
            return path.exists() and path.is_dir()
        except Exception:
            return False

    async def increment_usage_count(self, *, workspace_id: str, profile_id: UUID, session_id: UUID | None = None) -> BrowserProfile:
        """增加 profile 使用次数，并写入 usage log。"""

        profile = await self._get_profile(workspace_id=workspace_id, profile_id=profile_id)
        if profile is None:
            raise ValueError("Browser profile not found")
        profile.usage_count = max(0, profile.usage_count or 0) + 1
        await self._log_usage(
            workspace_id=workspace_id,
            profile_id=profile.id,
            session_id=session_id,
            action="session_start",
            success=True,
            metadata={"usage_count": profile.usage_count},
        )
        await self.session.flush()
        return profile

    async def list_usage_logs(self, *, workspace_id: str, profile_id: UUID, limit: int = 100) -> list[BrowserProfileUsageLog]:
        """列出 profile usage logs。"""

        statement = (
            select(BrowserProfileUsageLog)
            .where(BrowserProfileUsageLog.workspace_id == workspace_id, BrowserProfileUsageLog.profile_id == profile_id)
            .order_by(BrowserProfileUsageLog.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def summarize_profiles(self, *, workspace_id: str) -> ProfileHealthSummary:
        """按 health_status 汇总当前 workspace 的 profile 健康状态。"""

        statement = select(BrowserProfile).where(BrowserProfile.workspace_id == workspace_id)
        result = await self.session.execute(statement)
        profiles = list(result.scalars().all())
        counts = {
            BrowserProfileHealthStatus.HEALTHY.value: 0,
            BrowserProfileHealthStatus.WARNING.value: 0,
            BrowserProfileHealthStatus.CORRUPTED.value: 0,
            BrowserProfileHealthStatus.STALE.value: 0,
            BrowserProfileHealthStatus.DELETED.value: 0,
        }
        for profile in profiles:
            status = profile.health_status or BrowserProfileHealthStatus.HEALTHY.value
            counts[status] = counts.get(status, 0) + 1
        return ProfileHealthSummary(
            workspace_id=workspace_id,
            total_profiles=len(profiles),
            healthy_count=counts[BrowserProfileHealthStatus.HEALTHY.value],
            warning_count=counts[BrowserProfileHealthStatus.WARNING.value],
            corrupted_count=counts[BrowserProfileHealthStatus.CORRUPTED.value],
            stale_count=counts[BrowserProfileHealthStatus.STALE.value],
            deleted_count=counts[BrowserProfileHealthStatus.DELETED.value],
        )

    async def record_usage(
        self,
        *,
        workspace_id: str,
        profile_id: UUID,
        session_id: UUID | None = None,
        action: str,
        success: bool,
        error: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """公开的 usage log 入口，供 BrowserService 等调用。"""

        await self._log_usage(
            workspace_id=workspace_id,
            profile_id=profile_id,
            session_id=session_id,
            action=action,
            success=success,
            error=error,
            metadata=metadata,
        )
        await self.session.flush()

    async def _get_profile(self, *, workspace_id: str, profile_id: UUID, include_deleted: bool = False) -> BrowserProfile | None:
        statement = select(BrowserProfile).where(BrowserProfile.workspace_id == workspace_id, BrowserProfile.id == profile_id)
        if not include_deleted:
            statement = statement.where(BrowserProfile.status != BrowserProfileStatus.DELETED.value)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def _recovery_reason(self, profile: BrowserProfile) -> str | None:
        if self._is_lock_stale(profile):
            return f"profile lock exceeded {self.settings.browser_profile_lock_timeout_seconds}s"
        if profile.locked_by_session_id is None:
            return "locked profile has no locking session"
        session = await self.session.get(BrowserSession, profile.locked_by_session_id)
        if session is None or session.status != BrowserSessionStatus.ACTIVE.value:
            return "locking session is closed or missing"
        worker_statement = (
            select(BrowserWorkerSession, BrowserWorker)
            .join(BrowserWorker, BrowserWorker.id == BrowserWorkerSession.worker_id)
            .where(
                BrowserWorkerSession.local_browser_session_id == profile.locked_by_session_id,
                BrowserWorkerSession.status == BrowserWorkerSessionStatus.ACTIVE.value,
                BrowserWorker.status.in_([BrowserWorkerStatus.OFFLINE.value, BrowserWorkerStatus.ERROR.value]),
            )
        )
        worker_result = await self.session.execute(worker_statement)
        row = worker_result.first()
        if row is not None:
            return "locking worker is offline or error"
        return None

    def _is_lock_stale(self, profile: BrowserProfile) -> bool:
        if profile.locked_at is None:
            return False
        locked_at = profile.locked_at
        if locked_at.tzinfo is None:
            locked_at = locked_at.replace(tzinfo=UTC)
        return datetime.now(UTC) - locked_at > timedelta(seconds=self.settings.browser_profile_lock_timeout_seconds)

    async def _set_health(self, profile: BrowserProfile, status: str, *, error: str | None) -> None:
        profile.health_status = status
        profile.last_health_check_at = datetime.now(UTC)
        profile.last_error = error
        if status == BrowserProfileHealthStatus.CORRUPTED.value and profile.corrupted_at is None:
            profile.corrupted_at = datetime.now(UTC)
        await self.session.flush()

    async def _log_usage(
        self,
        *,
        workspace_id: str,
        profile_id: UUID,
        session_id: UUID | None = None,
        action: str,
        success: bool,
        error: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        log = BrowserProfileUsageLog(
            workspace_id=workspace_id,
            profile_id=profile_id,
            session_id=session_id,
            action=action,
            success=success,
            error=error,
            log_metadata=metadata or {},
        )
        self.session.add(log)
        await self.session.flush()

    def _resolve_profile_path(self, value: str) -> Path:
        path = Path(value)
        if not path.is_absolute():
            path = Path.cwd() / path
        return path.resolve()
