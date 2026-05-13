"""Worker Client CLI tests."""

from __future__ import annotations

from worker_client.cli import main
from worker_client.config import WorkerClientState
from worker_client.registration import WorkerRegistrationResult


def test_worker_client_cli_register(monkeypatch, tmp_path, capsys) -> None:
    """CLI register 应输出 worker_id，不输出 secret。"""

    config_path = tmp_path / "worker_config.yaml"
    config_path.write_text(
        """
server_url: http://ai-server.test
worker_name: cli-worker
worker_type: playwright
workspace_id: workspace-cli
state_path: worker_state.json
capabilities:
  browser: chromium
""",
        encoding="utf-8",
    )

    async def fake_register(config, *, force=False, http_client=None):  # type: ignore[no-untyped-def]
        state = WorkerClientState(
            worker_id="cli-worker-id",
            worker_secret="do-not-print",
            server_url=config.server_url,
            worker_name=config.worker_name,
            workspace_id=config.workspace_id,
            worker_base_url=config.effective_worker_base_url,
        )
        return WorkerRegistrationResult(True, "cli-worker-id", state, "ok")

    monkeypatch.setattr("worker_client.cli.register_worker", fake_register)

    assert main(["--config", str(config_path), "register"]) == 0
    output = capsys.readouterr().out
    assert "cli-worker-id" in output
    assert "do-not-print" not in output


def test_worker_client_cli_heartbeat_once(monkeypatch, tmp_path, capsys) -> None:
    """CLI heartbeat --once 应调用一次 heartbeat。"""

    config_path = tmp_path / "worker_config.yaml"
    config_path.write_text(
        """
server_url: http://ai-server.test
worker_name: cli-worker
worker_type: playwright
workspace_id: workspace-cli
state_path: worker_state.json
capabilities:
  browser: chromium
""",
        encoding="utf-8",
    )

    class FakeResult:
        success = True
        worker_id = "worker-id"
        auth_status = "verified"

    async def fake_heartbeat(config, *, status="online", http_client=None):  # type: ignore[no-untyped-def]
        assert status == "busy"
        return FakeResult()

    monkeypatch.setattr("worker_client.cli.send_heartbeat_once", fake_heartbeat)

    assert main(["--config", str(config_path), "heartbeat", "--once", "--status", "busy"]) == 0
    output = capsys.readouterr().out
    assert "auth_status=verified" in output


def test_worker_client_cli_serve_uses_async_server(monkeypatch, tmp_path) -> None:
    """CLI serve 应在当前 event loop 内 await uvicorn.Server.serve。"""

    config_path = tmp_path / "worker_config.yaml"
    state_path = tmp_path / "worker_state.json"
    config_path.write_text(
        f"""
server_url: http://ai-server.test
worker_name: cli-worker
worker_type: playwright
workspace_id: workspace-cli
state_path: {state_path.as_posix()}
capabilities:
  browser: chromium
""",
        encoding="utf-8",
    )
    state_path.write_text(
        """
{
  "worker_id": "worker-id",
  "worker_secret": "do-not-print",
  "server_url": "http://ai-server.test",
  "worker_name": "cli-worker",
  "workspace_id": "workspace-cli",
  "worker_base_url": "http://localhost:9100"
}
""",
        encoding="utf-8",
    )
    served: dict[str, bool] = {"called": False}

    class FakeServer:
        def __init__(self, config):  # type: ignore[no-untyped-def]
            self.config = config

        async def serve(self) -> None:
            served["called"] = True

    monkeypatch.setattr("worker_client.cli.create_worker_client_app", lambda config, state=None, manager=None: object())
    monkeypatch.setattr("worker_client.cli.uvicorn.Server", FakeServer)

    assert main(["--config", str(config_path), "serve", "--host", "127.0.0.1", "--port", "9109"]) == 0
    assert served["called"] is True
