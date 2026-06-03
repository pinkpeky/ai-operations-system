"""Worker Client heartbeat tests."""

from __future__ import annotations

import asyncio
import json

import httpx
import pytest

from worker_client.config import WorkerClientConfig, WorkerClientState, save_worker_state
from worker_client.heartbeat import WorkerHeartbeatResult, heartbeat_loop, send_heartbeat_once


@pytest.mark.asyncio
async def test_worker_client_heartbeat_sends_secret_and_signature(tmp_path) -> None:
    """heartbeat 应携带 worker secret 与 Phase 26 签名头，且 body 不泄露 secret。"""

    state_path = tmp_path / "worker_state.json"
    save_worker_state(
        state_path,
        WorkerClientState(
            worker_id="worker-123",
            worker_secret="local-secret",
            server_url="http://ai-server.test",
            worker_name="worker",
            workspace_id="workspace-a",
            worker_base_url="http://localhost:9100",
        ),
    )
    config = WorkerClientConfig(
        server_url="http://ai-server.test",
        worker_name="worker",
        worker_type="playwright",
        workspace_id="workspace-a",
        state_path=state_path,
        capabilities={"browser": "chromium", "screenshot": True},
    )

    async def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content.decode("utf-8"))
        assert request.url.path == "/api/v1/browser-workers/worker-123/heartbeat"
        assert request.headers["X-Workspace-Id"] == "workspace-a"
        assert request.headers["X-Worker-Secret"] == "local-secret"
        assert request.headers["X-Worker-Id"] == "worker-123"
        assert request.headers["X-Worker-Signature"]
        assert request.headers["X-Worker-Timestamp"]
        assert request.headers["X-Worker-Nonce"]
        assert "local-secret" not in request.content.decode("utf-8")
        assert body["status"] == "online"
        return httpx.Response(200, json={"id": "worker-123", "auth_status": "verified"})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        result = await send_heartbeat_once(config, http_client=client)

    assert result.success is True
    assert result.auth_status == "verified"


@pytest.mark.asyncio
async def test_worker_client_heartbeat_loop_marks_running_status(monkeypatch) -> None:
    updates: list[dict[str, object]] = []
    stop_event = asyncio.Event()
    config = WorkerClientConfig(
        server_url="http://ai-server.test",
        worker_name="worker",
        worker_type="playwright",
        workspace_id="workspace-a",
        heartbeat_interval_seconds=1,
    )

    async def fake_send_heartbeat_once(config, *, status="online"):  # type: ignore[no-untyped-def]
        stop_event.set()
        return WorkerHeartbeatResult(
            success=True,
            status_code=200,
            worker_id="worker-123",
            auth_status="verified",
            response={"id": "worker-123"},
        )

    def fake_update_status(payload):  # type: ignore[no-untyped-def]
        updates.append(dict(payload))
        return payload

    monkeypatch.setattr("worker_client.heartbeat.send_heartbeat_once", fake_send_heartbeat_once)
    monkeypatch.setattr("worker_client.heartbeat.update_status", fake_update_status)

    await heartbeat_loop(config, stop_event=stop_event)

    assert updates[0]["heartbeat_running"] is True
    assert [payload.get("heartbeat_running") for payload in updates].count(True) >= 2
    assert updates[-1]["heartbeat_running"] is False

