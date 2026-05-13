"""Worker Runtime Manager tests."""

from __future__ import annotations

import time
from dataclasses import dataclass

from worker_client.config import WorkerClientConfig, WorkerClientState, save_worker_state
from worker_client.runtime_manager import WorkerRuntimeManager


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
