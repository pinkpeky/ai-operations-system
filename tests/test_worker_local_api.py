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
        self.metric_scheduler: dict[str, Any] = {
            "configured": False,
            "running": False,
            "scheduler_status": "not_configured",
            "scheduler_enabled": False,
            "notification_records": [],
        }

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

    def metric_dispatch_scheduler_state(self) -> dict[str, Any]:
        return self.metric_scheduler

    def configure_metric_dispatch_scheduler(self, payload: dict[str, Any]) -> dict[str, Any]:
        self.metric_scheduler = {
            **self.metric_scheduler,
            "configured": True,
            "scheduler_status": payload.get("scheduler_status", "configured"),
            "scheduler_enabled": bool(payload.get("scheduler_enabled", True)),
            "client_timer_payload": payload.get("client_timer_payload", payload),
            "notification_records": payload.get("notification_events", []),
        }
        return self.metric_scheduler

    async def tick_metric_dispatch_scheduler(self, *, force: bool = False) -> dict[str, Any]:
        self.metric_scheduler = {**self.metric_scheduler, "tick_status": "poll_executed", "force": force}
        return self.metric_scheduler

    def start_metric_dispatch_scheduler(self) -> dict[str, Any]:
        self.metric_scheduler = {**self.metric_scheduler, "running": True}
        return self.metric_scheduler

    def stop_metric_dispatch_scheduler(self) -> dict[str, Any]:
        self.metric_scheduler = {**self.metric_scheduler, "running": False}
        return self.metric_scheduler

    def clear_metric_dispatch_scheduler(self) -> dict[str, Any]:
        self.metric_scheduler = {
            "configured": False,
            "running": False,
            "scheduler_status": "not_configured",
            "scheduler_enabled": False,
            "notification_records": [],
        }
        return self.metric_scheduler


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
        scheduler_payload = {
            "scheduler_status": "scheduled",
            "scheduler_enabled": True,
            "client_timer_payload": {
                "endpoint": "/api/v1/commercial-operations/metric-analysis-dispatch/customer-poll",
                "request_body": {"customer_machine_id": "customer-machine-a"},
            },
            "notification_events": [{"event_type": "ready"}],
        }
        scheduler_configured = await client.post("/local/metric-dispatch-scheduler/configure", json=scheduler_payload)
        scheduler_started = await client.post("/local/metric-dispatch-scheduler/start")
        scheduler_tick = await client.post("/local/metric-dispatch-scheduler/tick", json={"force": True})
        scheduler_state = await client.get("/local/metric-dispatch-scheduler")
        scheduler_stopped = await client.post("/local/metric-dispatch-scheduler/stop")
        scheduler_cleared = await client.post("/local/metric-dispatch-scheduler/clear")
        logs = await client.get("/local/logs")
        stopped = await client.post("/local/runtime/stop")

    assert status.status_code == 200
    assert "worker_secret" not in status.json()
    assert health.json()["success"] is True
    assert started.json()["runtime_running"] is True
    assert heartbeat.json()["heartbeat_running"] is True
    assert scheduler_configured.json()["configured"] is True
    assert scheduler_started.json()["running"] is True
    assert scheduler_tick.json()["tick_status"] == "poll_executed"
    assert scheduler_tick.json()["force"] is True
    assert scheduler_state.json()["notification_records"][0]["event_type"] == "ready"
    assert scheduler_stopped.json()["running"] is False
    assert scheduler_cleared.json()["configured"] is False
    assert isinstance(logs.json()["lines"], list)
    assert stopped.json()["runtime_running"] is False
