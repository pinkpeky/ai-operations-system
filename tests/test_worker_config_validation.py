"""Worker Client config validation tests."""

from __future__ import annotations

import pytest

from worker_client.config import WorkerClientConfig


def test_worker_config_validation_accepts_valid_config() -> None:
    """合法配置应能通过启动前校验。"""

    config = WorkerClientConfig(
        server_url="http://localhost:8000",
        worker_name="local-worker",
        worker_type="playwright",
        workspace_id="workspace-a",
    )

    config.validate_config()


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("server_url", "localhost:8000", "server_url"),
        ("worker_name", "", "worker_name"),
        ("workspace_id", "workspace a", "workspace_id"),
        ("runtime_port", 70000, "runtime_port"),
    ],
)
def test_worker_config_validation_rejects_invalid_config(field: str, value: object, message: str) -> None:
    """非法配置应返回清晰错误。"""

    config = WorkerClientConfig(
        server_url="http://localhost:8000",
        worker_name="local-worker",
        worker_type="playwright",
        workspace_id="workspace-a",
    )
    setattr(config, field, value)

    with pytest.raises(ValueError, match=message):
        config.validate_config()
