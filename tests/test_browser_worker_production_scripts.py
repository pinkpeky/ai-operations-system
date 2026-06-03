"""Browser worker production script guardrails."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_browser_worker_start_script_supervises_heartbeat_loop() -> None:
    script = (ROOT / "deployment/windows/start_browser_worker_aiops.ps1").read_text(encoding="utf-8")
    task = (ROOT / "deployment/windows/register_browser_worker_aiops_task.ps1").read_text(encoding="utf-8")

    for token in [
        "SkipHeartbeat",
        "Start-WorkerHeartbeatLoop",
        "worker_client.cli",
        "heartbeat",
        "browser_worker_heartbeat_stdout.log",
        "browser_worker_heartbeat_stderr.log",
        "Browser worker already responds",
    ]:
        assert token in script

    assert "Start strict signed Browser Worker and heartbeat loop" in task


def test_browser_worker_compose_shares_runtime_state_with_supervised_heartbeat() -> None:
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")

    assert "./worker_client/runtime_state:/app/worker_client/runtime_state" in compose
    assert "./worker_client/worker_state.json:/app/worker_client/worker_state.json:ro" in compose
