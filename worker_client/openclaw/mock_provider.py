"""Mock OpenClaw provider.

该 provider 不调用真实 OpenClaw，不执行社媒平台动作，只返回稳定的协议测试结果。
"""

from __future__ import annotations

import time

from worker_client.openclaw.provider import BaseOpenClawProvider
from worker_client.openclaw.schemas import (
    OpenClawActionRequest,
    OpenClawActionResponse,
    OpenClawCapabilitiesResponse,
    OpenClawHealthResponse,
)


class MockOpenClawProvider(BaseOpenClawProvider):
    """用于 Phase 28 验证链路的 mock OpenClaw provider。"""

    provider_name = "mock"
    mock = True

    async def health_check(self) -> OpenClawHealthResponse:
        """返回 mock health，不访问任何真实执行器。"""

        return OpenClawHealthResponse(
            success=True,
            provider=self.provider_name,
            reachable=True,
            enabled=True,
            mock=True,
            version=await self.get_version(),
            error=None,
        )

    async def execute_action(self, request: OpenClawActionRequest) -> OpenClawActionResponse:
        """返回稳定的 mock action 结果。"""

        started = time.perf_counter()
        output = {
            "message": "mock openclaw action success",
            "target": request.target,
            "profile_id": request.profile_id,
            "browser_session_id": request.browser_session_id,
            "input_payload": request.input_payload,
            "metadata": request.metadata,
            "real_openclaw_called": False,
        }
        duration_ms = max(0, int((time.perf_counter() - started) * 1000))
        return OpenClawActionResponse(
            success=True,
            action_type=request.action_type,
            output_payload=output,
            error=None,
            duration_ms=duration_ms,
            provider=self.provider_name,
            mock=True,
        )

    async def list_capabilities(self) -> OpenClawCapabilitiesResponse:
        """声明当前仅支持 mock OpenClaw protocol。"""

        return OpenClawCapabilitiesResponse(
            success=True,
            provider=self.provider_name,
            mock=True,
            capabilities={
                "openclaw": True,
                "provider": self.provider_name,
                "real_openclaw": False,
                "platform_automation": False,
                "browser_worker_adapter": True,
            },
            actions=["health_check", "list_capabilities", "execute_action"],
            error=None,
        )

    async def get_version(self) -> str:
        """返回 mock provider 版本。"""

        return "mock-openclaw-0.1"
