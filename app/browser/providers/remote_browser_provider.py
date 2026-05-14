"""Remote Browser Provider。

该 provider 不直接启动浏览器，而是通过 BrowserWorkerClient 把动作分发到已注册的
Browser Worker。Phase 19 只使用 mock worker runtime 验证协议，不部署真实外部 worker。
"""

from __future__ import annotations

import logging
import time
from typing import Any, Callable
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.providers.base import BaseBrowserProvider, BrowserProviderResult
from app.browser.remote.client import BrowserWorkerClient
from app.browser.remote.services.browser_worker_auth_service import BrowserWorkerAuthService
from app.browser.remote.services.browser_worker_repository import BrowserWorkerRepository
from app.browser.remote.services.browser_worker_selector import BrowserWorkerSelector
from app.core.config import Settings
from app.models.browser_worker import BrowserWorker

logger = logging.getLogger(__name__)

BrowserWorkerClientFactory = Callable[[BrowserWorker], BrowserWorkerClient]


class RemoteBrowserProvider(BaseBrowserProvider):
    """通过 Remote Browser Worker 执行动作的 provider。"""

    provider_name = "remote"

    def __init__(
        self,
        *,
        session: AsyncSession,
        settings: Settings,
        client_factory: BrowserWorkerClientFactory | None = None,
    ) -> None:
        self.session = session
        self.settings = settings
        self.repository = BrowserWorkerRepository(session)
        self.selector = BrowserWorkerSelector(session)
        self.client_factory = client_factory or self._default_client_factory

    async def create_session(self, *, metadata: dict[str, Any] | None = None) -> BrowserProviderResult:
        """选择可用 worker 并创建 remote session。"""

        workspace_id = str((metadata or {}).get("workspace_id") or "")
        local_session_id = self._parse_uuid((metadata or {}).get("session_id"))
        if not workspace_id:
            return BrowserProviderResult(success=False, message="workspace_id is required", error="workspace_id is required")

        requested_worker_id = self._parse_uuid((metadata or {}).get("worker_id"))
        worker = await self.selector.select_worker(workspace_id=workspace_id, worker_id=requested_worker_id)
        if worker is None:
            return BrowserProviderResult(
                success=False,
                message="No available browser worker",
                error="No online or busy browser worker found in current workspace",
                data={"default_worker_url": self.settings.browser_worker_default_url},
            )

        client = self.client_factory(worker)
        payload = {
            "workspace_id": workspace_id,
            "local_browser_session_id": str(local_session_id) if local_session_id else None,
            "profile_id": (metadata or {}).get("profile_id"),
            "profile_path": (metadata or {}).get("profile_path"),
            "use_persistent_profile": bool((metadata or {}).get("use_persistent_profile")),
            "metadata": metadata or {},
        }
        result = await client.create_session(payload=payload)
        if not result.success:
            return BrowserProviderResult(
                success=False,
                message=result.message,
                error=result.error,
                data={
                    "worker_id": str(worker.id),
                    "worker_name": worker.worker_name,
                    "profile_startup_latency_ms": result.data.get("profile_startup_latency_ms"),
                    "profile_id": result.data.get("profile_id"),
                    "profile_path": result.data.get("profile_path"),
                },
            )

        remote_session_id = str(result.data.get("remote_session_id") or "")
        if not remote_session_id:
            return BrowserProviderResult(
                success=False,
                message="Worker did not return remote_session_id",
                error="remote_session_id missing",
                data={"worker_id": str(worker.id), "worker_name": worker.worker_name},
            )

        worker_session = await self.repository.create_worker_session(
            workspace_id=workspace_id,
            worker_id=worker.id,
            remote_session_id=remote_session_id,
            local_browser_session_id=local_session_id,
            metadata={"client_result": result.model_dump(), "worker_base_url": worker.base_url},
        )
        provider_metadata = {
            "provider_session_id": remote_session_id,
            "remote_session_id": remote_session_id,
            "worker_session_id": str(worker_session.id),
            "worker_id": str(worker.id),
            "worker_name": worker.worker_name,
            "worker_type": worker.worker_type,
            "worker_base_url": worker.base_url,
            "worker_load": worker.current_load,
            "active_sessions": worker.active_sessions,
            "max_sessions": worker.max_sessions,
            "profile_id": (metadata or {}).get("profile_id"),
            "profile_path": result.data.get("profile_path") or (metadata or {}).get("profile_path"),
            "persistent_context_enabled": bool(result.data.get("persistent_context_enabled") or (metadata or {}).get("use_persistent_profile")),
            "profile_startup_latency_ms": result.data.get("profile_startup_latency_ms"),
        }
        return BrowserProviderResult(
            success=True,
            message="remote browser session created",
            data={
                "provider_session_id": remote_session_id,
                "browser_id": remote_session_id,
                "page_id": None,
                "provider_session_metadata": provider_metadata,
                **provider_metadata,
            },
        )

    async def close_session(self, *, provider_session_id: str | None = None) -> BrowserProviderResult:
        """关闭 remote session。"""

        if not provider_session_id:
            return BrowserProviderResult(success=False, message="provider_session_id is required", error="missing provider_session_id")
        worker_session = await self.repository.get_worker_session_by_remote(remote_session_id=provider_session_id)
        if worker_session is None:
            return BrowserProviderResult(success=False, message="Remote worker session not found", error="session not found")
        worker = await self.repository.get_worker(workspace_id=worker_session.workspace_id, worker_id=worker_session.worker_id)
        if worker is None:
            return BrowserProviderResult(success=False, message="Browser worker not found", error="worker not found")
        result = await self.client_factory(worker).close_session(remote_session_id=provider_session_id)
        if result.success:
            await self.repository.close_worker_session(worker_session)
        return BrowserProviderResult(
            success=result.success,
            message=result.message,
            error=result.error,
            data={
                "remote_session_id": provider_session_id,
                "worker_id": str(worker.id),
                "worker_name": worker.worker_name,
                "client_result": result.model_dump(),
            },
        )

    async def navigate(
        self,
        *,
        target: str | None,
        input_payload: dict[str, Any],
        session_metadata: dict[str, Any] | None = None,
    ) -> BrowserProviderResult:
        """分发 navigate action。"""

        return await self._dispatch_action("navigate", target=target, input_payload=input_payload, session_metadata=session_metadata)

    async def click(
        self,
        *,
        target: str | None,
        input_payload: dict[str, Any],
        session_metadata: dict[str, Any] | None = None,
    ) -> BrowserProviderResult:
        """分发 click action。"""

        return await self._dispatch_action("click", target=target, input_payload=input_payload, session_metadata=session_metadata)

    async def type_text(
        self,
        *,
        target: str | None,
        input_payload: dict[str, Any],
        session_metadata: dict[str, Any] | None = None,
    ) -> BrowserProviderResult:
        """分发 type_text action。"""

        return await self._dispatch_action("type_text", target=target, input_payload=input_payload, session_metadata=session_metadata)

    async def scroll(
        self,
        *,
        target: str | None,
        input_payload: dict[str, Any],
        session_metadata: dict[str, Any] | None = None,
    ) -> BrowserProviderResult:
        """分发 scroll action。"""

        return await self._dispatch_action("scroll", target=target, input_payload=input_payload, session_metadata=session_metadata)

    async def screenshot(
        self,
        *,
        target: str | None,
        input_payload: dict[str, Any],
        session_metadata: dict[str, Any] | None = None,
    ) -> BrowserProviderResult:
        """分发 screenshot action。"""

        return await self._dispatch_action("screenshot", target=target, input_payload=input_payload, session_metadata=session_metadata)

    async def get_page_content(
        self,
        *,
        target: str | None,
        input_payload: dict[str, Any],
        session_metadata: dict[str, Any] | None = None,
    ) -> BrowserProviderResult:
        """分发 get_page_content action。"""

        return await self._dispatch_action("get_page_content", target=target, input_payload=input_payload, session_metadata=session_metadata)

    async def _dispatch_action(
        self,
        action_type: str,
        *,
        target: str | None,
        input_payload: dict[str, Any],
        session_metadata: dict[str, Any] | None,
    ) -> BrowserProviderResult:
        """向 worker 分发 action，并写入 worker action 映射。"""

        metadata = session_metadata or {}
        workspace_id = str(input_payload.get("_workspace_id") or "")
        local_action_id = self._parse_uuid(input_payload.get("_local_action_id"))
        worker_id = self._parse_uuid(metadata.get("worker_id"))
        worker_session_id = self._parse_uuid(metadata.get("worker_session_id"))
        remote_session_id = str(metadata.get("remote_session_id") or metadata.get("provider_session_id") or "")
        if not workspace_id or worker_id is None or worker_session_id is None or not remote_session_id:
            return BrowserProviderResult(
                success=False,
                message="Remote browser session metadata is incomplete",
                error="missing worker/session metadata",
                data={"action_type": action_type},
            )

        worker = await self.repository.get_worker(workspace_id=workspace_id, worker_id=worker_id)
        if worker is None:
            return BrowserProviderResult(success=False, message="Browser worker not found", error="worker not found")

        request_payload = {
            "remote_session_id": remote_session_id,
            "action_type": action_type,
            "target": target,
            "input_payload": input_payload,
        }
        worker_action = await self.repository.create_worker_action(
            workspace_id=workspace_id,
            worker_id=worker.id,
            worker_session_id=worker_session_id,
            local_action_id=local_action_id,
            action_type=action_type,
            request_payload=request_payload,
            max_retries=self.settings.browser_action_retry_count,
        )
        started_at = time.perf_counter()
        result = await self.client_factory(worker).execute_action(payload=request_payload)
        duration_ms = max(0, int((time.perf_counter() - started_at) * 1000))
        remote_action_id = result.data.get("remote_action_id")
        if result.success:
            await self.repository.complete_worker_action(
                worker_action,
                remote_action_id=str(remote_action_id) if remote_action_id is not None else None,
                response_payload=result.model_dump(),
                duration_ms=duration_ms,
                retry_count=result.retry_count,
            )
        else:
            await self.repository.fail_worker_action(
                worker_action,
                response_payload=result.model_dump(),
                error=result.error or result.message,
                duration_ms=duration_ms,
                retry_count=result.retry_count,
            )
        data = {
            **result.data,
            "worker_id": str(worker.id),
            "worker_name": worker.worker_name,
            "worker_session_id": str(worker_session_id),
            "remote_session_id": remote_session_id,
            "remote_action_id": str(remote_action_id) if remote_action_id is not None else None,
            "worker_action_id": str(worker_action.id),
            "retry_count": result.retry_count,
            "retry_logs": result.retry_logs,
            "max_retries": self.settings.browser_action_retry_count,
        }
        return BrowserProviderResult(success=result.success, message=result.message, error=result.error, data=data)

    def _default_client_factory(self, worker: BrowserWorker) -> BrowserWorkerClient:
        """创建默认 HTTP client。"""

        return BrowserWorkerClient(
            base_url=worker.base_url,
            timeout_seconds=self.settings.browser_worker_default_timeout_seconds,
            retry_count=self.settings.browser_action_retry_count,
            action_timeout_seconds=self.settings.browser_action_timeout_seconds,
            retry_backoff_seconds=self.settings.browser_action_retry_backoff_seconds,
            worker_id=str(worker.id),
            worker_secret=BrowserWorkerAuthService.get_cached_secret(worker.id),
        )

    def _parse_uuid(self, value: Any) -> UUID | None:
        """宽松解析 UUID。"""

        if value is None or value == "":
            return None
        if isinstance(value, UUID):
            return value
        try:
            return UUID(str(value))
        except Exception:
            logger.warning("Invalid UUID value in remote browser provider", extra={"value": str(value)})
            return None
