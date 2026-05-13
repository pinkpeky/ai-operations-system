"""Playwright Browser Provider 占位实现。

Phase 17 不安装、不调用 Playwright。该类只保留 provider 边界，并在被
误用时返回清晰的 placeholder 错误。
"""

from __future__ import annotations

from typing import Any

from app.browser.providers.base import BaseBrowserProvider, BrowserProviderResult


class PlaywrightBrowserProvider(BaseBrowserProvider):
    """未来 Playwright 集成的占位 provider。"""

    provider_name = "playwright"

    async def create_session(self, *, metadata: dict[str, Any] | None = None) -> BrowserProviderResult:
        """返回清晰的占位响应。"""

        return self._placeholder("create_session", target=None, input_payload=metadata or {})

    async def close_session(self, *, provider_session_id: str | None = None) -> BrowserProviderResult:
        """返回清晰的占位响应。"""

        return self._placeholder("close_session", target=provider_session_id, input_payload={})

    async def navigate(
        self,
        *,
        target: str | None,
        input_payload: dict[str, Any],
        session_metadata: dict[str, Any] | None = None,
    ) -> BrowserProviderResult:
        """返回清晰的占位响应。"""

        return self._placeholder("navigate", target=target, input_payload=input_payload)

    async def click(
        self,
        *,
        target: str | None,
        input_payload: dict[str, Any],
        session_metadata: dict[str, Any] | None = None,
    ) -> BrowserProviderResult:
        """返回清晰的占位响应。"""

        return self._placeholder("click", target=target, input_payload=input_payload)

    async def type_text(
        self,
        *,
        target: str | None,
        input_payload: dict[str, Any],
        session_metadata: dict[str, Any] | None = None,
    ) -> BrowserProviderResult:
        """返回清晰的占位响应。"""

        return self._placeholder("type_text", target=target, input_payload=input_payload)

    async def scroll(
        self,
        *,
        target: str | None,
        input_payload: dict[str, Any],
        session_metadata: dict[str, Any] | None = None,
    ) -> BrowserProviderResult:
        """返回清晰的占位响应。"""

        return self._placeholder("scroll", target=target, input_payload=input_payload)

    async def screenshot(
        self,
        *,
        target: str | None,
        input_payload: dict[str, Any],
        session_metadata: dict[str, Any] | None = None,
    ) -> BrowserProviderResult:
        """返回清晰的占位响应。"""

        return self._placeholder("screenshot", target=target, input_payload=input_payload)

    async def get_page_content(
        self,
        *,
        target: str | None,
        input_payload: dict[str, Any],
        session_metadata: dict[str, Any] | None = None,
    ) -> BrowserProviderResult:
        """返回清晰的占位响应。"""

        return self._placeholder("get_page_content", target=target, input_payload=input_payload)

    def _placeholder(self, action_type: str, *, target: str | None, input_payload: dict[str, Any]) -> BrowserProviderResult:
        """构造稳定的占位失败 payload。"""

        message = "PlaywrightBrowserProvider is a placeholder in Phase 17; no browser was started."
        return BrowserProviderResult(
            success=False,
            message=message,
            data={"action_type": action_type, "target": target, "input_payload": input_payload},
            error=message,
        )
