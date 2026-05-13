"""Worker Client config tests."""

from __future__ import annotations

from worker_client.config import load_worker_client_config, load_worker_state, save_worker_state, WorkerClientState


def test_worker_client_config_loads_yaml_and_env_override(tmp_path, monkeypatch) -> None:
    """Worker Client 应从 yaml 读取配置，并支持 env override。"""

    config_path = tmp_path / "worker_config.yaml"
    state_path = tmp_path / "worker_state.json"
    config_path.write_text(
        """
server_url: http://localhost:8000
worker_name: yaml-worker
worker_type: playwright
workspace_id: yaml-workspace
state_path: STATE_PATH_PLACEHOLDER
heartbeat_interval_seconds: 15
capabilities:
  browser: chromium
  screenshot: true
  page_content: true
  persistent_profile: true
""".replace("STATE_PATH_PLACEHOLDER", str(state_path).replace("\\", "/")),
        encoding="utf-8",
    )
    monkeypatch.setenv("WORKER_CLIENT_WORKER_NAME", "env-worker")
    monkeypatch.setenv("WORKER_CLIENT_RUNTIME_PORT", "9200")

    config = load_worker_client_config(config_path)

    assert config.worker_name == "env-worker"
    assert config.runtime_port == 9200
    assert config.effective_worker_base_url == "http://localhost:9200"
    assert config.capabilities["persistent_profile"] is True
    assert config.state_path == state_path


def test_worker_client_state_redacts_secret(tmp_path) -> None:
    """本地 state 能保存 secret，但 redacted 输出不能泄露 secret。"""

    state = WorkerClientState(
        worker_id="worker-1",
        worker_secret="secret-value",
        server_url="http://localhost:8000",
        worker_name="worker",
        workspace_id="workspace",
        worker_base_url="http://localhost:9100",
    )
    path = tmp_path / "worker_state.json"
    save_worker_state(path, state)
    loaded = load_worker_state(path)

    assert loaded is not None
    assert loaded.worker_secret == "secret-value"
    assert loaded.redacted()["worker_secret"] == "***"

