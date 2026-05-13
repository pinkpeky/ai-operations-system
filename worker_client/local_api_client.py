"""Worker Console Foundation 本地 API Client。"""

from __future__ import annotations

from typing import Any

import httpx


class WorkerLocalAPIClient:
    """供未来 Worker Console GUI 复用的本地管理 API client。"""

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:9100",
        *,
        timeout: float = 10.0,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._http_client = http_client

    async def _request(self, method: str, path: str) -> dict[str, Any]:
        """发送本地请求并返回 JSON。"""

        if self._http_client is not None:
            response = await self._http_client.request(method, f"{self.base_url}{path}")
            response.raise_for_status()
            body = response.json()
            return body if isinstance(body, dict) else {"value": body}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.request(method, f"{self.base_url}{path}")
            response.raise_for_status()
            body = response.json()
        return body if isinstance(body, dict) else {"value": body}

    async def local_status(self) -> dict[str, Any]:
        """获取本地状态。"""

        return await self._request("GET", "/local/status")

    async def local_health(self) -> dict[str, Any]:
        """获取本地健康状态。"""

        return await self._request("GET", "/local/health")

    async def start_runtime(self) -> dict[str, Any]:
        """启动 runtime。"""

        return await self._request("POST", "/local/runtime/start")

    async def stop_runtime(self) -> dict[str, Any]:
        """停止 runtime。"""

        return await self._request("POST", "/local/runtime/stop")

    async def restart_runtime(self) -> dict[str, Any]:
        """重启 runtime。"""

        return await self._request("POST", "/local/runtime/restart")

    async def start_heartbeat(self) -> dict[str, Any]:
        """启动 heartbeat。"""

        return await self._request("POST", "/local/heartbeat/start")

    async def stop_heartbeat(self) -> dict[str, Any]:
        """停止 heartbeat。"""

        return await self._request("POST", "/local/heartbeat/stop")

    async def local_logs(self, *, lines: int = 100) -> dict[str, Any]:
        """读取最近本地日志。"""

        return await self._request("GET", f"/local/logs?lines={lines}")
