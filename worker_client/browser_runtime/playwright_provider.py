"""Playwright implementation for the customer-machine Browser Runtime."""

from __future__ import annotations

import base64
import os
import re
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from uuid import uuid4

from worker_client.browser_runtime.schemas import (
    BrowserRuntimeActionResponse,
    BrowserRuntimeCreateSessionRequest,
    BrowserRuntimePageResponse,
    BrowserRuntimeScreenshotRequest,
    BrowserRuntimeSessionResponse,
)
from worker_client.browser_runtime.session_manager import BrowserRuntimeSessionManager, BrowserRuntimeSessionRecord


class PlaywrightBrowserRuntimeProvider:
    """Small Playwright Chromium runtime used by customer-machine workers."""

    def __init__(
        self,
        *,
        timeout_seconds: float = 30.0,
        headless: bool = False,
        viewport: dict[str, int] | None = None,
        screenshot_dir: str = "worker/screenshots",
        profile_dir: str = "worker/profiles",
        session_manager: BrowserRuntimeSessionManager | None = None,
        browser_executable_path: str | None = None,
    ) -> None:
        self.timeout_ms = int(timeout_seconds * 1000)
        self.headless = headless
        self.viewport = viewport or {"width": 1280, "height": 720}
        self.screenshot_dir = Path(screenshot_dir)
        self.profile_dir = Path(profile_dir)
        self.sessions = session_manager or BrowserRuntimeSessionManager()
        self.browser_executable_path = browser_executable_path or self._discover_browser_executable_path()

    async def create_session(self, request: BrowserRuntimeCreateSessionRequest) -> BrowserRuntimeSessionResponse:
        """Create a Chromium session, optionally using a persistent context."""

        started_at = time.perf_counter()
        playwright: Any | None = None
        try:
            from playwright.async_api import async_playwright
        except Exception as exc:
            return BrowserRuntimeSessionResponse(success=False, message="Playwright import failed", error=str(exc))

        try:
            if request.browser != "chromium":
                raise ValueError("Browser runtime only supports chromium")
            playwright = await async_playwright().start()
            persistent = bool(request.use_persistent_context or request.profile_id)
            profile_path: Path | None = None
            if persistent:
                profile_path = self._profile_path(
                    workspace_id=request.workspace_id,
                    profile_id=request.profile_id or f"profile-{uuid4()}",
                    profile_path=request.profile_path,
                )
                profile_path.mkdir(parents=True, exist_ok=True)
                browser_instance = None
                context = await playwright.chromium.launch_persistent_context(
                    user_data_dir=str(profile_path),
                    viewport=self.viewport,
                    **self._launch_options(),
                )
                page = context.pages[0] if getattr(context, "pages", []) else await context.new_page()
            else:
                browser_instance = await playwright.chromium.launch(**self._launch_options())
                context = await browser_instance.new_context(viewport=self.viewport)
                page = await context.new_page()
            session_id = f"browser-runtime-session-{uuid4()}"
            metadata = {
                **request.metadata,
                "workspace_id": request.workspace_id,
                "browser": request.browser,
                "headless": self.headless,
                "viewport": self.viewport,
                "persistent_context_enabled": persistent,
                "profile_id": request.profile_id,
                "profile_path": str(profile_path) if profile_path is not None else request.profile_path,
                "browser_executable_path": self.browser_executable_path,
                "started_at": datetime.now(UTC).isoformat(),
                "startup_latency_ms": self._elapsed_ms(started_at),
            }
            record = BrowserRuntimeSessionRecord(
                session_id=session_id,
                workspace_id=request.workspace_id,
                browser=request.browser,
                playwright=playwright,
                browser_instance=browser_instance,
                context=context,
                page=page,
                metadata=metadata,
            )
            self.sessions.add(record)
            return BrowserRuntimeSessionResponse(
                success=True,
                remote_session_id=session_id,
                session_id=session_id,
                message="browser runtime session created",
                data={"remote_session_id": session_id, "session_id": session_id, **metadata},
            )
        except Exception as exc:
            if playwright is not None:
                try:
                    await playwright.stop()
                except Exception:
                    pass
            return BrowserRuntimeSessionResponse(
                success=False,
                message="browser runtime session create failed",
                error=str(exc),
                data={"startup_latency_ms": self._elapsed_ms(started_at)},
            )

    async def navigate(self, *, session_id: str, url: str) -> BrowserRuntimeActionResponse:
        """Navigate an existing session."""

        record = self._require_session(session_id)
        self._ensure_safe_url(url)
        started_at = time.perf_counter()
        try:
            await record.page.goto(url, timeout=self.timeout_ms, wait_until="domcontentloaded")
            title = await record.page.title()
            record.current_url = url
            record.page_title = title
            self.sessions.touch(record)
            return BrowserRuntimeActionResponse(
                success=True,
                remote_action_id=f"browser-runtime-action-{uuid4()}",
                message="browser runtime navigate success",
                data={
                    "remote_session_id": session_id,
                    "target_url": url,
                    "current_url": url,
                    "page_title": title,
                    "duration_ms": self._elapsed_ms(started_at),
                },
            )
        except Exception as exc:
            return BrowserRuntimeActionResponse(
                success=False,
                message="browser runtime navigate failed",
                error=str(exc),
                data={"remote_session_id": session_id, "duration_ms": self._elapsed_ms(started_at)},
            )

    async def screenshot(self, *, session_id: str, request: BrowserRuntimeScreenshotRequest) -> BrowserRuntimeActionResponse:
        """Capture a screenshot and return base64 so the API server can store it."""

        record = self._require_session(session_id)
        started_at = time.perf_counter()
        try:
            screenshot_bytes = await self._screenshot_bytes(record=record, request=request)
            encoded = base64.b64encode(screenshot_bytes).decode("ascii")
            title = await record.page.title()
            self.sessions.touch(record)
            return BrowserRuntimeActionResponse(
                success=True,
                remote_action_id=f"browser-runtime-action-{uuid4()}",
                message="browser runtime screenshot success",
                data={
                    "remote_session_id": session_id,
                    "screenshot_base64": encoded,
                    "page_title": title,
                    "current_url": record.current_url,
                    "duration_ms": self._elapsed_ms(started_at),
                },
            )
        except Exception as exc:
            return BrowserRuntimeActionResponse(
                success=False,
                message="browser runtime screenshot failed",
                error=str(exc),
                data={"remote_session_id": session_id, "duration_ms": self._elapsed_ms(started_at)},
            )

    async def get_page(self, *, session_id: str) -> BrowserRuntimePageResponse:
        """Return current page title/content."""

        record = self._require_session(session_id)
        try:
            title = await record.page.title()
            content = await record.page.content()
            record.page_title = title
            self.sessions.touch(record)
            return BrowserRuntimePageResponse(
                success=True,
                message="browser runtime page fetched",
                title=title,
                url=record.current_url,
                content=content,
                data={"remote_session_id": session_id, "page_title": title, "current_url": record.current_url},
            )
        except Exception as exc:
            return BrowserRuntimePageResponse(success=False, message="browser runtime page failed", error=str(exc))

    async def close_session(self, *, session_id: str) -> BrowserRuntimeSessionResponse:
        """Close context/browser/playwright and remove the in-memory session."""

        record = self.sessions.remove(session_id)
        if record is None:
            return BrowserRuntimeSessionResponse(success=False, remote_session_id=session_id, message="session not found", error="session not found")
        errors: list[str] = []
        for closer in [record.context.close, record.browser_instance.close if record.browser_instance is not None else None, record.playwright.stop]:
            if closer is None:
                continue
            try:
                await closer()
            except Exception as exc:
                errors.append(str(exc))
        return BrowserRuntimeSessionResponse(
            success=not errors,
            remote_session_id=session_id,
            session_id=session_id,
            message="browser runtime session closed" if not errors else "browser runtime session closed with errors",
            data={"remote_session_id": session_id, "errors": errors},
            error="; ".join(errors) if errors else None,
        )

    async def close_all(self) -> None:
        """Close all process-local sessions."""

        for session_id in list(self.sessions.sessions.keys()):
            await self.close_session(session_id=session_id)

    def _launch_options(self) -> dict[str, Any]:
        options: dict[str, Any] = {"headless": self.headless, "args": ["--no-sandbox"]}
        if self.browser_executable_path:
            options["executable_path"] = self.browser_executable_path
        return options

    @staticmethod
    def _discover_browser_executable_path() -> str | None:
        for env_name in (
            "WORKER_CLIENT_BROWSER_EXECUTABLE_PATH",
            "BROWSER_EXECUTABLE_PATH",
            "PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH",
        ):
            configured = os.getenv(env_name)
            if configured:
                return configured

        candidates = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
            "/usr/bin/google-chrome",
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser",
            "/usr/bin/microsoft-edge",
        ]
        for candidate in candidates:
            if Path(candidate).exists():
                return candidate
        return None

    def _require_session(self, session_id: str) -> BrowserRuntimeSessionRecord:
        record = self.sessions.get(session_id)
        if record is None:
            raise ValueError("session not found")
        return record

    async def _screenshot_bytes(
        self,
        *,
        record: BrowserRuntimeSessionRecord,
        request: BrowserRuntimeScreenshotRequest,
    ) -> bytes:
        screenshot_path = self._screenshot_path(record=record, request=request)
        screenshot_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            await record.page.screenshot(path=str(screenshot_path), full_page=request.full_page)
            if screenshot_path.exists():
                return screenshot_path.read_bytes()
        except (OSError, TypeError):
            pass
        result = await record.page.screenshot(full_page=request.full_page)
        if isinstance(result, bytes):
            return result
        raise RuntimeError("Browser runtime screenshot produced no image bytes or file")

    def _screenshot_path(self, *, record: BrowserRuntimeSessionRecord, request: BrowserRuntimeScreenshotRequest) -> Path:
        workspace_id = self._safe_name(str(record.workspace_id or "default-workspace"))
        session_id = self._safe_name(record.session_id)
        name = self._safe_name(request.screenshot_name or f"screenshot-{uuid4()}")
        if not name.endswith(".png"):
            name = f"{name}.png"
        return self.screenshot_dir / workspace_id / session_id / name

    def _profile_path(self, *, workspace_id: str | None, profile_id: str, profile_path: str | None) -> Path:
        safe_workspace = self._safe_name(str(workspace_id or "default-workspace"))
        safe_profile = self._safe_name(profile_id)
        expected = (self.profile_dir / safe_workspace / safe_profile).resolve()
        if profile_path:
            candidate = Path(profile_path)
            if not candidate.is_absolute():
                candidate = Path.cwd() / candidate
            try:
                root = self.profile_dir.resolve()
                resolved = candidate.resolve()
                if str(resolved).startswith(str(root)):
                    return resolved
            except Exception:
                pass
        return expected

    def _ensure_safe_url(self, url: str) -> None:
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
        raise ValueError("Browser runtime only allows example.com, local test pages, or static file URLs")

    def _safe_name(self, value: str) -> str:
        return re.sub(r"[^a-zA-Z0-9_.-]", "-", value).strip("-") or "item"

    def _elapsed_ms(self, started_at: float) -> int:
        return max(0, int((time.perf_counter() - started_at) * 1000))
