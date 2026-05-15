"""OpenClaw runtime facade for worker_client."""

from __future__ import annotations

from worker_client.openclaw.mock_provider import MockOpenClawProvider
from worker_client.openclaw.provider import BaseOpenClawProvider
from worker_client.openclaw.schemas import (
    OpenClawActionRequest,
    OpenClawActionResponse,
    OpenClawCapabilitiesResponse,
    OpenClawHealthResponse,
)


class OpenClawRuntime:
    """Worker runtime 内的 OpenClaw 适配门面。"""

    def __init__(
        self,
        *,
        provider_name: str = "mock",
        enabled: bool = True,
        provider: BaseOpenClawProvider | None = None,
    ) -> None:
        self.enabled = enabled
        self.provider = provider or self._build_provider(provider_name)

    def _build_provider(self, provider_name: str) -> BaseOpenClawProvider:
        """按配置构造 provider；当前仅允许 mock。"""

        if provider_name != "mock":
            # 当前不调用真实 OpenClaw，未知 provider 也降级为 mock，避免客户机 worker 崩溃。
            return MockOpenClawProvider()
        return MockOpenClawProvider()

    async def health_check(self) -> OpenClawHealthResponse:
        """返回 OpenClaw runtime health。"""

        if not self.enabled:
            return OpenClawHealthResponse(
                success=False,
                provider=self.provider.provider_name,
                reachable=False,
                enabled=False,
                mock=self.provider.mock,
                version=None,
                error="OpenClaw runtime is disabled",
            )
        return await self.provider.health_check()

    async def capabilities(self) -> OpenClawCapabilitiesResponse:
        """返回 OpenClaw runtime 能力。"""

        if not self.enabled:
            return OpenClawCapabilitiesResponse(
                success=False,
                provider=self.provider.provider_name,
                mock=self.provider.mock,
                capabilities={"openclaw": False},
                actions=[],
                error="OpenClaw runtime is disabled",
            )
        return await self.provider.list_capabilities()

    async def execute_action(self, request: OpenClawActionRequest) -> OpenClawActionResponse:
        """执行 OpenClaw action；当前仅 mock。"""

        if not self.enabled:
            return OpenClawActionResponse(
                success=False,
                action_type=request.action_type,
                output_payload={},
                error="OpenClaw runtime is disabled",
                duration_ms=0,
                provider=self.provider.provider_name,
                mock=self.provider.mock,
            )
        return await self.provider.execute_action(request)
