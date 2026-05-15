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
