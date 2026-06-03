"""Standalone browser worker local compatibility API tests."""

from __future__ import annotations

from typing import Any
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from worker.browser_worker.config import WorkerSettings
from worker.main import create_app


ROOT = Path(__file__).resolve().parents[1]


class FakeLocalManager:
    def __init__(self) -> None:
        self.runtime_running = True
        self.heartbeat = False
        self.scheduler: dict[str, Any] = {
            "configured": False,
            "running": False,
            "scheduler_status": "not_configured",
            "scheduler_enabled": False,
            "notification_records": [],
        }

    def mark_runtime_running(self, running: bool, *, error: str | None = None) -> dict[str, Any]:
        self.runtime_running = running
        return {"runtime_running": running, "current_status": "running" if running else "stopped", "last_error": error}

    def runtime_health(self) -> dict[str, Any]:
        return {"success": True, "runtime_running": self.runtime_running, "heartbeat_running": self.heartbeat}

    def start_heartbeat(self) -> dict[str, Any]:
        self.heartbeat = True
        return {"heartbeat_running": True}

    def stop_heartbeat(self) -> dict[str, Any]:
        self.heartbeat = False
        return {"heartbeat_running": False}

    def metric_dispatch_scheduler_state(self) -> dict[str, Any]:
        return self.scheduler

    def configure_metric_dispatch_scheduler(self, payload: dict[str, Any]) -> dict[str, Any]:
        self.scheduler = {
            **self.scheduler,
            "configured": True,
            "scheduler_enabled": bool(payload.get("scheduler_enabled", True)),
            "scheduler_status": str(payload.get("scheduler_status") or "configured"),
            "client_timer_payload": payload.get("client_timer_payload"),
        }
        return self.scheduler

    async def tick_metric_dispatch_scheduler(self, *, force: bool = False) -> dict[str, Any]:
        self.scheduler = {**self.scheduler, "tick_status": "poll_executed", "force": force}
        return self.scheduler

    def start_metric_dispatch_scheduler(self) -> dict[str, Any]:
        self.scheduler = {**self.scheduler, "running": True}
        return self.scheduler

    def stop_metric_dispatch_scheduler(self) -> dict[str, Any]:
        self.scheduler = {**self.scheduler, "running": False}
        return self.scheduler

    def clear_metric_dispatch_scheduler(self) -> dict[str, Any]:
        self.scheduler = {
            "configured": False,
            "running": False,
            "scheduler_status": "not_configured",
            "scheduler_enabled": False,
            "notification_records": [],
        }
        return self.scheduler


@pytest.mark.asyncio
async def test_worker_main_exposes_worker_client_local_compatibility_api(tmp_path) -> None:
    settings = WorkerSettings(
        WORKER_HOST="127.0.0.1",
        WORKER_PORT=9100,
        WORKER_SCREENSHOT_DIR=str(tmp_path / "screenshots"),
        WORKER_PROFILE_DIR=str(tmp_path / "profiles"),
    )
    app = create_app(settings=settings)
    app.state.local_runtime_manager = FakeLocalManager()
    scheduler_payload = {
        "scheduler_status": "scheduled",
        "scheduler_enabled": True,
        "client_timer_payload": {
            "endpoint": "/api/v1/commercial-operations/metric-analysis-dispatch/customer-poll",
            "request_body": {"customer_machine_id": "customer-machine-a"},
        },
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://worker") as client:
        status = await client.get("/local/status")
        preflight = await client.options(
            "/local/status",
            headers={"Origin": "http://127.0.0.1:5174", "Access-Control-Request-Method": "GET"},
        )
        health = await client.get("/local/health")
        openclaw_health = await client.get("/openclaw/health")
        openclaw_capabilities = await client.get("/openclaw/capabilities")
        openclaw_submit = await client.post(
            "/openclaw/actions",
            json={
                "action_type": "publish_submit_guarded",
                "target": "douyin",
                "metadata": {"operator_final_submit_confirmed": True},
            },
        )
        configured = await client.post("/local/metric-dispatch-scheduler/configure", json=scheduler_payload)
        started = await client.post("/local/metric-dispatch-scheduler/start")
        ticked = await client.post("/local/metric-dispatch-scheduler/tick", json={"force": True})
        scheduler = await client.get("/local/metric-dispatch-scheduler")
        logs = await client.get("/local/logs")
        stopped = await client.post("/local/metric-dispatch-scheduler/stop")
        cleared = await client.post("/local/metric-dispatch-scheduler/clear")

    assert status.status_code == 200
    assert preflight.status_code == 200
    assert preflight.headers["access-control-allow-origin"] == "http://127.0.0.1:5174"
    assert status.json()["runtime_running"] is True
    assert status.json()["standalone_browser_worker_compatibility"] is True
    assert health.json()["success"] is True
    assert openclaw_health.status_code == 200
    assert openclaw_health.json()["provider"] == "mock"
    assert openclaw_capabilities.status_code == 200
    assert openclaw_capabilities.json()["capabilities"]["publish_submit_guarded"] is True
    assert openclaw_submit.status_code == 200
    assert openclaw_submit.json()["error"] == "real_publish_provider_not_configured"
    assert openclaw_submit.json()["output_payload"]["actual_publish_performed"] is False
    assert configured.json()["configured"] is True
    assert started.json()["running"] is True
    assert ticked.json()["tick_status"] == "poll_executed"
    assert ticked.json()["force"] is True
    assert scheduler.json()["scheduler_status"] == "scheduled"
    assert isinstance(logs.json()["lines"], list)
    assert stopped.json()["running"] is False
    assert cleared.json()["configured"] is False


def test_phase_68v_standalone_worker_local_compatibility_is_documented() -> None:
    phase_doc = (ROOT / "docs/PHASE_68V_STANDALONE_WORKER_LOCAL_COMPATIBILITY.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")

    for text in (phase_doc, phase_index, current_next):
        assert "Phase 68V Standalone Worker Local Compatibility" in text
        assert "worker.main:app" in text
        assert "/local/metric-dispatch-scheduler" in text
        assert "controlled restart" in text or "service-manager" in text


def test_phase_68w_production_worker_registration_is_documented() -> None:
    phase_doc = (ROOT / "docs/PHASE_68W_PRODUCTION_WORKER_REGISTRATION.md").read_text(encoding="utf-8")
    phase_index = (ROOT / "docs/PHASE_INDEX.md").read_text(encoding="utf-8")
    current_next = (ROOT / "docs/CURRENT_NEXT_PHASE.md").read_text(encoding="utf-8")
    runtime_doc = (ROOT / "docs/BROWSER_WORKER_PRODUCTION_RUNTIME.md").read_text(encoding="utf-8")

    for text in (phase_doc, phase_index, current_next, runtime_doc):
        assert "Phase 68W" in text
        assert "production-workspace" in text
        assert "worker_state.json" in text
        assert "worker_config.yaml" in text
