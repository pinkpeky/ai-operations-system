"""Playwright based Browser Worker runtime。

该 runtime 是 Phase 20 的真实 worker 基础能力。它只支持受控的 chromium/headless
动作，不实现登录、社媒自动化、Cookie 注入、代理池、指纹绕过或验证码处理。
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from uuid import uuid4

from worker.browser_worker.config import WorkerSettings
from worker.browser_worker.runtime import BaseBrowserWorkerRuntime
from worker.browser_worker.schemas import WorkerActionResponse, WorkerHumanControlResponse, WorkerSessionResponse


@dataclass(slots=True)
class PlaywrightWorkerSession:
    """Worker 进程内 Playwright session。"""

    playwright: Any
    browser: Any | None
    context: Any
    page: Any
    metadata: dict[str, Any]


class PlaywrightBrowserWorkerRuntime(BaseBrowserWorkerRuntime):
    """独立 worker 内的 Playwright Chromium runtime。"""

    def __init__(self, settings: WorkerSettings) -> None:
        self.settings = settings
        self.timeout_ms = int(settings.worker_timeout_seconds * 1000)
        self.viewport = {"width": settings.worker_viewport_width, "height": settings.worker_viewport_height}
        self.screenshot_dir = Path(settings.worker_screenshot_dir)
        self.profile_dir = Path(settings.worker_profile_dir)
        self.sessions: dict[str, PlaywrightWorkerSession] = {}
        self.human_controls: dict[str, dict[str, Any]] = {}

    async def create_session(
        self,
        *,
        workspace_id: str | None,
        local_browser_session_id: str | None,
        metadata: dict[str, Any],
        profile_id: str | None = None,
        profile_path: str | None = None,
        use_persistent_profile: bool = False,
    ) -> WorkerSessionResponse:
        """启动一个独立 Chromium session。"""

        started_at = time.perf_counter()
        playwright: Any | None = None
        try:
            from playwright.async_api import async_playwright
        except Exception as exc:
            return WorkerSessionResponse(success=False, message="Playwright import failed", error=str(exc))

        try:
            browser_type = self.settings.worker_browser_type.lower()
            if browser_type != "chromium":
                raise ValueError("Browser worker only supports chromium")
            playwright = await async_playwright().start()
            persistent_context_enabled = bool(use_persistent_profile and profile_id)
            worker_profile_path: Path | None = None
            if persistent_context_enabled:
                worker_profile_path = self._profile_path(
                    workspace_id=workspace_id,
                    profile_id=str(profile_id),
                    profile_path=profile_path,
                )
                worker_profile_path.mkdir(parents=True, exist_ok=True)
                if not worker_profile_path.exists() or not worker_profile_path.is_dir():
                    raise RuntimeError("profile path validation failed")
                browser = None
                context = await playwright.chromium.launch_persistent_context(
                    user_data_dir=str(worker_profile_path),
                    headless=self.settings.worker_headless,
                    viewport=self.viewport,
                    args=["--no-sandbox"],
                )
                page = context.pages[0] if getattr(context, "pages", []) else await context.new_page()
            else:
                browser = await playwright.chromium.launch(headless=self.settings.worker_headless, args=["--no-sandbox"])
                context = await browser.new_context(viewport=self.viewport)
                page = await context.new_page()
            remote_session_id = f"worker-session-{uuid4()}"
            session_metadata = {
                **metadata,
                "workspace_id": workspace_id,
                "local_browser_session_id": local_browser_session_id,
                "profile_id": profile_id,
                "profile_path": str(worker_profile_path) if worker_profile_path is not None else profile_path,
                "persistent_context_enabled": persistent_context_enabled,
                "browser_type": browser_type,
                "headless": self.settings.worker_headless,
                "viewport": self.viewport,
                "started_at": datetime.now(UTC).isoformat(),
                "profile_startup_latency_ms": self._elapsed_ms(started_at),
            }
            self.sessions[remote_session_id] = PlaywrightWorkerSession(
                playwright=playwright,
                browser=browser,
                context=context,
                page=page,
                metadata=session_metadata,
            )
            return WorkerSessionResponse(
                success=True,
                remote_session_id=remote_session_id,
                message="browser worker session created",
                data={
                    "remote_session_id": remote_session_id,
                    "profile_id": profile_id,
                    "profile_path": session_metadata.get("profile_path"),
                    "persistent_context_enabled": persistent_context_enabled,
                    "profile_startup_latency_ms": session_metadata.get("profile_startup_latency_ms"),
                    "metadata": session_metadata,
                },
            )
        except Exception as exc:
            if playwright is not None:
                try:
                    await playwright.stop()
                except Exception:
                    pass
            return WorkerSessionResponse(
                success=False,
                message="browser worker session create failed",
                error=str(exc),
                data={
                    "profile_id": profile_id,
                    "profile_path": profile_path,
                    "persistent_context_enabled": bool(use_persistent_profile and profile_id),
                    "profile_startup_latency_ms": self._elapsed_ms(started_at),
                },
            )

    async def close_session(self, *, remote_session_id: str) -> WorkerSessionResponse:
        """关闭指定 session。"""

        session = self.sessions.pop(remote_session_id, None)
        self.human_controls.pop(remote_session_id, None)
        if session is None:
            return WorkerSessionResponse(success=False, remote_session_id=remote_session_id, message="session not found", error="session not found")
        errors: list[str] = []
        closers = [session.context.close]
        if session.browser is not None:
            closers.append(session.browser.close)
        closers.append(session.playwright.stop)
        for closer in closers:
            try:
                await closer()
            except Exception as exc:
                errors.append(str(exc))
        return WorkerSessionResponse(
            success=not errors,
            remote_session_id=remote_session_id,
            message="browser worker session closed" if not errors else "browser worker session closed with errors",
            data={"remote_session_id": remote_session_id},
            error="; ".join(errors) if errors else None,
        )

    async def execute_action(
        self,
        *,
        remote_session_id: str,
        action_type: str,
        target: str | None,
        input_payload: dict[str, Any],
    ) -> WorkerActionResponse:
        """执行基础 browser action。"""

        session = self.sessions.get(remote_session_id)
        if session is None:
            return WorkerActionResponse(success=False, message="session not found", error="session not found")
        remote_action_id = f"worker-action-{uuid4()}"
        try:
            data = await self._dispatch(session=session, action_type=action_type, target=target, input_payload=input_payload)
            data.update({"remote_session_id": remote_session_id, "remote_action_id": remote_action_id, "action_type": action_type})
            return WorkerActionResponse(
                success=True,
                remote_action_id=remote_action_id,
                message=f"browser worker {action_type} success",
                data=data,
            )
        except Exception as exc:
            return WorkerActionResponse(
                success=False,
                remote_action_id=remote_action_id,
                message=f"browser worker {action_type} failed",
                error=str(exc),
                data={"remote_session_id": remote_session_id, "remote_action_id": remote_action_id, "action_type": action_type},
            )

    async def close_all(self) -> None:
        """关闭所有 session，供 FastAPI shutdown 使用。"""

        for remote_session_id in list(self.sessions.keys()):
            await self.close_session(remote_session_id=remote_session_id)

    async def start_human_control(
        self,
        *,
        remote_session_id: str,
        control_session_id: str | None,
        payload: dict[str, Any],
    ) -> WorkerHumanControlResponse:
        """进入人工接管 metadata 状态，不暴露真实远程 UI。"""

        session = self.sessions.get(remote_session_id)
        if session is None:
            return WorkerHumanControlResponse(
                success=False,
                remote_session_id=remote_session_id,
                status="failed",
                message="session not found",
                error="session not found",
            )
        metadata = {
            "status": "active",
            "control_session_id": control_session_id,
            "started_at": datetime.now(UTC).isoformat(),
            "payload": payload,
        }
        self.human_controls[remote_session_id] = metadata
        session.metadata["human_control"] = metadata
        return WorkerHumanControlResponse(
            success=True,
            remote_session_id=remote_session_id,
            status="active",
            message="human control started",
            data=metadata,
        )

    async def complete_human_control(
        self,
        *,
        remote_session_id: str,
        control_session_id: str | None,
        note: str | None,
        payload: dict[str, Any],
    ) -> WorkerHumanControlResponse:
        """结束人工接管 metadata 状态。"""

        session = self.sessions.get(remote_session_id)
        if session is None:
            return WorkerHumanControlResponse(
                success=False,
                remote_session_id=remote_session_id,
                status="failed",
                message="session not found",
                error="session not found",
            )
        metadata = self.human_controls.get(remote_session_id, {})
        metadata = {
            **metadata,
            "status": "completed",
            "control_session_id": control_session_id or metadata.get("control_session_id"),
            "completed_at": datetime.now(UTC).isoformat(),
            "note": note,
            "payload": payload,
        }
        self.human_controls[remote_session_id] = metadata
        session.metadata["human_control"] = metadata
        return WorkerHumanControlResponse(
            success=True,
            remote_session_id=remote_session_id,
            status="completed",
            message="human control completed",
            data=metadata,
        )

    async def get_human_control_status(self, *, remote_session_id: str) -> WorkerHumanControlResponse:
        """查询人工接管 metadata 状态。"""

        if remote_session_id not in self.sessions:
            return WorkerHumanControlResponse(
                success=False,
                remote_session_id=remote_session_id,
                status="failed",
                message="session not found",
                error="session not found",
            )
        metadata = self.human_controls.get(remote_session_id, {"status": "inactive"})
        return WorkerHumanControlResponse(
            success=True,
            remote_session_id=remote_session_id,
            status=str(metadata.get("status") or "inactive"),
            message="human control status",
            data=metadata,
        )

    async def _dispatch(
        self,
        *,
        session: PlaywrightWorkerSession,
        action_type: str,
        target: str | None,
        input_payload: dict[str, Any],
    ) -> dict[str, Any]:
        """分发单个 browser action。"""

        page = session.page
        if action_type == "navigate":
            if not target:
                raise ValueError("navigate target is required")
            self._ensure_safe_url(target)
            await page.goto(target, timeout=self.timeout_ms, wait_until="domcontentloaded")
            return {"target_url": target, "page_title": await page.title()}
        if action_type == "click":
            selector = self._selector(target=target, input_payload=input_payload)
            await page.click(selector, timeout=self.timeout_ms)
            return {"selector": selector, "page_title": await page.title()}
        if action_type == "type_text":
            selector = self._selector(target=target, input_payload=input_payload)
            text = str(input_payload.get("text") or "")
            await page.fill(selector, text, timeout=self.timeout_ms)
            return {"selector": selector, "text_length": len(text), "page_title": await page.title()}
        if action_type == "scroll":
            x = int(input_payload.get("x", 0))
            y = int(input_payload.get("y", 800))
            await page.mouse.wheel(x, y)
            return {"scroll": {"x": x, "y": y}, "page_title": await page.title()}
        if action_type == "screenshot":
            screenshot_path = self._screenshot_path(session=session, input_payload=input_payload)
            screenshot_path.parent.mkdir(parents=True, exist_ok=True)
            await page.screenshot(path=str(screenshot_path), full_page=bool(input_payload.get("full_page", True)))
            return {"screenshot_path": str(screenshot_path), "page_title": await page.title()}
        if action_type == "get_page_content":
            return {"content": await page.content(), "page_title": await page.title()}
        raise ValueError(f"Unsupported browser worker action_type: {action_type}")

    def _selector(self, *, target: str | None, input_payload: dict[str, Any]) -> str:
        """解析 selector。"""

        selector = input_payload.get("selector") or target
        if not selector:
            raise ValueError("selector is required")
        return str(selector)

    def _screenshot_path(self, *, session: PlaywrightWorkerSession, input_payload: dict[str, Any]) -> Path:
        """生成截图路径。"""

        workspace_id = self._safe_name(str(session.metadata.get("workspace_id") or "default-workspace"))
        remote_session_id = self._safe_name(str(next(key for key, value in self.sessions.items() if value is session)))
        name = self._safe_name(str(input_payload.get("screenshot_name") or f"screenshot-{uuid4()}"))
        if not name.endswith(".png"):
            name = f"{name}.png"
        return self.screenshot_dir / workspace_id / remote_session_id / name

    def _profile_path(self, *, workspace_id: str | None, profile_id: str, profile_path: str | None) -> Path:
        """生成 worker/profiles/{workspace_id}/{profile_id} 持久化目录。"""

        safe_workspace_id = self._safe_name(str(workspace_id or "default-workspace"))
        safe_profile_id = self._safe_name(profile_id)
        expected_path = (self.profile_dir / safe_workspace_id / safe_profile_id).resolve()
        if profile_path:
            candidate = Path(profile_path)
            if not candidate.is_absolute():
                candidate = Path.cwd() / candidate
            try:
                profile_root = self.profile_dir.resolve()
                candidate_resolved = candidate.resolve()
                if str(candidate_resolved).startswith(str(profile_root)):
                    return candidate_resolved
            except Exception:
                pass
        return expected_path

    def _safe_name(self, value: str) -> str:
        """生成安全文件名片段。"""

        return re.sub(r"[^a-zA-Z0-9_.-]", "-", value).strip("-") or "item"

    def _elapsed_ms(self, started_at: float) -> int:
        """返回启动耗时毫秒。"""

        return max(0, int((time.perf_counter() - started_at) * 1000))

    def _ensure_safe_url(self, url: str) -> None:
        """基础安全边界：只允许 example.com、本地测试页面和静态文件。"""

        parsed = urlparse(url)
        hostname = (parsed.hostname or "").lower()
        if parsed.scheme == "file":
            return
        if parsed.scheme not in {"http", "https"}:
            raise ValueError("Only http, https, and file URLs are allowed")
        if hostname == "example.com" or hostname.endswith(".example.com"):
            return
        if hostname in {"localhost", "127.0.0.1", "0.0.0.0", "::1"}:
            return
        raise ValueError("Browser worker only allows example.com, local test pages, or static file URLs")
