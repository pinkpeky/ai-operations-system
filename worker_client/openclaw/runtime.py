"""OpenClaw runtime facade for worker_client."""

from __future__ import annotations

from typing import Any

from worker_client.openclaw.http_provider import HttpOpenClawProvider
from worker_client.openclaw.mock_provider import MockOpenClawProvider
from worker_client.openclaw.provider import BaseOpenClawProvider
from worker_client.openclaw.schemas import (
    OpenClawActionRequest,
    OpenClawActionResponse,
    OpenClawCapabilitiesResponse,
    OpenClawHealthResponse,
    OpenClawProviderDiagnosticsResponse,
)


class OpenClawRuntime:
    """Worker runtime 内的 OpenClaw 适配门面。"""

    def __init__(
        self,
        *,
        provider_name: str = "mock",
        enabled: bool = True,
        provider_config: dict[str, Any] | None = None,
        provider: BaseOpenClawProvider | None = None,
    ) -> None:
        self.enabled = enabled
        self.provider_config = provider_config or {}
        self.provider = provider or self._build_provider(provider_name, self.provider_config)

    def _build_provider(self, provider_name: str, provider_config: dict[str, Any]) -> BaseOpenClawProvider:
        """按配置构造 provider；当前仅允许 mock。"""

        normalized = provider_name.strip().lower()
        if normalized in {"", "mock", "disabled"}:
            # 当前不调用真实 OpenClaw，未知 provider 也降级为 mock，避免客户机 worker 崩溃。
            return MockOpenClawProvider()
        return HttpOpenClawProvider(
            provider_name=provider_name,
            base_url=str(provider_config.get("base_url") or ""),
            api_key=str(provider_config.get("api_key") or "") or None,
            timeout_seconds=float(provider_config.get("timeout_seconds") or 60.0),
            health_path=str(provider_config.get("health_path") or "/openclaw/health"),
            capabilities_path=str(provider_config.get("capabilities_path") or "/openclaw/capabilities"),
            action_path=str(provider_config.get("action_path") or "/openclaw/actions"),
        )

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

    def provider_diagnostics(self) -> OpenClawProviderDiagnosticsResponse:
        """Return configuration diagnostics without calling the provider or exposing secrets."""

        provider = self.provider.provider_name
        normalized = provider.strip().lower()
        mock = bool(self.provider.mock)
        base_url = str(self.provider_config.get("base_url") or "").strip()
        api_key = str(self.provider_config.get("api_key") or "").strip()
        timeout_seconds = self.provider_config.get("timeout_seconds")
        paths = {
            "health_path": str(self.provider_config.get("health_path") or "/openclaw/health"),
            "capabilities_path": str(self.provider_config.get("capabilities_path") or "/openclaw/capabilities"),
            "action_path": str(self.provider_config.get("action_path") or "/openclaw/actions"),
        }
        required_env = [
            "WORKER_CLIENT_OPENCLAW_PROVIDER",
            "WORKER_CLIENT_OPENCLAW_BASE_URL",
            "WORKER_CLIENT_OPENCLAW_API_KEY",
        ]
        missing_config: list[str] = []
        next_actions: list[str] = []

        if not self.enabled:
            readiness_status = "openclaw_provider_disabled"
            missing_config.append("WORKER_CLIENT_OPENCLAW_ENABLED")
            next_actions.append("enable_worker_client_openclaw_provider")
        elif mock or normalized in {"", "mock", "disabled"}:
            readiness_status = "openclaw_provider_is_mock"
            missing_config.append("WORKER_CLIENT_OPENCLAW_PROVIDER")
            next_actions.append("set_WORKER_CLIENT_OPENCLAW_PROVIDER_openclaw_http")
            next_actions.append("configure_WORKER_CLIENT_OPENCLAW_BASE_URL")
        elif normalized in {"openclaw_http", "http", "openclaw"} and not base_url:
            readiness_status = "openclaw_http_base_url_required"
            missing_config.append("WORKER_CLIENT_OPENCLAW_BASE_URL")
            next_actions.append("configure_WORKER_CLIENT_OPENCLAW_BASE_URL")
        else:
            readiness_status = "openclaw_provider_configured_pending_capability_check"
            next_actions.append("verify_openclaw_health_and_capabilities")
            next_actions.append("confirm_real_publish_submit_and_publish_submit_guarded")

        configured = self.enabled and not mock and not missing_config
        return OpenClawProviderDiagnosticsResponse(
            success=configured,
            provider=provider,
            enabled=self.enabled,
            mock=mock,
            configured=configured,
            readiness_status=readiness_status,
            base_url_configured=bool(base_url),
            api_key_configured=bool(api_key),
            timeout_seconds=float(timeout_seconds) if timeout_seconds is not None else None,
            paths=paths,
            missing_config=missing_config,
            required_env=required_env,
            next_actions=next_actions,
            secret_fields_redacted=["api_key", "WORKER_CLIENT_OPENCLAW_API_KEY"],
        )
