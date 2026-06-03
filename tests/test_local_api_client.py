"""Worker Local API Client tests."""

from __future__ import annotations

import json

import httpx
import pytest

from worker_client.local_api_client import WorkerLocalAPIClient


@pytest.mark.asyncio
async def test_local_api_client_calls_management_endpoints() -> None:
    """Local API client 应调用未来 GUI 所需的本地管理端点。"""

    seen: list[tuple[str, str]] = []
    payloads: dict[str, dict[str, object]] = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        seen.append((request.method, request.url.path))
        if request.content:
            payloads[request.url.path] = json.loads(request.content.decode("utf-8"))
        if request.url.path == "/local/logs":
            return httpx.Response(200, json={"lines": ["ok"]})
        return httpx.Response(200, json={"success": True, "path": request.url.path})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        api = WorkerLocalAPIClient("http://127.0.0.1:9100", http_client=client)
        assert (await api.local_status())["success"] is True
        assert (await api.local_health())["success"] is True
        assert (await api.start_runtime())["success"] is True
        assert (await api.stop_runtime())["success"] is True
        assert (await api.restart_runtime())["success"] is True
        assert (await api.start_heartbeat())["success"] is True
        assert (await api.stop_heartbeat())["success"] is True
        assert (await api.metric_dispatch_scheduler_status())["success"] is True
        assert (await api.configure_metric_dispatch_scheduler({"client_timer_payload": {"request_body": {"a": 1}}}))["success"] is True
        assert (await api.tick_metric_dispatch_scheduler(force=True))["success"] is True
        assert (await api.start_metric_dispatch_scheduler())["success"] is True
        assert (await api.stop_metric_dispatch_scheduler())["success"] is True
        assert (await api.clear_metric_dispatch_scheduler())["success"] is True
        assert (await api.local_logs())["lines"] == ["ok"]

    assert ("GET", "/local/status") in seen
    assert ("POST", "/local/runtime/start") in seen
    assert ("GET", "/local/metric-dispatch-scheduler") in seen
    assert ("POST", "/local/metric-dispatch-scheduler/configure") in seen
    assert payloads["/local/metric-dispatch-scheduler/tick"]["force"] is True
    assert ("GET", "/local/logs") in seen
