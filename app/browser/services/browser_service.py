"""Browser Adapter 服务层。

该服务负责 provider 选择、workspace 校验、数据持久化和结构化可观测记录。
Phase 17 默认使用 MockBrowserProvider，不运行真实浏览器。
"""

from __future__ import annotations

import logging
import time
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.providers import (
    BaseBrowserProvider,
    BrowserProviderResult,
    MockBrowserProvider,
    PlaywrightBrowserProvider,
    PlaywrightLocalProvider,
    RemoteBrowserProvider,
)
from app.browser.repositories import BrowserRepository
from app.browser.services.browser_action_policy_service import BrowserActionPolicyService
from app.browser.services.browser_profile_health_service import BrowserProfileHealthService
from app.browser.services.browser_profile_service import BrowserProfileService
from app.core.config import Settings, get_settings
from app.models.browser import BrowserAction, BrowserActionLog, BrowserSession
from app.models.enums import BrowserSessionStatus

logger = logging.getLogger(__name__)


class BrowserService:
    """按 workspace 隔离的 Browser Adapter 服务。"""

    def __init__(
        self,
        session: AsyncSession,
        *,
        settings: Settings | None = None,
        provider: BaseBrowserProvider | None = None,
    ) -> None:
        self.session = session
        self.settings = settings or get_settings()
        self.repository = BrowserRepository(session)
        self.provider = provider or self._build_provider()

    async def create_browser_session(
        self,
        *,
        workspace_id: str,
        user_id: str | None = None,
        metadata: dict[str, Any] | None = None,
        profile_id: UUID | None = None,
        use_persistent_profile: bool = False,
    ) -> BrowserSession:
        """创建 browser session 记录和 provider 侧占位 session。"""

        started_at = time.perf_counter()
        profile_service = BrowserProfileService(self.session, settings=self.settings)
        profile = None
        if use_persistent_profile:
            if profile_id is None:
                raise ValueError("profile_id is required when use_persistent_profile=true")
            profile = await profile_service.get_profile(workspace_id=workspace_id, profile_id=profile_id)
            if profile is None:
                raise ValueError("Browser profile not found")

        browser_session = await self.repository.create_session(
            workspace_id=workspace_id,
            user_id=user_id,
            provider=self.provider.provider_name,
            metadata=metadata or {},
            profile_id=profile.id if profile is not None else None,
            profile_path=profile.profile_path if profile is not None else None,
            persistent_context_enabled=use_persistent_profile,
        )
        await self.session.flush()
        if profile is not None:
            await profile_service.lock_profile(workspace_id=workspace_id, profile_id=profile.id, session_id=browser_session.id)

        provider_metadata = {
            **(metadata or {}),
            "workspace_id": workspace_id,
            "session_id": str(browser_session.id),
            "profile_id": str(profile.id) if profile is not None else None,
            "profile_path": profile.profile_path if profile is not None else None,
            "use_persistent_profile": use_persistent_profile,
        }
        provider_result = await self.provider.create_session(
            metadata=provider_metadata,
        )
        if profile is not None and not provider_result.success:
            await profile_service.release_profile(workspace_id=workspace_id, profile_id=profile.id, session_id=browser_session.id)
            await BrowserProfileHealthService(self.session, settings=self.settings).mark_profile_warning(
                workspace_id=workspace_id,
                profile_id=profile.id,
                error=provider_result.error or provider_result.message,
            )
        if profile is not None and provider_result.success:
            await BrowserProfileHealthService(self.session, settings=self.settings).increment_usage_count(
                workspace_id=workspace_id,
                profile_id=profile.id,
                session_id=browser_session.id,
            )
        status = BrowserSessionStatus.ACTIVE.value if provider_result.success else BrowserSessionStatus.FAILED.value
        provider_session_metadata = dict(provider_result.data.get("provider_session_metadata") or {})
        if provider_result.data.get("provider_session_id") and "provider_session_id" not in provider_session_metadata:
            provider_session_metadata["provider_session_id"] = provider_result.data.get("provider_session_id")
        await self.repository.update_session_status(
            browser_session=browser_session,
            status=status,
            browser_id=provider_result.data.get("browser_id"),
            page_id=provider_result.data.get("page_id"),
            provider_session_metadata=provider_session_metadata,
            metadata_patch={
                "provider_result": provider_result.model_dump(),
                "provider_session_id": provider_result.data.get("provider_session_id"),
                "browser_id": provider_result.data.get("browser_id"),
                "page_id": provider_result.data.get("page_id"),
                "profile_id": str(profile.id) if profile is not None else None,
                "profile_path": profile.profile_path if profile is not None else None,
                "persistent_context_enabled": use_persistent_profile,
            },
        )
        await self.repository.create_log(
            workspace_id=workspace_id,
            session_id=browser_session.id,
            action_id=None,
            level="info" if provider_result.success else "error",
            message=provider_result.message,
            metadata={
                "provider": self.provider.provider_name,
                "latency_ms": self._elapsed_ms(started_at),
                "success": provider_result.success,
                "error": provider_result.error,
                "profile_id": str(profile.id) if profile is not None else None,
                "profile_path": profile.profile_path if profile is not None else None,
            },
        )
        await self.session.commit()
        await self.session.refresh(browser_session)
        logger.info(
            "Browser session created",
            extra={"workspace_id": workspace_id, "session_id": str(browser_session.id), "provider": self.provider.provider_name},
        )
        return browser_session

    async def execute_action(
        self,
        *,
        workspace_id: str,
        session_id: UUID,
        action_type: str,
        target: str | None = None,
        input_payload: dict[str, Any] | None = None,
    ) -> BrowserAction:
        """执行 browser action，并写入状态与日志。"""

        browser_session = await self.repository.get_session(session_id=session_id, workspace_id=workspace_id)
        if browser_session is None:
            raise ValueError("Browser session not found")
        if browser_session.status != BrowserSessionStatus.ACTIVE.value:
            raise ValueError(f"Browser session is not active: {browser_session.status}")

        payload = input_payload or {}
        selector = payload.get("selector") if isinstance(payload.get("selector"), str) else None
        if action_type in {"click", "type_text"} and selector is None:
            selector = target
        target_url = target if action_type == "navigate" else None
        action = await self.repository.create_action(
            workspace_id=workspace_id,
            session_id=session_id,
            action_type=action_type,
            target=target,
            input_payload=payload,
            selector=selector,
            target_url=target_url,
        )
        policy_result = await BrowserActionPolicyService(self.session, settings=self.settings).check_action_policy(
            workspace_id=workspace_id,
            browser_session=browser_session,
            action_type=action_type,
            target=target,
            input_payload=payload,
        )
        if not policy_result.allowed:
            await self.repository.fail_action(action, error=policy_result.reason or "action blocked by policy", duration_ms=0)
            await self.repository.create_log(
                workspace_id=workspace_id,
                session_id=session_id,
                action_id=action.id,
                level="warning",
                message="Browser action blocked by policy",
                metadata={
                    "provider": self.provider.provider_name,
                    "action_type": action_type,
                    "target": target,
                    "reason": policy_result.reason,
                    "policy_metadata": policy_result.metadata or {},
                },
            )
            await self.session.commit()
            await self.session.refresh(action)
            return action
        await self.repository.mark_action_running(action)
        await self.repository.create_log(
            workspace_id=workspace_id,
            session_id=session_id,
            action_id=action.id,
            level="info",
            message=f"Browser action started: {action_type}",
            metadata={"provider": self.provider.provider_name, "action_type": action_type, "target": target},
        )
        await self.session.flush()

        started_at = time.perf_counter()
        try:
            provider_payload = {
                **payload,
                "_workspace_id": workspace_id,
                "_session_id": str(session_id),
                "_local_action_id": str(action.id),
            }
            provider_result = await self._call_provider_action(
                action_type=action_type,
                target=target,
                input_payload=provider_payload,
                session_metadata=browser_session.provider_session_metadata or {},
            )
            duration_ms = self._elapsed_ms(started_at)
            output = provider_result.model_dump()
            data = provider_result.data or {}
            if provider_result.success:
                await self.repository.complete_action(
                    action,
                    output_payload=output,
                    duration_ms=duration_ms,
                    selector=data.get("selector") or selector,
                    target_url=data.get("target_url") or target_url,
                    screenshot_path=data.get("screenshot_path"),
                    page_title=data.get("page_title"),
                )
                await self.repository.create_log(
                    workspace_id=workspace_id,
                    session_id=session_id,
                    action_id=action.id,
                    level="info",
                    message=provider_result.message,
                    metadata={
                        "provider": self.provider.provider_name,
                        "action_type": action_type,
                        "latency_ms": duration_ms,
                        "success": True,
                        "error": None,
                        "screenshot_path": data.get("screenshot_path"),
                        "worker_id": data.get("worker_id"),
                        "worker_name": data.get("worker_name"),
                        "remote_action_id": data.get("remote_action_id"),
                    },
                )
            else:
                await self.repository.fail_action(
                    action,
                    error=provider_result.error or provider_result.message,
                    duration_ms=duration_ms,
                    screenshot_path=data.get("screenshot_path"),
                    page_title=data.get("page_title"),
                )
                action.output_payload = output
                await self.repository.create_log(
                    workspace_id=workspace_id,
                    session_id=session_id,
                    action_id=action.id,
                    level="error",
                    message=provider_result.message,
                    metadata={
                        "provider": self.provider.provider_name,
                        "action_type": action_type,
                        "latency_ms": duration_ms,
                        "success": False,
                        "error": provider_result.error,
                        "screenshot_path": data.get("screenshot_path"),
                        "worker_id": data.get("worker_id"),
                        "worker_name": data.get("worker_name"),
                        "remote_action_id": data.get("remote_action_id"),
                    },
                )
            await self.session.commit()
            await self.session.refresh(action)
            return action
        except Exception as exc:
            duration_ms = self._elapsed_ms(started_at)
            await self.repository.fail_action(action, error=str(exc), duration_ms=duration_ms)
            await self.repository.create_log(
                workspace_id=workspace_id,
                session_id=session_id,
                action_id=action.id,
                level="error",
                message=f"Browser action failed: {action_type}",
                metadata={
                    "provider": self.provider.provider_name,
                    "action_type": action_type,
                    "latency_ms": duration_ms,
                    "success": False,
                    "error": str(exc),
                },
            )
            await self.session.commit()
            await self.session.refresh(action)
            logger.exception(
                "Browser action failed",
                extra={"workspace_id": workspace_id, "session_id": str(session_id), "action_type": action_type},
            )
            return action

    async def close_browser_session(self, *, workspace_id: str, session_id: UUID) -> BrowserSession:
        """关闭 browser session。"""

        browser_session = await self.repository.get_session(session_id=session_id, workspace_id=workspace_id)
        if browser_session is None:
            raise ValueError("Browser session not found")
        provider_session_id = str((browser_session.provider_session_metadata or {}).get("provider_session_id") or "")
        started_at = time.perf_counter()
        provider_result = await self.provider.close_session(provider_session_id=provider_session_id or None)
        status = BrowserSessionStatus.CLOSED.value if provider_result.success else BrowserSessionStatus.FAILED.value
        await self.repository.update_session_status(
            browser_session=browser_session,
            status=status,
            metadata_patch={"close_result": provider_result.model_dump()},
        )
        await self.repository.create_log(
            workspace_id=workspace_id,
            session_id=session_id,
            action_id=None,
            level="info" if provider_result.success else "error",
            message=provider_result.message,
            metadata={
                "provider": self.provider.provider_name,
                "latency_ms": self._elapsed_ms(started_at),
                "success": provider_result.success,
                "error": provider_result.error,
                "profile_id": str(browser_session.profile_id) if browser_session.profile_id is not None else None,
            },
        )
        if browser_session.profile_id is not None and browser_session.persistent_context_enabled:
            await BrowserProfileHealthService(self.session, settings=self.settings).record_usage(
                workspace_id=workspace_id,
                profile_id=browser_session.profile_id,
                session_id=session_id,
                action="session_close",
                success=provider_result.success,
                error=provider_result.error,
                metadata={"provider": self.provider.provider_name},
            )
            await BrowserProfileService(self.session, settings=self.settings).release_profile(
                workspace_id=workspace_id,
                profile_id=browser_session.profile_id,
                session_id=session_id,
            )
        await self.session.commit()
        await self.session.refresh(browser_session)
        return browser_session

    async def list_sessions(self, *, workspace_id: str, status: str | None = None, limit: int = 100) -> list[BrowserSession]:
        """列出当前 workspace 的 browser sessions。"""

        return await self.repository.list_sessions(workspace_id=workspace_id, status=status, limit=limit)

    async def list_actions(self, *, workspace_id: str, session_id: UUID, limit: int = 100) -> list[BrowserAction]:
        """列出指定 session 的 browser actions。"""

        if await self.repository.get_session(session_id=session_id, workspace_id=workspace_id) is None:
            raise ValueError("Browser session not found")
        return await self.repository.list_actions(workspace_id=workspace_id, session_id=session_id, limit=limit)

    async def list_logs(self, *, workspace_id: str, session_id: UUID, limit: int = 100) -> list[BrowserActionLog]:
        """列出指定 session 的 browser logs。"""

        if await self.repository.get_session(session_id=session_id, workspace_id=workspace_id) is None:
            raise ValueError("Browser session not found")
        return await self.repository.list_logs(workspace_id=workspace_id, session_id=session_id, limit=limit)

    def _build_provider(self) -> BaseBrowserProvider:
        """根据配置构建 browser provider。"""

        provider_name = str(getattr(self.settings, "browser_provider", "mock")).lower()
        if provider_name == "mock":
            return MockBrowserProvider()
        if provider_name == "playwright_local":
            return PlaywrightLocalProvider(
                timeout_seconds=self.settings.browser_timeout_seconds,
                browser_type=self.settings.browser_type,
                headless=self.settings.browser_headless,
                viewport={
                    "width": self.settings.browser_viewport_width,
                    "height": self.settings.browser_viewport_height,
                },
                screenshot_dir=self.settings.browser_screenshot_dir,
            )
        if provider_name == "playwright":
            return PlaywrightBrowserProvider()
        if provider_name == "remote":
            return RemoteBrowserProvider(session=self.session, settings=self.settings)
        raise ValueError(f"Unsupported browser provider: {provider_name}")

    async def _call_provider_action(
        self,
        *,
        action_type: str,
        target: str | None,
        input_payload: dict[str, Any],
        session_metadata: dict[str, Any] | None,
    ) -> BrowserProviderResult:
        """把单个 browser action 分发给当前 provider。"""

        action_map = {
            "navigate": self.provider.navigate,
            "click": self.provider.click,
            "type_text": self.provider.type_text,
            "scroll": self.provider.scroll,
            "screenshot": self.provider.screenshot,
            "get_page_content": self.provider.get_page_content,
        }
        handler = action_map.get(action_type)
        if handler is None:
            raise ValueError(f"Unsupported browser action_type: {action_type}")
        return await handler(target=target, input_payload=input_payload, session_metadata=session_metadata)

    def _elapsed_ms(self, started_at: float) -> int:
        """返回可观测用耗时毫秒。"""

        return max(0, int((time.perf_counter() - started_at) * 1000))
