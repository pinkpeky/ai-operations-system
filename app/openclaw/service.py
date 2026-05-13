"""OpenClaw adapter application service."""

from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.remote.services import BrowserWorkerSelector
from app.browser.remote.services.browser_worker_auth_service import BrowserWorkerAuthService
from app.browser.services import BrowserSecurityAuditService
from app.core.config import Settings, get_settings
from app.models.browser_worker import BrowserWorker
from app.openclaw.client import OpenClawWorkerClient
from app.openclaw.repository import OpenClawActionLogRepository
from app.openclaw.schemas import OpenClawActionRequest, OpenClawActionResponse, OpenClawCapabilitiesResponse, OpenClawHealthResponse

logger = logging.getLogger(__name__)


class OpenClawService:
    """OpenClaw worker adapter 服务。

    该服务只调度已注册 Browser Worker 的 OpenClaw mock runtime，并记录审计与 action log。
    """

    def __init__(self, session: AsyncSession, *, settings: Settings | None = None) -> None:
        self.session = session
        self.settings = settings or get_settings()
        self.selector = BrowserWorkerSelector(session)
        self.logs = OpenClawActionLogRepository(session)
        self.audit = BrowserSecurityAuditService(session)

    async def health_check(
        self,
        *,
        workspace_id: str,
        worker_id: UUID | None = None,
        actor_type: str = "api",
        actor_id: str | None = None,
    ) -> OpenClawHealthResponse:
        """检查当前 workspace 可用 OpenClaw worker。"""

        if not self.settings.openclaw_enabled:
            return OpenClawHealthResponse(success=False, provider=self.settings.openclaw_provider, enabled=False, reachable=False, error="OpenClaw is disabled")
        worker = await self._select_worker(workspace_id=workspace_id, worker_id=worker_id)
        if worker is None:
            await self._audit(workspace_id, actor_type, actor_id, "openclaw_health_check", None, False, "No available OpenClaw worker")
            return OpenClawHealthResponse(success=False, provider=self.settings.openclaw_provider, enabled=True, reachable=False, error="No available OpenClaw worker")
        result = await self._client(worker).health_check()
        await self._audit(workspace_id, actor_type, actor_id, "openclaw_health_check", worker.id, result.success, result.error, result.data)
        return OpenClawHealthResponse(
            provider=str(result.data.get("provider") or self.settings.openclaw_provider),
            enabled=bool(result.data.get("enabled", self.settings.openclaw_enabled)),
            reachable=result.success,
            worker_id=worker.id,
            worker_name=worker.worker_name,
            mock=bool(result.data.get("mock", True)),
            version=result.data.get("version"),
            error=result.error,
            raw=result.data,
        )

    async def capabilities(
        self,
        *,
        workspace_id: str,
        worker_id: UUID | None = None,
        actor_type: str = "api",
        actor_id: str | None = None,
    ) -> OpenClawCapabilitiesResponse:
        """查询当前 workspace OpenClaw capabilities。"""

        worker = await self._select_worker(workspace_id=workspace_id, worker_id=worker_id)
        if worker is None:
            await self._audit(workspace_id, actor_type, actor_id, "openclaw_capabilities", None, False, "No available OpenClaw worker")
            return OpenClawCapabilitiesResponse(success=False, provider=self.settings.openclaw_provider, enabled=self.settings.openclaw_enabled, error="No available OpenClaw worker")
        result = await self._client(worker).capabilities()
        await self._audit(workspace_id, actor_type, actor_id, "openclaw_capabilities", worker.id, result.success, result.error, result.data)
        return OpenClawCapabilitiesResponse(
            provider=str(result.data.get("provider") or self.settings.openclaw_provider),
            enabled=self.settings.openclaw_enabled,
            worker_id=worker.id,
            worker_name=worker.worker_name,
            mock=bool(result.data.get("mock", True)),
            capabilities=dict(result.data.get("capabilities") or {}),
            actions=list(result.data.get("actions") or []),
            error=result.error,
            raw=result.data,
        )

    async def execute_action(
        self,
        *,
        workspace_id: str,
        request: OpenClawActionRequest,
        actor_type: str = "api",
        actor_id: str | None = None,
    ) -> OpenClawActionResponse:
        """执行 OpenClaw mock action，并写入 action log 和 security audit。"""

        worker = await self._select_worker(workspace_id=workspace_id, worker_id=request.worker_id)
        if worker is None:
            await self._audit(workspace_id, actor_type, actor_id, "openclaw_action", None, False, "No available OpenClaw worker")
            log = await self.logs.create_log(
                workspace_id=workspace_id,
                worker_id=None,
                action_type=request.action_type,
                target=request.target,
                input_payload=request.model_dump(mode="json"),
                output_payload={},
                success=False,
                error="No available OpenClaw worker",
                duration_ms=0,
                provider=self.settings.openclaw_provider,
                mock=True,
            )
            return OpenClawActionResponse(
                success=False,
                action_type=request.action_type,
                output_payload={},
                error="No available OpenClaw worker",
                duration_ms=0,
                provider=self.settings.openclaw_provider,
                mock=True,
                worker_id=None,
                log_id=log.id,
            )
        payload = request.model_dump(mode="json", exclude={"worker_id"})
        result = await self._client(worker).execute_action(payload=payload)
        output_payload = dict(result.data.get("output_payload") or {})
        provider = str(result.data.get("provider") or self.settings.openclaw_provider)
        mock = bool(result.data.get("mock", True))
        duration_ms = result.data.get("duration_ms")
        log = await self.logs.create_log(
            workspace_id=workspace_id,
            worker_id=worker.id,
            action_type=request.action_type,
            target=request.target,
            input_payload=payload,
            output_payload=output_payload,
            success=result.success,
            error=result.error,
            duration_ms=int(duration_ms) if duration_ms is not None else None,
            provider=provider,
            mock=mock,
        )
        await self._audit(
            workspace_id,
            actor_type,
            actor_id,
            "openclaw_action",
            worker.id,
            result.success,
            result.error,
            {"action_type": request.action_type, "target": request.target, "log_id": str(log.id), "mock": mock},
        )
        logger.info(
            "OpenClaw action dispatched",
            extra={"workspace_id": workspace_id, "worker_id": str(worker.id), "action_type": request.action_type, "success": result.success},
        )
        return OpenClawActionResponse(
            success=result.success,
            action_type=request.action_type,
            output_payload=output_payload,
            error=result.error,
            duration_ms=int(duration_ms) if duration_ms is not None else None,
            provider=provider,
            mock=mock,
            worker_id=worker.id,
            log_id=log.id,
        )

    async def _select_worker(self, *, workspace_id: str, worker_id: UUID | None = None) -> BrowserWorker | None:
        """选择支持 OpenClaw capability 的在线 worker。"""

        return await self.selector.select_worker(workspace_id=workspace_id, worker_id=worker_id, capability="openclaw")

    def _client(self, worker: BrowserWorker) -> OpenClawWorkerClient:
        """构造指向 worker base_url 的 OpenClaw client。"""

        secret = BrowserWorkerAuthService.get_cached_secret(worker.id)
        return OpenClawWorkerClient(
            base_url=worker.base_url,
            timeout_seconds=self.settings.openclaw_action_timeout_seconds,
            retry_count=self.settings.browser_worker_retry_count,
            retry_backoff_seconds=self.settings.browser_action_retry_backoff_seconds,
            worker_id=str(worker.id),
            worker_secret=secret,
        )

    async def _audit(
        self,
        workspace_id: str,
        actor_type: str,
        actor_id: str | None,
        event_type: str,
        worker_id: UUID | None,
        success: bool,
        error: str | None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """写入 Browser security audit log。"""

        await self.audit.log_event(
            workspace_id=workspace_id,
            actor_type=actor_type,
            actor_id=actor_id,
            event_type=event_type,
            target_type="openclaw_worker",
            target_id=str(worker_id) if worker_id else None,
            success=success,
            error=error,
            metadata=metadata or {},
        )
