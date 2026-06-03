"""HTTP OpenClaw provider for customer-machine workers."""

from __future__ import annotations

import time
from typing import Any

import httpx

from worker_client.openclaw.provider import BaseOpenClawProvider
from worker_client.openclaw.schemas import (
    OpenClawActionRequest,
    OpenClawActionResponse,
    OpenClawCapabilitiesResponse,
    OpenClawHealthResponse,
)


class HttpOpenClawProvider(BaseOpenClawProvider):
    """Proxy the worker OpenClaw protocol to a configured real OpenClaw adapter."""

    mock = False

    def __init__(
        self,
        *,
        provider_name: str = "openclaw_http",
        base_url: str = "",
        api_key: str | None = None,
        timeout_seconds: float = 60.0,
        health_path: str = "/openclaw/health",
        capabilities_path: str = "/openclaw/capabilities",
        action_path: str = "/openclaw/actions",
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.provider_name = provider_name or "openclaw_http"
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or None
        self.timeout_seconds = timeout_seconds
        self.health_path = health_path
        self.capabilities_path = capabilities_path
        self.action_path = action_path
        self.transport = transport

    async def health_check(self) -> OpenClawHealthResponse:
        payload, error, _duration_ms = await self._request("GET", self.health_path)
        if error:
            return OpenClawHealthResponse(
                success=False,
                provider=self.provider_name,
                reachable=False,
                enabled=True,
                mock=False,
                version=None,
                error=error,
            )
        provider = str(payload.get("provider") or self.provider_name)
        success = bool(payload.get("success", True))
        return OpenClawHealthResponse(
            success=success,
            provider=provider,
            reachable=bool(payload.get("reachable", success)),
            enabled=bool(payload.get("enabled", True)),
            mock=bool(payload.get("mock", False)),
            version=payload.get("version"),
            error=payload.get("error"),
        )

    async def list_capabilities(self) -> OpenClawCapabilitiesResponse:
        payload, error, _duration_ms = await self._request("GET", self.capabilities_path)
        if error:
            return OpenClawCapabilitiesResponse(
                success=False,
                provider=self.provider_name,
                mock=False,
                capabilities={
                    "openclaw": False,
                    "real_openclaw": False,
                    "publish_dry_run": False,
                    "publish_submit_guarded": False,
                    "real_publish_submit": False,
                },
                actions=[],
                error=error,
            )
        return OpenClawCapabilitiesResponse(
            success=bool(payload.get("success", True)),
            provider=str(payload.get("provider") or self.provider_name),
            mock=bool(payload.get("mock", False)),
            capabilities=dict(payload.get("capabilities") or {}),
            actions=[str(action) for action in payload.get("actions", [])],
            error=payload.get("error"),
        )

    async def execute_action(self, request: OpenClawActionRequest) -> OpenClawActionResponse:
        started = time.perf_counter()
        payload, error, duration_ms = await self._request("POST", self.action_path, json=request.model_dump(mode="json"))
        if error:
            return OpenClawActionResponse(
                success=False,
                action_type=request.action_type,
                output_payload={
                    "target": request.target,
                    "input_payload": request.input_payload,
                    "metadata": request.metadata,
                    "real_openclaw_called": False,
                    "actual_publish_performed": False,
                },
                error=error,
                duration_ms=duration_ms,
                provider=self.provider_name,
                mock=False,
            )

        output_payload = dict(payload.get("output_payload") or {})
        provider = str(payload.get("provider") or self.provider_name)
        mock = bool(payload.get("mock", False))
        success = bool(payload.get("success", False))
        response_error = payload.get("error")
        response_duration = int(payload.get("duration_ms") or max(duration_ms, int((time.perf_counter() - started) * 1000)))

        if request.action_type in {"publish_submit", "publish_submit_guarded"} and success:
            actual_publish_performed = bool(
                output_payload.get("actual_publish_performed") or output_payload.get("real_openclaw_called")
            )
            output_payload["actual_publish_performed"] = actual_publish_performed
            output_payload.setdefault("real_openclaw_called", actual_publish_performed and not mock)
            if mock:
                success = False
                response_error = "mock_provider_cannot_submit"
            elif not actual_publish_performed:
                success = False
                response_error = "real_publish_evidence_missing_from_provider"

        return OpenClawActionResponse(
            success=success,
            action_type=str(payload.get("action_type") or request.action_type),
            output_payload=output_payload,
            error=response_error,
            duration_ms=response_duration,
            provider=provider,
            mock=mock,
        )

    async def get_version(self) -> str:
        health = await self.health_check()
        return health.version or "openclaw-http-adapter"

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
    ) -> tuple[dict[str, Any], str | None, int]:
        started = time.perf_counter()
        if not self.base_url:
            return {}, "openclaw_http_base_url_required", 0
        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds, transport=self.transport) as client:
                response = await client.request(method, self._url(path), headers=self._headers(), json=json)
                response.raise_for_status()
                payload = response.json()
                if not isinstance(payload, dict):
                    return {}, "openclaw_http_invalid_json_payload", self._duration_ms(started)
                return payload, None, self._duration_ms(started)
        except httpx.HTTPStatusError as exc:
            return {}, f"openclaw_http_status_{exc.response.status_code}", self._duration_ms(started)
        except httpx.RequestError as exc:
            return {}, f"openclaw_http_request_failed: {exc}", self._duration_ms(started)
        except ValueError as exc:
            return {}, f"openclaw_http_invalid_json_payload: {exc}", self._duration_ms(started)

    def _url(self, path: str) -> str:
        if path.startswith("http://") or path.startswith("https://"):
            return path
        return f"{self.base_url}/{path.lstrip('/')}"

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            headers["X-OpenClaw-API-Key"] = self.api_key
        return headers

    @staticmethod
    def _duration_ms(started: float) -> int:
        return max(0, int((time.perf_counter() - started) * 1000))
