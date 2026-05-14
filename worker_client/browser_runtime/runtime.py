"""Remote Browser Runtime facade for worker_client local API."""

from __future__ import annotations

from worker_client.browser_runtime.playwright_provider import PlaywrightBrowserRuntimeProvider
from worker_client.browser_runtime.schemas import (
    BrowserRuntimeCreateSessionRequest,
    BrowserRuntimeNavigateRequest,
    BrowserRuntimePageResponse,
    BrowserRuntimeScreenshotRequest,
    BrowserRuntimeSessionResponse,
)
from worker_client.config import WorkerClientConfig


class BrowserRuntime:
    """Thin facade around the configured Playwright runtime provider."""

    def __init__(self, provider: PlaywrightBrowserRuntimeProvider) -> None:
        self.provider = provider

    @classmethod
    def from_worker_client_config(cls, config: WorkerClientConfig) -> "BrowserRuntime":
        """Build a runtime from worker_client.yaml."""

        headless = bool(config.capabilities.get("headless", False))
        provider = PlaywrightBrowserRuntimeProvider(
            timeout_seconds=config.timeout_seconds,
            headless=headless,
            screenshot_dir=config.screenshot_dir,
            profile_dir=config.profile_dir,
        )
        return cls(provider)

    @classmethod
    def from_worker_settings(cls, settings: object) -> "BrowserRuntime":
        """Build a runtime from the standalone browser-worker settings."""

        provider = PlaywrightBrowserRuntimeProvider(
            timeout_seconds=float(getattr(settings, "worker_timeout_seconds", 30.0)),
            headless=bool(getattr(settings, "worker_headless", True)),
            viewport={
                "width": int(getattr(settings, "worker_viewport_width", 1280)),
                "height": int(getattr(settings, "worker_viewport_height", 720)),
            },
            screenshot_dir=str(getattr(settings, "worker_screenshot_dir", "worker/screenshots")),
            profile_dir=str(getattr(settings, "worker_profile_dir", "worker/profiles")),
        )
        return cls(provider)

    async def create_session(self, request: BrowserRuntimeCreateSessionRequest) -> BrowserRuntimeSessionResponse:
        return await self.provider.create_session(request)

    async def navigate(self, *, session_id: str, request: BrowserRuntimeNavigateRequest):
        return await self.provider.navigate(session_id=session_id, url=request.url)

    async def screenshot(self, *, session_id: str, request: BrowserRuntimeScreenshotRequest):
        return await self.provider.screenshot(session_id=session_id, request=request)

    async def get_page(self, *, session_id: str) -> BrowserRuntimePageResponse:
        return await self.provider.get_page(session_id=session_id)

    async def close_session(self, *, session_id: str) -> BrowserRuntimeSessionResponse:
        return await self.provider.close_session(session_id=session_id)

    async def close_all(self) -> None:
        await self.provider.close_all()
