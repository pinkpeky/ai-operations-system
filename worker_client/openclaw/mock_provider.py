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
        if request.action_type in {"publish_submit", "publish_submit_guarded"}:
            output = {
                "message": "mock openclaw cannot perform real publish submit",
                "target": request.target,
                "profile_id": request.profile_id,
                "browser_session_id": request.browser_session_id,
                "input_payload": request.input_payload,
                "metadata": request.metadata,
                "real_openclaw_called": False,
                "actual_publish_performed": False,
                "requires_real_openclaw_provider": True,
                "operator_final_submit_confirmed": bool(request.metadata.get("operator_final_submit_confirmed")),
            }
            duration_ms = max(0, int((time.perf_counter() - started) * 1000))
            return OpenClawActionResponse(
                success=False,
                action_type=request.action_type,
                output_payload=output,
                error="real_publish_provider_not_configured",
                duration_ms=duration_ms,
                provider=self.provider_name,
                mock=True,
            )
        output = {
            "message": "mock openclaw action success",
            "target": request.target,
            "profile_id": request.profile_id,
            "browser_session_id": request.browser_session_id,
            "input_payload": request.input_payload,
            "metadata": request.metadata,
            "real_openclaw_called": False,
            "actual_publish_performed": False,
        }
        if request.action_type == "publish_dry_run":
            output["dry_run_completed"] = True
            output["no_real_publish"] = True
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
                "publish_dry_run": True,
                "publish_submit_guarded": True,
                "real_publish_submit": False,
                "browser_worker_adapter": True,
            },
            actions=[
                "health_check",
                "list_capabilities",
                "execute_action",
                "publish_dry_run",
                "publish_submit_guarded",
            ],
            error=None,
        )

    async def get_version(self) -> str:
        """返回 mock provider 版本。"""

        return "mock-openclaw-0.1"
