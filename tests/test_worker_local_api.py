"""Worker local management API tests."""

from __future__ import annotations

from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient

from tests.test_worker_client_runtime_compatibility import FakeRuntime
from worker_client.config import WorkerClientConfig
from worker_client.runtime import create_worker_client_app


class FakeManager:
    """轻量 manager，用于验证 /local/* API。"""

    def __init__(self) -> None:
        self.started = False
        self.heartbeat = False

    def runtime_state(self) -> dict[str, Any]:
        return {"runtime_running": self.started, "heartbeat_running": self.heartbeat, "worker_secret": "hidden"}

    def runtime_health(self) -> dict[str, Any]:
        return {"success": True, "runtime_running": self.started, "heartbeat_running": self.heartbeat}

    def start_runtime(self) -> dict[str, Any]:
        self.started = True
        return self.runtime_state()

    def stop_runtime(self) -> dict[str, Any]:
        self.started = False
        return self.runtime_state()

    def restart_runtime(self) -> dict[str, Any]:
        self.started = True
        return self.runtime_state()

    def start_heartbeat(self) -> dict[str, Any]:
        self.heartbeat = True
        return self.runtime_state()

    def stop_heartbeat(self) -> dict[str, Any]:
        self.heartbeat = False
        return self.runtime_state()


@pytest.mark.asyncio
async def test_worker_local_management_api(tmp_path) -> None:
    """本地管理 API 应暴露 status / health / runtime / heartbeat / logs。"""

    config = WorkerClientConfig(
        server_url="http://localhost:8000",
        worker_name="local-api-worker",
        worker_type="playwright",
        workspace_id="workspace-a",
        state_path=tmp_path / "worker_state.json",
    )
    manager = FakeManager()
    app = create_worker_client_app(config, runtime=FakeRuntime(), manager=manager)  # type: ignore[arg-type]

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://worker") as client:
        status = await client.get("/local/status")
        health = await client.get("/local/health")
        started = await client.post("/local/runtime/start")
        heartbeat = await client.post("/local/heartbeat/start")
        logs = await client.get("/local/logs")
        stopped = await client.post("/local/runtime/stop")

    assert status.status_code == 200
    assert "worker_secret" not in status.json()
    assert health.json()["success"] is True
    assert started.json()["runtime_running"] is True
    assert heartbeat.json()["heartbeat_running"] is True
    assert isinstance(logs.json()["lines"], list)
    assert stopped.json()["runtime_running"] is False
