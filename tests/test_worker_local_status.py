"""Worker Client local status tests."""

from __future__ import annotations

from worker_client.status import clear_status, get_status, update_status, write_status


def test_worker_local_status_roundtrip_and_redacts_secret(tmp_path) -> None:
    """本地 status 文件应可读写，并且不能保留 worker_secret。"""

    path = tmp_path / "status.json"

    write_status({"worker_id": "worker-1", "worker_secret": "secret"}, path)
    loaded = get_status(path)

    assert loaded["worker_id"] == "worker-1"
    assert "worker_secret" not in loaded

    updated = update_status({"runtime_running": True, "current_status": "running"}, path)
    assert updated["runtime_running"] is True
    assert get_status(path)["current_status"] == "running"

    cleared = clear_status(path)
    assert cleared["registered"] is False
    assert not path.exists()


def test_worker_local_status_recovers_from_corrupt_json(tmp_path) -> None:
    """Corrupt local status must not block worker registration or heartbeat."""

    path = tmp_path / "status.json"
    path.write_text('{"worker_id": "worker-1"} trailing', encoding="utf-8")

    loaded = get_status(path)
    assert loaded["registered"] is False
    assert loaded["current_status"] == "stopped"
    assert loaded["last_error"] == "status file unreadable: JSONDecodeError"

    updated = update_status({"registered": True, "worker_id": "worker-2"}, path)
    assert updated["registered"] is True
    assert updated["worker_id"] == "worker-2"
    assert get_status(path)["worker_id"] == "worker-2"
