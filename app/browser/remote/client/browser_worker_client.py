"""Browser Worker HTTP client。

该 client 封装 AI Server 与远程/独立 browser worker 的协议，并提供结构化
retry 日志，避免 worker 超时或失败时直接拖垮 API 进程。
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any

import httpx

from app.browser.remote.services.browser_worker_auth_service import BrowserWorkerAuthService


@dataclass(slots=True)
class BrowserWorkerClientResult:
    """结构化 BrowserWorkerClient 返回结果。"""

    success: bool
    message: str
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    status_code: int | None = None
    retry_count: int = 0
    retry_logs: list[dict[str, Any]] = field(default_factory=list)

    def model_dump(self) -> dict[str, Any]:
        """返回可 JSON 序列化的结果。"""

        return {
            "success": self.success,
            "message": self.message,
            "data": self.data,
            "error": self.error,
            "status_code": self.status_code,
            "retry_count": self.retry_count,
            "retry_logs": self.retry_logs,
        }


class BrowserWorkerClient:
    """带 timeout / retry 处理的远程 Browser Worker HTTP client。"""

    def __init__(
        self,
        *,
        base_url: str,
        timeout_seconds: float = 30.0,
        retry_count: int = 2,
        action_timeout_seconds: float | None = None,
        retry_backoff_seconds: float = 0.0,
        http_client: httpx.AsyncClient | None = None,
        worker_id: str | None = None,
        worker_secret: str | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.retry_count = max(0, retry_count)
        self.action_timeout_seconds = action_timeout_seconds or timeout_seconds
        self.retry_backoff_seconds = max(0.0, retry_backoff_seconds)
        self.http_client = http_client
        self.worker_id = worker_id
        self.worker_secret = worker_secret

    async def health_check(self) -> BrowserWorkerClientResult:
        """检查 worker 是否可达。"""

        return await self._request("GET", "/health")

    async def create_session(self, *, payload: dict[str, Any]) -> BrowserWorkerClientResult:
        """请求创建远程 worker session。"""

        return await self._request("POST", "/sessions", json=payload)

    async def execute_action(self, *, payload: dict[str, Any]) -> BrowserWorkerClientResult:
        """请求执行 worker action，并使用 action 专属 timeout。"""

        return await self._request("POST", "/actions", json=payload, timeout_seconds=self.action_timeout_seconds)

    async def close_session(self, *, remote_session_id: str) -> BrowserWorkerClientResult:
        """请求关闭 worker session。"""

        return await self._request("POST", f"/sessions/{remote_session_id}/close")

    async def start_human_control(self, *, remote_session_id: str, payload: dict[str, Any]) -> BrowserWorkerClientResult:
        """请求 worker 进入人工接管 metadata 状态。"""

        return await self._request(
            "POST",
            "/human-control/start",
            json={"remote_session_id": remote_session_id, **payload},
            timeout_seconds=self.action_timeout_seconds,
        )

    async def complete_human_control(self, *, remote_session_id: str, payload: dict[str, Any]) -> BrowserWorkerClientResult:
        """请求 worker 结束人工接管 metadata 状态。"""

        return await self._request(
            "POST",
            "/human-control/complete",
            json={"remote_session_id": remote_session_id, **payload},
            timeout_seconds=self.action_timeout_seconds,
        )

    async def get_human_control_status(self, *, remote_session_id: str) -> BrowserWorkerClientResult:
        """查询 worker 侧人工接管状态。"""

        return await self._request("GET", f"/human-control/status/{remote_session_id}")

    async def get_ui_access_capabilities(self) -> BrowserWorkerClientResult:
        """查询 worker UI access placeholder 能力。"""

        return await self._request("GET", "/ui-access/capabilities")

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        timeout_seconds: float | None = None,
    ) -> BrowserWorkerClientResult:
        """发送请求，并执行简单 retry/backoff。"""

        last_error: str | None = None
        retry_logs: list[dict[str, Any]] = []
        used_timeout = timeout_seconds or self.timeout_seconds
        for attempt in range(self.retry_count + 1):
            try:
                headers = self._auth_headers(body=json)
                if self.http_client is not None:
                    response = await self.http_client.request(method, path, json=json, timeout=used_timeout, headers=headers)
                else:
                    async with httpx.AsyncClient(base_url=self.base_url, timeout=used_timeout) as client:
                        response = await client.request(method, path, json=json, headers=headers)
                payload = response.json()
                if response.status_code >= 500 and attempt < self.retry_count:
                    last_error = str(
                        payload.get("error")
                        or payload.get("message")
                        or f"worker server error: {response.status_code}"
                    )
                    retry_logs.append({"attempt": attempt + 1, "status_code": response.status_code, "error": last_error})
                    if self.retry_backoff_seconds:
                        await asyncio.sleep(self.retry_backoff_seconds)
                    continue
                return self._from_payload(
                    payload,
                    status_code=response.status_code,
                    retry_count=attempt,
                    retry_logs=retry_logs,
                )
            except Exception as exc:
                last_error = str(exc)
                retry_logs.append({"attempt": attempt + 1, "status_code": None, "error": last_error})
                if attempt >= self.retry_count:
                    break
                if self.retry_backoff_seconds:
                    await asyncio.sleep(self.retry_backoff_seconds)
        retry_count = max(0, len(retry_logs) - 1)
        return BrowserWorkerClientResult(
            success=False,
            message="browser worker request failed",
            data={"retry_count": retry_count, "retry_logs": retry_logs},
            error=last_error,
            status_code=None,
            retry_count=retry_count,
            retry_logs=retry_logs,
        )

    def _from_payload(
        self,
        payload: dict[str, Any],
        *,
        status_code: int,
        retry_count: int = 0,
        retry_logs: list[dict[str, Any]] | None = None,
    ) -> BrowserWorkerClientResult:
        """标准化 worker 响应 payload。"""

        success = bool(payload.get("success")) and status_code < 400
        logs = retry_logs or []
        data = dict(payload.get("data") or {})
        data["retry_count"] = retry_count
        data["retry_logs"] = logs
        for key in ("remote_session_id", "remote_action_id"):
            if payload.get(key) is not None:
                data[key] = payload.get(key)
        return BrowserWorkerClientResult(
            success=success,
            message=str(payload.get("message") or ("ok" if success else "failed")),
            data=data,
            error=payload.get("error") if not success else None,
            status_code=status_code,
            retry_count=retry_count,
            retry_logs=logs,
        )

    def _auth_headers(self, *, body: dict[str, Any] | None) -> dict[str, str]:
        """Build signed worker request headers when a plaintext secret is available."""

        if not self.worker_secret:
            return {}
        headers = BrowserWorkerAuthService.sign_request(secret=self.worker_secret, body=body)
        if self.worker_id:
            headers["X-Worker-Id"] = self.worker_id
        return headers
