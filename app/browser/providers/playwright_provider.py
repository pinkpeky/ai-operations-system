"""Playwright Local Provider。

该 provider 是 Phase 18 的基础真实浏览器执行能力，只允许受控的本地
Chromium/headless 场景。它不实现登录、Cookie 注入、指纹绕过、验证码、
社媒自动化或 autonomous browser agent。
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from uuid import uuid4

from app.browser.providers.base import BaseBrowserProvider, BrowserProviderResult


@dataclass(slots=True)
class _PlaywrightSession:
    """进程内 Playwright session 句柄。"""

    playwright: Any
    browser: Any
    context: Any
    page: Any
    metadata: dict[str, Any]


class PlaywrightLocalProvider(BaseBrowserProvider):
    """本地 Playwright Chromium provider。"""

    provider_name = "playwright_local"
    _sessions: dict[str, _PlaywrightSession] = {}

    def __init__(
        self,
        *,
        timeout_seconds: float = 30.0,
        browser_type: str = "chromium",
        headless: bool = True,
        viewport: dict[str, int] | None = None,
        screenshot_dir: str | Path = "screenshots",
    ) -> None:
        self.timeout_seconds = timeout_seconds
        self.timeout_ms = int(timeout_seconds * 1000)
        self.browser_type = browser_type
        self.headless = headless
        self.viewport = viewport or {"width": 1280, "height": 720}
        self.screenshot_dir = Path(screenshot_dir)

    async def create_session(self, *, metadata: dict[str, Any] | None = None) -> BrowserProviderResult:
        """启动本地 headless Chromium session。"""

        try:
            from playwright.async_api import async_playwright
        except Exception as exc:
            message = "Playwright Python is not installed or cannot be imported"
            return BrowserProviderResult(success=False, message=message, error=str(exc), data={})

        try:
            requested = self.browser_type.lower()
            if requested != "chromium":
                raise ValueError("Phase 18 only supports chromium")
            playwright = await async_playwright().start()
            browser_launcher = getattr(playwright, requested)
            browser = await browser_launcher.launch(headless=self.headless, args=["--no-sandbox"])
            context = await browser.new_context(viewport=self.viewport)
            page = await context.new_page()
            provider_session_id = f"playwright-{uuid4()}"
            started_at = datetime.now(UTC).isoformat()
            provider_metadata = {
                "provider_session_id": provider_session_id,
                "browser_type": requested,
                "headless": self.headless,
                "viewport": self.viewport,
                "started_at": started_at,
                "workspace_id": (metadata or {}).get("workspace_id"),
                "session_id": (metadata or {}).get("session_id"),
            }
            self._sessions[provider_session_id] = _PlaywrightSession(
                playwright=playwright,
                browser=browser,
                context=context,
                page=page,
                metadata=provider_metadata,
            )
            return BrowserProviderResult(
                success=True,
                message="playwright local session created",
                data={
                    "provider_session_id": provider_session_id,
                    "browser_id": str(id(browser)),
                    "page_id": str(id(page)),
                    "provider_session_metadata": provider_metadata,
                },
            )
        except Exception as exc:
            return BrowserProviderResult(
                success=False,
                message="playwright local session creation failed",
                error=str(exc),
                data={},
            )

    async def close_session(self, *, provider_session_id: str | None = None) -> BrowserProviderResult:
        """关闭本地 Playwright session。"""

        if not provider_session_id:
            return BrowserProviderResult(success=False, message="provider_session_id is required", error="provider_session_id is required")
        session = self._sessions.pop(provider_session_id, None)
        if session is None:
            return BrowserProviderResult(success=False, message="playwright session not found", error="playwright session not found")
        errors: list[str] = []
        for closer in (session.context.close, session.browser.close, session.playwright.stop):
            try:
                result = closer()
                if hasattr(result, "__await__"):
                    await result
            except Exception as exc:
                errors.append(str(exc))
        if errors:
            return BrowserProviderResult(success=False, message="playwright local session close failed", error="; ".join(errors))
        return BrowserProviderResult(success=True, message="playwright local session closed", data={"provider_session_id": provider_session_id})

    async def navigate(
        self,
        *,
        target: str | None,
        input_payload: dict[str, Any],
        session_metadata: dict[str, Any] | None = None,
    ) -> BrowserProviderResult:
        """导航到允许范围内的 URL。"""

        try:
            url = self._ensure_safe_url(target)
            session = self._get_session(session_metadata)
            await session.page.goto(url, timeout=self.timeout_ms, wait_until=input_payload.get("wait_until", "domcontentloaded"))
            title = await session.page.title()
            return BrowserProviderResult(
                success=True,
                message="playwright navigate success",
                data={
                    "target_url": url,
                    "page_title": title,
                    "provider_session_metadata": session.metadata,
                },
            )
        except Exception as exc:
            return BrowserProviderResult(success=False, message="playwright navigate failed", error=str(exc), data={})

    async def click(
        self,
        *,
        target: str | None,
        input_payload: dict[str, Any],
        session_metadata: dict[str, Any] | None = None,
    ) -> BrowserProviderResult:
        """点击允许页面上的选择器。"""

        try:
            selector = self._selector(target=target, input_payload=input_payload)
            session = self._get_session(session_metadata)
            await session.page.click(selector, timeout=self.timeout_ms)
            title = await session.page.title()
            return BrowserProviderResult(success=True, message="playwright click success", data={"selector": selector, "page_title": title})
        except Exception as exc:
            return BrowserProviderResult(success=False, message="playwright click failed", error=str(exc), data={})

    async def type_text(
        self,
        *,
        target: str | None,
        input_payload: dict[str, Any],
        session_metadata: dict[str, Any] | None = None,
    ) -> BrowserProviderResult:
        """向选择器输入文本。"""

        try:
            selector = self._selector(target=target, input_payload=input_payload)
            text = str(input_payload.get("text") or "")
            session = self._get_session(session_metadata)
            await session.page.fill(selector, text, timeout=self.timeout_ms)
            title = await session.page.title()
            return BrowserProviderResult(success=True, message="playwright type_text success", data={"selector": selector, "page_title": title})
        except Exception as exc:
            return BrowserProviderResult(success=False, message="playwright type_text failed", error=str(exc), data={})

    async def scroll(
        self,
        *,
        target: str | None,
        input_payload: dict[str, Any],
        session_metadata: dict[str, Any] | None = None,
    ) -> BrowserProviderResult:
        """滚动页面。"""

        try:
            session = self._get_session(session_metadata)
            delta_y = int(input_payload.get("delta_y") or 600)
            await session.page.mouse.wheel(0, delta_y)
            title = await session.page.title()
            return BrowserProviderResult(success=True, message="playwright scroll success", data={"page_title": title, "delta_y": delta_y})
        except Exception as exc:
            return BrowserProviderResult(success=False, message="playwright scroll failed", error=str(exc), data={})

    async def screenshot(
        self,
        *,
        target: str | None,
        input_payload: dict[str, Any],
        session_metadata: dict[str, Any] | None = None,
    ) -> BrowserProviderResult:
        """保存 PNG 截图到 workspace/session 分类目录。"""

        try:
            session = self._get_session(session_metadata)
            workspace_id = self._safe_path_part(str(input_payload.get("_workspace_id") or session.metadata.get("workspace_id") or "default"))
            session_id = self._safe_path_part(str(input_payload.get("_session_id") or session.metadata.get("session_id") or "default"))
            name = self._safe_path_part(str(input_payload.get("screenshot_name") or target or f"screenshot-{uuid4()}"))
            filename = f"{name}.png" if not name.endswith(".png") else name
            output_dir = self.screenshot_dir / workspace_id / session_id
            output_dir.mkdir(parents=True, exist_ok=True)
            path = output_dir / filename
            await session.page.screenshot(path=str(path), full_page=bool(input_payload.get("full_page", True)))
            title = await session.page.title()
            return BrowserProviderResult(
                success=True,
                message="playwright screenshot success",
                data={
                    "screenshot_path": str(path),
                    "screenshot_filename": filename,
                    "page_title": title,
                },
            )
        except Exception as exc:
            return BrowserProviderResult(success=False, message="playwright screenshot failed", error=str(exc), data={})

    async def get_page_content(
        self,
        *,
        target: str | None,
        input_payload: dict[str, Any],
        session_metadata: dict[str, Any] | None = None,
    ) -> BrowserProviderResult:
        """读取当前页面 HTML 内容。"""

        try:
            session = self._get_session(session_metadata)
            content = await session.page.content()
            title = await session.page.title()
            return BrowserProviderResult(
                success=True,
                message="playwright get_page_content success",
                data={"content": content, "page_title": title},
            )
        except Exception as exc:
            return BrowserProviderResult(success=False, message="playwright get_page_content failed", error=str(exc), data={})

    def _get_session(self, session_metadata: dict[str, Any] | None) -> _PlaywrightSession:
        """根据 provider_session_id 获取进程内 session。"""

        provider_session_id = str((session_metadata or {}).get("provider_session_id") or "")
        if not provider_session_id:
            raise ValueError("provider_session_id is required")
        session = self._sessions.get(provider_session_id)
        if session is None:
            raise ValueError("playwright session not found")
        return session

    def _ensure_safe_url(self, target: str | None) -> str:
        """限制 Phase 18 只访问 example.com、本地测试页或静态页面。"""

        if not target:
            raise ValueError("target URL is required")
        parsed = urlparse(target)
        if parsed.scheme == "file":
            return target
        if parsed.scheme not in {"http", "https"}:
            raise ValueError("Only http, https, and file URLs are allowed")
        host = parsed.hostname or ""
        if host == "example.com" or host.endswith(".example.com"):
            return target
        if host in {"localhost", "127.0.0.1", "0.0.0.0", "::1"}:
            return target
        raise ValueError("Phase 18 browser navigation only allows example.com, local test pages, or static file URLs")

    def _selector(self, *, target: str | None, input_payload: dict[str, Any]) -> str:
        """读取 selector 字段，兼容旧 target 用法。"""

        selector = str(input_payload.get("selector") or target or "")
        if not selector:
            raise ValueError("selector is required")
        return selector

    def _safe_path_part(self, value: str) -> str:
        """清理路径片段，避免路径穿越。"""

        cleaned = re.sub(r"[^a-zA-Z0-9_.-]+", "-", value.strip())
        return cleaned.strip(".-") or "item"
