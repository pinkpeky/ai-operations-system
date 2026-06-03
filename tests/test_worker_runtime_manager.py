"""Worker Runtime Manager tests."""

from __future__ import annotations

import time
from dataclasses import dataclass

from worker_client.config import WorkerClientConfig, WorkerClientState, save_worker_state
from worker_client.metric_dispatch_scheduler import EXPECTED_POLL_ENDPOINT
from worker_client.runtime_manager import WorkerRuntimeManager
from worker_client.status import update_status


@dataclass(slots=True)
class FakeHeartbeatResult:
    success: bool = True
    status_code: int = 200
    worker_id: str = "worker-1"
    auth_status: str = "verified"
    response: dict[str, str] | None = None


def test_worker_runtime_manager_tracks_runtime_state(tmp_path) -> None:
    """Runtime Manager 应汇总 runtime / heartbeat / state 信息，且不泄露 secret。"""

    state_path = tmp_path / "worker_state.json"
    status_path = tmp_path / "status.json"
    config = WorkerClientConfig(
        server_url="http://localhost:8000",
        worker_name="manager-worker",
        worker_type="playwright",
        workspace_id="workspace-a",
        state_path=state_path,
    )
    save_worker_state(
        state_path,
        WorkerClientState(
            worker_id="worker-1",
            worker_secret="secret",
            server_url=config.server_url,
            worker_name=config.worker_name,
            workspace_id=config.workspace_id,
            worker_base_url=config.effective_worker_base_url,
        ),
    )
    manager = WorkerRuntimeManager(config, status_path=str(status_path))

    manager.mark_runtime_running(True)
    state = manager.runtime_state()

    assert state["worker_id"] == "worker-1"
    assert state["runtime_running"] is True
    assert "worker_secret" not in state
    assert manager.runtime_health()["localhost_only"] is True

    manager.mark_runtime_running(False)
    assert manager.runtime_state()["runtime_running"] is False


def test_worker_runtime_manager_heartbeat_thread(monkeypatch, tmp_path) -> None:
    """Heartbeat 应能以独立线程启动和停止。"""

    state_path = tmp_path / "worker_state.json"
    status_path = tmp_path / "status.json"
    config = WorkerClientConfig(
        server_url="http://localhost:8000",
        worker_name="manager-worker",
        worker_type="playwright",
        workspace_id="workspace-a",
        state_path=state_path,
        heartbeat_interval_seconds=30,
    )
    save_worker_state(
        state_path,
        WorkerClientState(
            worker_id="worker-1",
            worker_secret="secret",
            server_url=config.server_url,
            worker_name=config.worker_name,
            workspace_id=config.workspace_id,
            worker_base_url=config.effective_worker_base_url,
        ),
    )

    async def fake_send_heartbeat_once(config, *, status="online"):  # type: ignore[no-untyped-def]
        return FakeHeartbeatResult(response={"ok": "true"})

    monkeypatch.setattr("worker_client.runtime_manager.send_heartbeat_once", fake_send_heartbeat_once)
    manager = WorkerRuntimeManager(config, status_path=str(status_path))

    manager.start_heartbeat()
    time.sleep(0.05)
    assert manager.runtime_state()["heartbeat_running"] is True
    manager.stop_heartbeat()
    assert manager.runtime_state()["heartbeat_running"] is False


def test_worker_runtime_manager_preserves_external_heartbeat_status(tmp_path) -> None:
    """Runtime status writes should not clear a separate supervised heartbeat loop."""

    state_path = tmp_path / "worker_state.json"
    status_path = tmp_path / "status.json"
    config = WorkerClientConfig(
        server_url="http://localhost:8000",
        worker_name="manager-worker",
        worker_type="playwright",
        workspace_id="workspace-a",
        state_path=state_path,
    )
    save_worker_state(
        state_path,
        WorkerClientState(
            worker_id="worker-1",
            worker_secret="secret",
            server_url=config.server_url,
            worker_name=config.worker_name,
            workspace_id=config.workspace_id,
            worker_base_url=config.effective_worker_base_url,
        ),
    )
    update_status({"heartbeat_running": True, "current_status": "online"}, status_path)
    manager = WorkerRuntimeManager(config, status_path=str(status_path))

    manager.mark_runtime_running(True)
    state = manager.runtime_state()

    assert state["runtime_running"] is True
    assert state["heartbeat_running"] is True
    assert manager.runtime_health()["heartbeat_running"] is True

    manager.stop_heartbeat()
    assert manager.runtime_state()["heartbeat_running"] is False


def test_worker_runtime_manager_tracks_metric_dispatch_scheduler(tmp_path) -> None:
    """Runtime Manager should expose local metric dispatch scheduler lifecycle state."""

    state_path = tmp_path / "worker_state.json"
    status_path = tmp_path / "status.json"
    config = WorkerClientConfig(
        server_url="http://localhost:8000",
        worker_name="manager-worker",
        worker_type="playwright",
        workspace_id="workspace-a",
        state_path=state_path,
    )
    manager = WorkerRuntimeManager(config, status_path=str(status_path))
    payload = {
        "scheduler_status": "scheduled",
        "scheduler_enabled": False,
        "client_timer_payload": {
            "endpoint": EXPECTED_POLL_ENDPOINT,
            "request_body": {"customer_machine_id": "manager-worker"},
        },
    }

    configured = manager.configure_metric_dispatch_scheduler(payload)
    started = manager.start_metric_dispatch_scheduler()
    stopped = manager.stop_metric_dispatch_scheduler()
    cleared = manager.clear_metric_dispatch_scheduler()

    assert configured["configured"] is True
    assert started["tick_status"] == "disabled"
    assert stopped["running"] is False
    assert cleared["configured"] is False
    assert manager.runtime_state()["metric_dispatch_scheduler_running"] is False
