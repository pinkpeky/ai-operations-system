"""Phase 34 Remote Browser Runtime provider.

This provider dispatches browser runtime commands to a registered customer
machine worker. It only supports safe runtime primitives: session create,
navigate, screenshot, page content, and close. It intentionally does not
implement stealth, proxy, cookie injection, login persistence, or platform
automation.
"""

from __future__ import annotations

import base64
import logging
import re
import time
from pathlib import Path
from typing import Any, Callable
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.providers.base import BrowserProviderResult
from app.browser.remote.client import BrowserWorkerClient
from app.browser.remote.services.browser_worker_repository import BrowserWorkerRepository
from app.browser.remote.services.browser_worker_selector import BrowserWorkerSelector
from app.browser.remote.services.browser_worker_auth_service import BrowserWorkerAuthService
from app.core.config import Settings
from app.models.browser_runtime import BrowserRuntimeSession
from app.models.browser_worker import BrowserWorker

logger = logging.getLogger(__name__)

BrowserWorkerClientFactory = Callable[[BrowserWorker], BrowserWorkerClient]


class RemoteBrowserProvider:
    """Dispatch Phase 34 browser runtime operations to a remote worker."""

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
        self.screenshot_root = Path(settings.browser_runtime_screenshot_dir)

    async def create_session(
        self,
        *,
        workspace_id: str,
        browser: str = "chromium",
        metadata: dict[str, Any] | None = None,
        worker_id: UUID | None = None,
    ) -> BrowserProviderResult:
        """Select an online worker and create a remote browser runtime session."""

        worker = await self.selector.select_worker(
            workspace_id=workspace_id,
            worker_id=worker_id,
            capabilities={"browser_runtime": True, "browser": browser},
        )
        if worker is None:
            return BrowserProviderResult(
                success=False,
                message="No available remote browser runtime worker",
                error="No online worker with browser_runtime/chromium capability and free session slots",
                data={"workspace_id": workspace_id, "browser": browser},
            )

        payload = {
            "workspace_id": workspace_id,
            "browser": browser,
            "metadata": metadata or {},
        }
        started_at = time.perf_counter()
        result = await self.client_factory(worker).create_runtime_session(payload=payload)
        latency_ms = self._elapsed_ms(started_at)
        if not result.success:
            logger.warning(
                "Remote browser runtime session create failed",
                extra={"workspace_id": workspace_id, "worker_id": str(worker.id), "error": result.error},
            )
            return BrowserProviderResult(
                success=False,
                message=result.message,
                error=result.error,
                data={
                    "workspace_id": workspace_id,
                    "worker_id": str(worker.id),
                    "worker_name": worker.worker_name,
                    "latency_ms": latency_ms,
                    "client_result": result.model_dump(),
                },
            )

        remote_session_id = str(result.data.get("remote_session_id") or result.data.get("session_id") or "")
        if not remote_session_id:
            return BrowserProviderResult(
                success=False,
                message="Remote worker did not return a runtime session id",
                error="remote_session_id missing",
                data={"worker_id": str(worker.id), "client_result": result.model_dump()},
            )

        return BrowserProviderResult(
            success=True,
            message="remote browser runtime session created",
            data={
                **result.data,
                "remote_session_id": remote_session_id,
                "worker_id": str(worker.id),
                "worker_name": worker.worker_name,
                "worker_base_url": worker.base_url,
                "browser": browser,
                "provider": self.provider_name,
                "latency_ms": latency_ms,
            },
        )

    async def navigate(self, *, runtime_session: BrowserRuntimeSession, url: str) -> BrowserProviderResult:
        """Navigate one remote runtime session."""

        return await self._runtime_action(runtime_session, "navigate", {"url": url})

    async def screenshot(
        self,
        *,
        runtime_session: BrowserRuntimeSession,
        full_page: bool = True,
        screenshot_name: str | None = None,
    ) -> BrowserProviderResult:
        """Capture a screenshot and persist the returned bytes on the API server."""

        result = await self._runtime_action(
            runtime_session,
            "screenshot",
            {"full_page": full_page, "screenshot_name": screenshot_name},
        )
        if result.success and result.data.get("screenshot_base64"):
            screenshot_path = self._store_screenshot(
                workspace_id=runtime_session.workspace_id,
                runtime_session_id=runtime_session.id,
                screenshot_base64=str(result.data["screenshot_base64"]),
                screenshot_name=screenshot_name,
            )
            result.data["screenshot_path"] = str(screenshot_path)
        return result

    async def get_page(self, *, runtime_session: BrowserRuntimeSession) -> BrowserProviderResult:
        """Fetch current page title/content."""

        return await self._runtime_action(runtime_session, "get_page", {})

    async def close_session(self, *, runtime_session: BrowserRuntimeSession) -> BrowserProviderResult:
        """Close one remote runtime session."""

        return await self._runtime_action(runtime_session, "close_session", {})

    async def _runtime_action(
        self,
        runtime_session: BrowserRuntimeSession,
        action_type: str,
        payload: dict[str, Any],
    ) -> BrowserProviderResult:
        """Dispatch one runtime action and capture structured retry metadata."""

        metadata = runtime_session.runtime_metadata or {}
        remote_session_id = str(metadata.get("remote_session_id") or "")
        if not remote_session_id:
            return BrowserProviderResult(
                success=False,
                message="Remote runtime session metadata is incomplete",
                error="remote_session_id missing",
                data={"runtime_session_id": str(runtime_session.id), "action_type": action_type},
            )
        worker = await self.repository.get_worker(workspace_id=runtime_session.workspace_id, worker_id=runtime_session.worker_id)
        if worker is None:
            return BrowserProviderResult(success=False, message="Browser worker not found", error="worker not found")

        client = self.client_factory(worker)
        started_at = time.perf_counter()
        if action_type == "navigate":
            client_result = await client.runtime_navigate(remote_session_id=remote_session_id, payload=payload)
        elif action_type == "screenshot":
            client_result = await client.runtime_screenshot(remote_session_id=remote_session_id, payload=payload)
        elif action_type == "get_page":
            client_result = await client.runtime_page(remote_session_id=remote_session_id)
        elif action_type == "close_session":
            client_result = await client.runtime_close(remote_session_id=remote_session_id)
        else:
            return BrowserProviderResult(False, f"Unsupported runtime action: {action_type}", error="unsupported action")
        latency_ms = self._elapsed_ms(started_at)
        data = {
            **client_result.data,
            "worker_id": str(worker.id),
            "worker_name": worker.worker_name,
            "remote_session_id": remote_session_id,
            "runtime_session_id": str(runtime_session.id),
            "action_type": action_type,
            "latency_ms": latency_ms,
            "retry_count": client_result.retry_count,
            "retry_logs": client_result.retry_logs,
        }
        return BrowserProviderResult(
            success=client_result.success,
            message=client_result.message,
            error=client_result.error,
            data=data,
        )

    def _store_screenshot(
        self,
        *,
        workspace_id: str,
        runtime_session_id: UUID,
        screenshot_base64: str,
        screenshot_name: str | None,
    ) -> Path:
        """Store worker-returned screenshot bytes under storage/browser_screenshots."""

        safe_workspace = self._safe_name(workspace_id)
        safe_name = self._safe_name(screenshot_name or f"screenshot-{uuid4()}")
        if not safe_name.endswith(".png"):
            safe_name = f"{safe_name}.png"
        session_dir = (self.screenshot_root / safe_workspace / str(runtime_session_id)).resolve()
        session_dir.mkdir(parents=True, exist_ok=True)
        target_path = (session_dir / safe_name).resolve()
        if not str(target_path).startswith(str(session_dir)):
            raise ValueError("Invalid screenshot path")
        target_path.write_bytes(base64.b64decode(screenshot_base64))
        return target_path

    def _default_client_factory(self, worker: BrowserWorker) -> BrowserWorkerClient:
        """Create the default signed BrowserWorkerClient."""

        return BrowserWorkerClient(
            base_url=worker.base_url,
            timeout_seconds=self.settings.browser_worker_default_timeout_seconds,
            retry_count=self.settings.browser_action_retry_count,
            action_timeout_seconds=self.settings.browser_action_timeout_seconds,
            retry_backoff_seconds=self.settings.browser_action_retry_backoff_seconds,
            worker_id=str(worker.id),
            worker_secret=BrowserWorkerAuthService.get_cached_secret(worker.id),
        )

    def _safe_name(self, value: str) -> str:
        """Return a filesystem-safe path segment."""

        return re.sub(r"[^a-zA-Z0-9_.-]", "-", value).strip("-") or "item"

    def _elapsed_ms(self, started_at: float) -> int:
        """Return elapsed milliseconds."""

        return max(0, int((time.perf_counter() - started_at) * 1000))
