"""OpenClaw worker HTTP client."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any

import httpx

from app.browser.remote.services.browser_worker_auth_service import BrowserWorkerAuthService


@dataclass(slots=True)
class OpenClawWorkerClientResult:
    """OpenClaw worker client 标准结果。"""

    success: bool
    message: str
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    status_code: int | None = None
    retry_count: int = 0


class OpenClawWorkerClient:
    """通过 Browser Worker base_url 调用 worker_client OpenClaw runtime。"""

    def __init__(
        self,
        *,
        base_url: str,
        timeout_seconds: float = 60.0,
        retry_count: int = 0,
        retry_backoff_seconds: float = 0.0,
        http_client: httpx.AsyncClient | None = None,
        worker_id: str | None = None,
        worker_secret: str | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.retry_count = max(0, retry_count)
        self.retry_backoff_seconds = max(0.0, retry_backoff_seconds)
        self.http_client = http_client
        self.worker_id = worker_id
        self.worker_secret = worker_secret

    async def health_check(self) -> OpenClawWorkerClientResult:
        """检查 OpenClaw worker runtime health。"""

        return await self._request("GET", "/openclaw/health")

    async def capabilities(self) -> OpenClawWorkerClientResult:
        """查询 OpenClaw worker runtime capabilities。"""

        return await self._request("GET", "/openclaw/capabilities")

    async def execute_action(self, *, payload: dict[str, Any]) -> OpenClawWorkerClientResult:
        """执行 OpenClaw action。"""

        return await self._request("POST", "/openclaw/actions", json=payload)

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
    ) -> OpenClawWorkerClientResult:
        """发送请求并返回结构化结果，避免 worker 异常拖垮 API。"""

        last_error: str | None = None
        for attempt in range(self.retry_count + 1):
            try:
                headers = self._auth_headers(body=json)
                if self.http_client is not None:
                    response = await self.http_client.request(method, path, json=json, headers=headers, timeout=self.timeout_seconds)
                else:
                    async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout_seconds) as client:
                        response = await client.request(method, path, json=json, headers=headers)
                payload = response.json()
                if response.status_code >= 500 and attempt < self.retry_count:
                    last_error = str(payload.get("error") or payload.get("message") or f"worker error {response.status_code}")
                    if self.retry_backoff_seconds:
                        await asyncio.sleep(self.retry_backoff_seconds)
                    continue
                return self._from_payload(payload, status_code=response.status_code, retry_count=attempt)
            except Exception as exc:
                last_error = str(exc)
                if attempt >= self.retry_count:
                    break
                if self.retry_backoff_seconds:
                    await asyncio.sleep(self.retry_backoff_seconds)
        return OpenClawWorkerClientResult(
            success=False,
            message="openclaw worker request failed",
            data={},
            error=last_error,
            status_code=None,
            retry_count=self.retry_count,
        )

    def _from_payload(self, payload: dict[str, Any], *, status_code: int, retry_count: int) -> OpenClawWorkerClientResult:
        """标准化 worker payload。"""

        success = bool(payload.get("success")) and status_code < 400
        data = dict(payload)
        if isinstance(payload.get("output_payload"), dict):
            data["output_payload"] = payload["output_payload"]
        return OpenClawWorkerClientResult(
            success=success,
            message=str(payload.get("message") or ("ok" if success else "failed")),
            data=data,
            error=payload.get("error") if not success else None,
            status_code=status_code,
            retry_count=retry_count,
        )

    def _auth_headers(self, *, body: dict[str, Any] | None) -> dict[str, str]:
        """如果进程内有 worker secret，则复用 Phase 26 签名机制。"""

        if not self.worker_secret:
            return {}
        headers = BrowserWorkerAuthService.sign_request(secret=self.worker_secret, body=body)
        if self.worker_id:
            headers["X-Worker-Id"] = self.worker_id
        return headers
