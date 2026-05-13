"""Worker Client local logging tests."""

from __future__ import annotations

import logging

from worker_client.logging import configure_worker_logging, get_recent_logs, log_event


def test_worker_local_logging_writes_rotating_log_and_redacts(tmp_path) -> None:
    """本地日志应写入 worker.log，并对 secret 字段做轻量脱敏。"""

    path = tmp_path / "worker.log"
    logger = configure_worker_logging(path, level=logging.INFO, max_bytes=1024, backup_count=1)
    logger.info("runtime started")
    log_event("register completed", extra={"worker_id": "worker-1", "worker_secret": "hidden"})

    lines = get_recent_logs(10, path)

    assert any("runtime started" in line for line in lines)
    assert any("register completed" in line for line in lines)
    assert "hidden" not in "\n".join(lines)
