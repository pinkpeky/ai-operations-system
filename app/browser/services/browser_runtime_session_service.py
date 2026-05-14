"""Service layer for Phase 34 remote browser runtime sessions."""

from __future__ import annotations

import logging
import time
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.providers.remote_provider import RemoteBrowserProvider
from app.browser.remote.services.browser_worker_repository import BrowserWorkerRepository
from app.browser.services.browser_runtime_observability_service import BrowserRuntimeObservabilityService
from app.core.config import Settings, get_settings
from app.models.browser_runtime import BrowserRuntimeSession
from app.models.enums import BrowserRuntimeSessionStatus, BrowserWorkerSessionStatus

logger = logging.getLogger(__name__)


class BrowserRuntimeSessionService:
    """Create and operate remote browser runtime sessions with workspace scope."""

    def __init__(
        self,
        session: AsyncSession,
        *,
        settings: Settings | None = None,
        provider: RemoteBrowserProvider | None = None,
    ) -> None:
        self.session = session
        self.settings = settings or get_settings()
        self.provider = provider or RemoteBrowserProvider(session=session, settings=self.settings)
        self.worker_repository = BrowserWorkerRepository(session)
        self.observability = BrowserRuntimeObservabilityService(session, settings=self.settings)

    async def create_session(
        self,
        *,
        workspace_id: str,
        browser: str = "chromium",
        metadata: dict[str, Any] | None = None,
        worker_id: UUID | None = None,
    ) -> BrowserRuntimeSession:
        """Select a worker, create remote session, then persist the runtime record."""

        result = await self.provider.create_session(
            workspace_id=workspace_id,
            browser=browser,
            metadata=metadata or {},
            worker_id=worker_id,
        )
        if not result.success:
            raise ValueError(result.error or result.message)

        selected_worker_id = UUID(str(result.data["worker_id"]))
        worker_session = await self.worker_repository.create_worker_session(
            workspace_id=workspace_id,
            worker_id=selected_worker_id,
            remote_session_id=str(result.data["remote_session_id"]),
            local_browser_session_id=None,
            metadata={"browser_runtime": True, "provider_result": result.model_dump()},
        )
        runtime_session = BrowserRuntimeSession(
            workspace_id=workspace_id,
            worker_id=selected_worker_id,
            provider=self.provider.provider_name,
            browser=browser,
            session_status=BrowserRuntimeSessionStatus.ACTIVE.value,
            last_activity_at=datetime.now(UTC),
            runtime_metadata={
                **(metadata or {}),
                **result.data,
                "worker_session_id": str(worker_session.id),
                "current_url": result.data.get("current_url"),
                "page_title": result.data.get("page_title"),
            },
        )
        self.session.add(runtime_session)
        await self.session.commit()
        await self.session.refresh(runtime_session)
        await self.observability.append_event(
            workspace_id=workspace_id,
            runtime_session_id=runtime_session.id,
            worker_id=runtime_session.worker_id,
            event_type="session_created",
            status="completed",
            message="Remote browser runtime session created",
            payload={
                "browser": browser,
                "worker_name": result.data.get("worker_name"),
                "remote_session_id": result.data.get("remote_session_id"),
            },
            duration_ms=result.data.get("latency_ms"),
            commit=True,
        )
        logger.info(
            "Remote browser runtime session created",
            extra={
                "workspace_id": workspace_id,
                "runtime_session_id": str(runtime_session.id),
                "worker_id": str(runtime_session.worker_id),
            },
        )
        return runtime_session

    async def get_session(self, *, workspace_id: str, session_id: UUID) -> BrowserRuntimeSession | None:
        """Load one runtime session in the current workspace."""

        statement = select(BrowserRuntimeSession).where(
            BrowserRuntimeSession.workspace_id == workspace_id,
            BrowserRuntimeSession.id == session_id,
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def list_sessions(
        self,
        *,
        workspace_id: str,
        status: str | None = None,
        limit: int = 100,
    ) -> list[BrowserRuntimeSession]:
        """List runtime sessions scoped to one workspace."""

        statement = select(BrowserRuntimeSession).where(BrowserRuntimeSession.workspace_id == workspace_id)
        if status is not None:
            statement = statement.where(BrowserRuntimeSession.session_status == status)
        statement = statement.order_by(BrowserRuntimeSession.created_at.desc()).limit(limit)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def navigate(self, *, workspace_id: str, session_id: UUID, url: str) -> BrowserRuntimeSession:
        """Navigate a remote runtime session and update activity metadata."""

        runtime_session = await self._require_active(workspace_id=workspace_id, session_id=session_id)
        await self.observability.append_event(
            workspace_id=workspace_id,
            runtime_session_id=runtime_session.id,
            worker_id=runtime_session.worker_id,
            event_type="navigate_started",
            status="running",
            message="Browser runtime navigation started",
            payload={"url": url},
            commit=True,
        )
        started_at = time.perf_counter()
        result = await self.provider.navigate(runtime_session=runtime_session, url=url)
        duration_ms = self._elapsed_ms(started_at)
        if not result.success:
            await self._record_failure(
                runtime_session,
                action_type="navigate",
                payload={"url": url, "provider_result": result.model_dump()},
                error=result.error or result.message,
                duration_ms=duration_ms,
            )
            await self._mark_error(runtime_session, result.error or result.message)
            raise ValueError(result.error or result.message)
        await self._patch_metadata(
            runtime_session,
            {
                "current_url": result.data.get("current_url") or result.data.get("target_url") or url,
                "page_title": result.data.get("page_title"),
                "last_action": "navigate",
                "last_result": result.model_dump(),
            },
        )
        await self.observability.append_event(
            workspace_id=workspace_id,
            runtime_session_id=runtime_session.id,
            worker_id=runtime_session.worker_id,
            event_type="navigate_completed",
            status="completed",
            message="Browser runtime navigation completed",
            payload={"url": url, "current_url": result.data.get("current_url"), "page_title": result.data.get("page_title")},
            duration_ms=duration_ms,
            commit=False,
        )
        await self.session.commit()
        await self.session.refresh(runtime_session)
        return runtime_session

    async def screenshot(
        self,
        *,
        workspace_id: str,
        session_id: UUID,
        full_page: bool = True,
        screenshot_name: str | None = None,
    ) -> BrowserRuntimeSession:
        """Capture a screenshot and store metadata on the runtime session."""

        runtime_session = await self._require_active(workspace_id=workspace_id, session_id=session_id)
        await self.observability.append_event(
            workspace_id=workspace_id,
            runtime_session_id=runtime_session.id,
            worker_id=runtime_session.worker_id,
            event_type="screenshot_started",
            status="running",
            message="Browser runtime screenshot started",
            payload={"full_page": full_page, "screenshot_name": screenshot_name},
            commit=True,
        )
        started_at = time.perf_counter()
        result = await self.provider.screenshot(
            runtime_session=runtime_session,
            full_page=full_page,
            screenshot_name=screenshot_name,
        )
        duration_ms = self._elapsed_ms(started_at)
        if not result.success:
            await self._record_failure(
                runtime_session,
                action_type="screenshot",
                payload={"full_page": full_page, "screenshot_name": screenshot_name, "provider_result": result.model_dump()},
                error=result.error or result.message,
                duration_ms=duration_ms,
            )
            await self._mark_error(runtime_session, result.error or result.message)
            raise ValueError(result.error or result.message)
        await self._patch_metadata(
            runtime_session,
            {
                "last_screenshot_path": result.data.get("screenshot_path"),
                "page_title": result.data.get("page_title"),
                "current_url": result.data.get("current_url") or runtime_session.runtime_metadata.get("current_url"),
                "last_action": "screenshot",
                "last_result": self._redact_screenshot(result.model_dump()),
            },
        )
        await self.observability.capture_screenshot_snapshot(
            runtime_session=runtime_session,
            screenshot_path=result.data.get("screenshot_path"),
            metadata={
                "full_page": full_page,
                "screenshot_name": screenshot_name,
                "provider_result": self._redact_screenshot(result.model_dump()),
            },
            commit=False,
        )
        await self.observability.append_event(
            workspace_id=workspace_id,
            runtime_session_id=runtime_session.id,
            worker_id=runtime_session.worker_id,
            event_type="screenshot_completed",
            status="completed",
            message="Browser runtime screenshot completed",
            payload={"screenshot_path": result.data.get("screenshot_path"), "page_title": result.data.get("page_title")},
            duration_ms=duration_ms,
            commit=False,
        )
        await self.session.commit()
        await self.session.refresh(runtime_session)
        return runtime_session

    async def get_page(self, *, workspace_id: str, session_id: UUID) -> dict[str, Any]:
        """Fetch current page content without storing full HTML by default."""

        runtime_session = await self._require_active(workspace_id=workspace_id, session_id=session_id)
        started_at = time.perf_counter()
        result = await self.provider.get_page(runtime_session=runtime_session)
        duration_ms = self._elapsed_ms(started_at)
        if not result.success:
            await self._record_failure(
                runtime_session,
                action_type="get_page",
                payload={"provider_result": result.model_dump()},
                error=result.error or result.message,
                duration_ms=duration_ms,
            )
            await self._mark_error(runtime_session, result.error or result.message)
            raise ValueError(result.error or result.message)
        await self._patch_metadata(
            runtime_session,
            {
                "current_url": result.data.get("current_url") or runtime_session.runtime_metadata.get("current_url"),
                "page_title": result.data.get("page_title"),
                "last_action": "get_page",
                "last_result": {**result.model_dump(), "data": {**result.data, "content": "[redacted in metadata]"}},
            },
        )
        await self.observability.capture_page_snapshot(runtime_session=runtime_session, page_data=result.data, commit=False)
        await self.observability.append_event(
            workspace_id=workspace_id,
            runtime_session_id=runtime_session.id,
            worker_id=runtime_session.worker_id,
            event_type="page_snapshot_captured",
            status="completed",
            message="Browser runtime page snapshot captured",
            payload={
                "current_url": result.data.get("current_url"),
                "page_title": result.data.get("page_title"),
                "content_length": len(str(result.data.get("content") or "")),
            },
            duration_ms=duration_ms,
            commit=False,
        )
        await self.session.commit()
        return result.data

    async def close_session(self, *, workspace_id: str, session_id: UUID) -> BrowserRuntimeSession:
        """Close the remote session and release worker capacity."""

        runtime_session = await self.get_session(workspace_id=workspace_id, session_id=session_id)
        if runtime_session is None:
            raise ValueError("Browser runtime session not found")
        result = await self.provider.close_session(runtime_session=runtime_session)
        status = BrowserRuntimeSessionStatus.CLOSED.value if result.success else BrowserRuntimeSessionStatus.ERROR.value
        runtime_session.session_status = status
        await self._patch_metadata(runtime_session, {"close_result": result.model_dump(), "last_action": "close_session"})
        if not result.success:
            await self.observability.capture_error_snapshot(
                runtime_session=runtime_session,
                action_type="close_session",
                payload={"provider_result": result.model_dump()},
                error=result.error or result.message,
                duration_ms=result.data.get("latency_ms"),
                commit=False,
            )
        await self.observability.append_event(
            workspace_id=workspace_id,
            runtime_session_id=runtime_session.id,
            worker_id=runtime_session.worker_id,
            event_type="session_closed" if result.success else "action_failed",
            status="completed" if result.success else "failed",
            message="Browser runtime session closed" if result.success else "Browser runtime session close failed",
            payload={"provider_result": result.model_dump()},
            duration_ms=result.data.get("latency_ms"),
            error=None if result.success else result.error or result.message,
            commit=False,
        )
        worker_session_id = runtime_session.runtime_metadata.get("worker_session_id")
        if worker_session_id:
            worker_session = await self.worker_repository.get_worker_session_by_remote(
                remote_session_id=str(runtime_session.runtime_metadata.get("remote_session_id") or "")
            )
            if worker_session is not None and worker_session.status == BrowserWorkerSessionStatus.ACTIVE.value:
                await self.worker_repository.close_worker_session(worker_session)
        await self.session.commit()
        await self.session.refresh(runtime_session)
        return runtime_session

    async def cleanup_stale_sessions(self, *, workspace_id: str, stale_after_seconds: int | None = None) -> int:
        """Mark old active sessions stale without contacting the remote worker."""

        threshold = datetime.now(UTC) - timedelta(seconds=stale_after_seconds or self.settings.browser_session_timeout_seconds)
        statement = select(BrowserRuntimeSession).where(
            BrowserRuntimeSession.workspace_id == workspace_id,
            BrowserRuntimeSession.session_status == BrowserRuntimeSessionStatus.ACTIVE.value,
            BrowserRuntimeSession.last_activity_at.is_not(None),
            BrowserRuntimeSession.last_activity_at < threshold,
        )
        result = await self.session.execute(statement)
        sessions = list(result.scalars().all())
        for runtime_session in sessions:
            runtime_session.session_status = BrowserRuntimeSessionStatus.STALE.value
        await self.session.commit()
        return len(sessions)

    async def _require_active(self, *, workspace_id: str, session_id: UUID) -> BrowserRuntimeSession:
        runtime_session = await self.get_session(workspace_id=workspace_id, session_id=session_id)
        if runtime_session is None:
            raise ValueError("Browser runtime session not found")
        if runtime_session.session_status != BrowserRuntimeSessionStatus.ACTIVE.value:
            raise ValueError(f"Browser runtime session is not active: {runtime_session.session_status}")
        return runtime_session

    async def _patch_metadata(self, runtime_session: BrowserRuntimeSession, patch: dict[str, Any]) -> None:
        runtime_session.runtime_metadata = {**(runtime_session.runtime_metadata or {}), **patch}
        runtime_session.last_activity_at = datetime.now(UTC)
        await self.session.flush()

    async def _mark_error(self, runtime_session: BrowserRuntimeSession, error: str) -> None:
        runtime_session.session_status = BrowserRuntimeSessionStatus.ERROR.value
        await self._patch_metadata(runtime_session, {"last_error": error})
        await self.session.commit()

    async def _record_failure(
        self,
        runtime_session: BrowserRuntimeSession,
        *,
        action_type: str,
        payload: dict[str, Any],
        error: str,
        duration_ms: int | None,
    ) -> None:
        """Record a failed action in timeline and snapshot metadata."""

        await self.observability.append_event(
            workspace_id=runtime_session.workspace_id,
            runtime_session_id=runtime_session.id,
            worker_id=runtime_session.worker_id,
            event_type="action_failed",
            status="failed",
            message=f"Browser runtime action failed: {action_type}",
            payload=payload,
            duration_ms=duration_ms,
            error=error,
            commit=False,
        )
        await self.observability.capture_error_snapshot(
            runtime_session=runtime_session,
            action_type=action_type,
            payload=payload,
            error=error,
            duration_ms=duration_ms,
            commit=False,
        )

    def _redact_screenshot(self, payload: dict[str, Any]) -> dict[str, Any]:
        data = dict(payload.get("data") or {})
        if "screenshot_base64" in data:
            data["screenshot_base64"] = "[redacted]"
        return {**payload, "data": data}

    def _elapsed_ms(self, started_at: float) -> int:
        return max(0, int((time.perf_counter() - started_at) * 1000))
