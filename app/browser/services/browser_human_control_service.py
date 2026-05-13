"""Human-in-the-loop Browser Control 服务。

该服务只负责人工接管的状态机、session pause/resume、事件记录和 worker
metadata 协议预留，不实现 VNC/noVNC/DevTools 真实远程 UI。
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
import logging
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.remote.client import BrowserWorkerClient
from app.browser.remote.services import BrowserWorkerRepository
from app.browser.repositories import BrowserRepository
from app.core.config import Settings, get_settings
from app.models.browser import BrowserHumanControlEvent, BrowserHumanControlSession, BrowserSession
from app.models.enums import (
    BrowserHumanControlEventType,
    BrowserHumanControlStatus,
    BrowserSessionStatus,
)

logger = logging.getLogger(__name__)


class BrowserHumanControlService:
    """按 workspace 隔离管理人工接管浏览器控制。"""

    def __init__(self, session: AsyncSession, *, settings: Settings | None = None) -> None:
        self.session = session
        self.settings = settings or get_settings()
        self.browser_repository = BrowserRepository(session)
        self.worker_repository = BrowserWorkerRepository(session)

    async def request_control(
        self,
        *,
        workspace_id: str,
        browser_session_id: UUID,
        reason: str | None,
        requested_by: str | None,
        metadata: dict[str, Any] | None = None,
    ) -> BrowserHumanControlSession:
        """请求人工接管，并立即暂停自动化动作。"""

        browser_session = await self._get_browser_session(workspace_id=workspace_id, browser_session_id=browser_session_id)
        if browser_session.status not in {BrowserSessionStatus.ACTIVE.value, BrowserSessionStatus.PAUSED.value}:
            raise ValueError(f"Browser session cannot enter human control from status: {browser_session.status}")
        existing = await self._active_control_for_session(workspace_id=workspace_id, browser_session_id=browser_session_id)
        if existing is not None:
            raise ValueError("Browser session already has an active human control session")

        control_session = BrowserHumanControlSession(
            workspace_id=workspace_id,
            browser_session_id=browser_session.id,
            profile_id=browser_session.profile_id,
            worker_id=self._worker_id(browser_session),
            status=BrowserHumanControlStatus.REQUESTED.value,
            reason=reason,
            requested_by=requested_by,
            expires_at=datetime.now(UTC) + timedelta(seconds=self.settings.browser_human_control_timeout_seconds),
            control_metadata=metadata or {},
        )
        self.session.add(control_session)
        await self.session.flush()
        await self._pause_browser_session(
            browser_session=browser_session,
            control_session=control_session,
            status=BrowserHumanControlStatus.REQUESTED.value,
        )
        await self.add_control_event(
            workspace_id=workspace_id,
            control_session_id=control_session.id,
            event_type=BrowserHumanControlEventType.REQUESTED.value,
            message=reason or "human control requested",
            payload={"requested_by": requested_by, "metadata": metadata or {}},
            commit=False,
        )
        await self._log_browser(
            browser_session=browser_session,
            level="info",
            message="Browser session paused for human control",
            metadata={"control_session_id": str(control_session.id), "reason": reason},
        )
        await self.session.commit()
        await self.session.refresh(control_session)
        logger.info("Browser human control requested", extra={"workspace_id": workspace_id, "control_session_id": str(control_session.id)})
        return control_session

    async def approve_control(
        self,
        *,
        workspace_id: str,
        control_session_id: UUID,
        approved_by: str | None,
        metadata: dict[str, Any] | None = None,
    ) -> BrowserHumanControlSession:
        """批准人工接管请求，状态仍保持 requested，等待 start。"""

        control_session = await self._get_control_session(workspace_id=workspace_id, control_session_id=control_session_id)
        if control_session.status != BrowserHumanControlStatus.REQUESTED.value:
            raise ValueError(f"Human control cannot be approved from status: {control_session.status}")
        control_session.approved_by = approved_by
        control_session.control_metadata = {**(control_session.control_metadata or {}), **(metadata or {})}
        browser_session = await self._get_browser_session(workspace_id=workspace_id, browser_session_id=control_session.browser_session_id)
        await self.add_control_event(
            workspace_id=workspace_id,
            control_session_id=control_session.id,
            event_type=BrowserHumanControlEventType.APPROVED.value,
            message="human control approved",
            payload={"approved_by": approved_by, "metadata": metadata or {}},
            commit=False,
        )
        await self._log_browser(
            browser_session=browser_session,
            level="info",
            message="Browser human control approved",
            metadata={"control_session_id": str(control_session.id), "approved_by": approved_by},
        )
        await self.session.commit()
        await self.session.refresh(control_session)
        return control_session

    async def start_control(
        self,
        *,
        workspace_id: str,
        control_session_id: UUID,
        metadata: dict[str, Any] | None = None,
    ) -> BrowserHumanControlSession:
        """启动人工接管窗口，并通知 worker runtime 进入 metadata-level human control。"""

        control_session = await self._get_control_session(workspace_id=workspace_id, control_session_id=control_session_id)
        if control_session.status != BrowserHumanControlStatus.REQUESTED.value:
            raise ValueError(f"Human control cannot start from status: {control_session.status}")
        browser_session = await self._get_browser_session(workspace_id=workspace_id, browser_session_id=control_session.browser_session_id)
        control_session.status = BrowserHumanControlStatus.ACTIVE.value
        control_session.started_at = datetime.now(UTC)
        control_session.control_metadata = {**(control_session.control_metadata or {}), **(metadata or {})}
        await self._pause_browser_session(
            browser_session=browser_session,
            control_session=control_session,
            status=BrowserHumanControlStatus.ACTIVE.value,
        )
        worker_result = await self._notify_worker(control_session=control_session, browser_session=browser_session, operation="start")
        await self.add_control_event(
            workspace_id=workspace_id,
            control_session_id=control_session.id,
            event_type=BrowserHumanControlEventType.STARTED.value,
            message="human control started",
            payload={"metadata": metadata or {}, "worker_result": worker_result},
            commit=False,
        )
        await self._log_browser(
            browser_session=browser_session,
            level="info",
            message="Browser human control started",
            metadata={"control_session_id": str(control_session.id), "worker_result": worker_result},
        )
        await self.session.commit()
        await self.session.refresh(control_session)
        return control_session

    async def complete_control(
        self,
        *,
        workspace_id: str,
        control_session_id: UUID,
        note: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> BrowserHumanControlSession:
        """完成人工接管并恢复 browser session。"""

        control_session = await self._get_control_session(workspace_id=workspace_id, control_session_id=control_session_id)
        if control_session.status not in {BrowserHumanControlStatus.REQUESTED.value, BrowserHumanControlStatus.ACTIVE.value}:
            raise ValueError(f"Human control cannot be completed from status: {control_session.status}")
        browser_session = await self._get_browser_session(workspace_id=workspace_id, browser_session_id=control_session.browser_session_id)
        worker_result = await self._notify_worker(control_session=control_session, browser_session=browser_session, operation="complete", note=note)
        control_session.status = BrowserHumanControlStatus.COMPLETED.value
        control_session.completed_at = datetime.now(UTC)
        control_session.control_metadata = {**(control_session.control_metadata or {}), **(metadata or {})}
        await self._resume_browser_session(
            browser_session=browser_session,
            control_session=control_session,
            status=BrowserHumanControlStatus.COMPLETED.value,
        )
        await self.add_control_event(
            workspace_id=workspace_id,
            control_session_id=control_session.id,
            event_type=BrowserHumanControlEventType.COMPLETED.value,
            message=note or "human control completed",
            payload={"note": note, "metadata": metadata or {}, "worker_result": worker_result},
            commit=False,
        )
        await self._log_browser(
            browser_session=browser_session,
            level="info",
            message="Browser session resumed after human control",
            metadata={"control_session_id": str(control_session.id), "worker_result": worker_result},
        )
        await self.session.commit()
        await self.session.refresh(control_session)
        return control_session

    async def cancel_control(
        self,
        *,
        workspace_id: str,
        control_session_id: UUID,
        reason: str | None = None,
    ) -> BrowserHumanControlSession:
        """取消人工接管并恢复 session。"""

        control_session = await self._get_control_session(workspace_id=workspace_id, control_session_id=control_session_id)
        if control_session.status in {
            BrowserHumanControlStatus.COMPLETED.value,
            BrowserHumanControlStatus.CANCELLED.value,
            BrowserHumanControlStatus.EXPIRED.value,
        }:
            raise ValueError(f"Human control cannot be cancelled from status: {control_session.status}")
        browser_session = await self._get_browser_session(workspace_id=workspace_id, browser_session_id=control_session.browser_session_id)
        control_session.status = BrowserHumanControlStatus.CANCELLED.value
        control_session.completed_at = datetime.now(UTC)
        await self._resume_browser_session(
            browser_session=browser_session,
            control_session=control_session,
            status=BrowserHumanControlStatus.CANCELLED.value,
        )
        await self.add_control_event(
            workspace_id=workspace_id,
            control_session_id=control_session.id,
            event_type=BrowserHumanControlEventType.CANCELLED.value,
            message=reason or "human control cancelled",
            payload={"reason": reason},
            commit=False,
        )
        await self._log_browser(
            browser_session=browser_session,
            level="info",
            message="Browser human control cancelled",
            metadata={"control_session_id": str(control_session.id), "reason": reason},
        )
        await self.session.commit()
        await self.session.refresh(control_session)
        return control_session

    async def expire_control(
        self,
        *,
        workspace_id: str,
        control_session_id: UUID,
        reason: str | None = None,
    ) -> BrowserHumanControlSession:
        """将人工接管标记为 expired，并恢复 session，避免永久暂停。"""

        control_session = await self._get_control_session(workspace_id=workspace_id, control_session_id=control_session_id)
        if control_session.status in {
            BrowserHumanControlStatus.COMPLETED.value,
            BrowserHumanControlStatus.CANCELLED.value,
            BrowserHumanControlStatus.EXPIRED.value,
        }:
            return control_session
        browser_session = await self._get_browser_session(workspace_id=workspace_id, browser_session_id=control_session.browser_session_id)
        control_session.status = BrowserHumanControlStatus.EXPIRED.value
        control_session.completed_at = datetime.now(UTC)
        await self._resume_browser_session(
            browser_session=browser_session,
            control_session=control_session,
            status=BrowserHumanControlStatus.EXPIRED.value,
        )
        await self.add_control_event(
            workspace_id=workspace_id,
            control_session_id=control_session.id,
            event_type=BrowserHumanControlEventType.EXPIRED.value,
            message=reason or "human control expired",
            payload={"reason": reason},
            commit=False,
        )
        await self._log_browser(
            browser_session=browser_session,
            level="warning",
            message="Browser human control expired",
            metadata={"control_session_id": str(control_session.id), "reason": reason},
        )
        await self.session.commit()
        await self.session.refresh(control_session)
        return control_session

    async def list_control_sessions(
        self,
        *,
        workspace_id: str,
        status: str | None = None,
        limit: int = 100,
    ) -> list[BrowserHumanControlSession]:
        """列出当前 workspace 的人工接管会话。"""

        statement = select(BrowserHumanControlSession).where(BrowserHumanControlSession.workspace_id == workspace_id)
        if status is not None:
            statement = statement.where(BrowserHumanControlSession.status == status)
        statement = statement.order_by(BrowserHumanControlSession.created_at.desc()).limit(limit)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def get_control_session(
        self,
        *,
        workspace_id: str,
        control_session_id: UUID,
    ) -> BrowserHumanControlSession | None:
        """读取单个人工接管会话。"""

        statement = select(BrowserHumanControlSession).where(
            BrowserHumanControlSession.workspace_id == workspace_id,
            BrowserHumanControlSession.id == control_session_id,
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def list_control_events(
        self,
        *,
        workspace_id: str,
        control_session_id: UUID,
        limit: int = 100,
    ) -> list[BrowserHumanControlEvent]:
        """列出人工接管事件。"""

        if await self.get_control_session(workspace_id=workspace_id, control_session_id=control_session_id) is None:
            raise ValueError("Human control session not found")
        statement = (
            select(BrowserHumanControlEvent)
            .where(
                BrowserHumanControlEvent.workspace_id == workspace_id,
                BrowserHumanControlEvent.control_session_id == control_session_id,
            )
            .order_by(BrowserHumanControlEvent.created_at.asc())
            .limit(limit)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def add_control_event(
        self,
        *,
        workspace_id: str,
        control_session_id: UUID,
        event_type: str,
        message: str | None,
        payload: dict[str, Any] | None = None,
        commit: bool = True,
    ) -> BrowserHumanControlEvent:
        """写入人工接管事件。"""

        event = BrowserHumanControlEvent(
            workspace_id=workspace_id,
            control_session_id=control_session_id,
            event_type=event_type,
            message=message,
            payload=payload or {},
        )
        self.session.add(event)
        await self.session.flush()
        if commit:
            await self.session.commit()
            await self.session.refresh(event)
        return event

    async def _active_control_for_session(self, *, workspace_id: str, browser_session_id: UUID) -> BrowserHumanControlSession | None:
        statement = select(BrowserHumanControlSession).where(
            BrowserHumanControlSession.workspace_id == workspace_id,
            BrowserHumanControlSession.browser_session_id == browser_session_id,
            BrowserHumanControlSession.status.in_(
                [BrowserHumanControlStatus.REQUESTED.value, BrowserHumanControlStatus.ACTIVE.value]
            ),
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def _get_control_session(self, *, workspace_id: str, control_session_id: UUID) -> BrowserHumanControlSession:
        control_session = await self.get_control_session(workspace_id=workspace_id, control_session_id=control_session_id)
        if control_session is None:
            raise ValueError("Human control session not found")
        return control_session

    async def _get_browser_session(self, *, workspace_id: str, browser_session_id: UUID) -> BrowserSession:
        browser_session = await self.browser_repository.get_session(session_id=browser_session_id, workspace_id=workspace_id)
        if browser_session is None:
            raise ValueError("Browser session not found")
        return browser_session

    async def _pause_browser_session(
        self,
        *,
        browser_session: BrowserSession,
        control_session: BrowserHumanControlSession,
        status: str,
    ) -> None:
        browser_session.status = BrowserSessionStatus.PAUSED.value
        browser_session.human_control_status = status
        browser_session.human_control_session_id = control_session.id
        if browser_session.paused_at is None:
            browser_session.paused_at = datetime.now(UTC)
        await self.session.flush()

    async def _resume_browser_session(
        self,
        *,
        browser_session: BrowserSession,
        control_session: BrowserHumanControlSession,
        status: str,
    ) -> None:
        browser_session.status = BrowserSessionStatus.ACTIVE.value
        browser_session.human_control_status = status
        browser_session.human_control_session_id = control_session.id
        browser_session.resumed_at = datetime.now(UTC)
        await self.session.flush()

    async def _log_browser(
        self,
        *,
        browser_session: BrowserSession,
        level: str,
        message: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        await self.browser_repository.create_log(
            workspace_id=browser_session.workspace_id,
            session_id=browser_session.id,
            action_id=None,
            level=level,
            message=message,
            metadata=metadata,
        )

    async def _notify_worker(
        self,
        *,
        control_session: BrowserHumanControlSession,
        browser_session: BrowserSession,
        operation: str,
        note: str | None = None,
    ) -> dict[str, Any]:
        """通知 worker runtime。缺少 remote metadata 时降级为 skip，系统不崩。"""

        provider_metadata = browser_session.provider_session_metadata or {}
        remote_session_id = str(provider_metadata.get("remote_session_id") or provider_metadata.get("provider_session_id") or "")
        if control_session.worker_id is None or not remote_session_id:
            return {"success": True, "skipped": True, "reason": "worker metadata not available"}
        worker = await self.worker_repository.get_worker(
            workspace_id=control_session.workspace_id,
            worker_id=control_session.worker_id,
        )
        if worker is None:
            return {"success": False, "skipped": True, "error": "worker not found"}
        client = BrowserWorkerClient(
            base_url=worker.base_url,
            timeout_seconds=self.settings.browser_worker_default_timeout_seconds,
            retry_count=self.settings.browser_worker_retry_count,
        )
        payload = {
            "control_session_id": str(control_session.id),
            "browser_session_id": str(browser_session.id),
            "profile_id": str(control_session.profile_id) if control_session.profile_id else None,
            "reason": control_session.reason,
            "note": note,
            "metadata": control_session.control_metadata or {},
        }
        if operation == "start":
            result = await client.start_human_control(remote_session_id=remote_session_id, payload=payload)
        elif operation == "complete":
            result = await client.complete_human_control(remote_session_id=remote_session_id, payload=payload)
        else:
            return {"success": False, "error": f"unsupported human control worker operation: {operation}"}
        return result.model_dump()

    def _worker_id(self, browser_session: BrowserSession) -> UUID | None:
        value = (browser_session.provider_session_metadata or {}).get("worker_id")
        if value is None:
            return None
        try:
            return UUID(str(value))
        except Exception:
            return None
