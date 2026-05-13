"""Worker Client runtime compatibility tests."""

from __future__ import annotations

from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient

from worker.browser_worker.schemas import WorkerActionResponse, WorkerHumanControlResponse, WorkerSessionResponse
from worker_client.config import WorkerClientConfig, WorkerClientState
from worker_client.runtime import create_worker_client_app


class FakeRuntime:
    """轻量 fake runtime，用于验证 API 协议兼容。"""

    async def create_session(self, **_: Any) -> WorkerSessionResponse:
        return WorkerSessionResponse(success=True, remote_session_id="remote-session", message="created", data={"ok": True})

    async def execute_action(self, **kwargs: Any) -> WorkerActionResponse:
        return WorkerActionResponse(success=True, remote_action_id="remote-action", message="action", data={"action_type": kwargs["action_type"]})

    async def close_session(self, *, remote_session_id: str) -> WorkerSessionResponse:
        return WorkerSessionResponse(success=True, remote_session_id=remote_session_id, message="closed", data={})

    async def close_all(self) -> None:
        return None

    async def start_human_control(self, **kwargs: Any) -> WorkerHumanControlResponse:
        return WorkerHumanControlResponse(success=True, remote_session_id=kwargs["remote_session_id"], status="active", message="started")

    async def complete_human_control(self, **kwargs: Any) -> WorkerHumanControlResponse:
        return WorkerHumanControlResponse(success=True, remote_session_id=kwargs["remote_session_id"], status="completed", message="completed")

    async def get_human_control_status(self, *, remote_session_id: str) -> WorkerHumanControlResponse:
        return WorkerHumanControlResponse(success=True, remote_session_id=remote_session_id, status="inactive", message="status")


@pytest.mark.asyncio
async def test_worker_client_runtime_matches_browser_worker_protocol(tmp_path) -> None:
    """worker_client serve API 应兼容现有 browser-worker 协议。"""

    config = WorkerClientConfig(
        server_url="http://ai-server.test",
        worker_name="runtime-worker",
        worker_type="playwright",
        workspace_id="workspace-runtime",
        state_path=tmp_path / "worker_state.json",
        capabilities={"browser": "chromium", "screenshot": True, "page_content": True},
    )
    state = WorkerClientState(
        worker_id="worker-id",
        worker_secret="secret",
        server_url=config.server_url,
        worker_name=config.worker_name,
        workspace_id=config.workspace_id,
        worker_base_url=config.effective_worker_base_url,
    )
    app = create_worker_client_app(config, runtime=FakeRuntime(), state=state)  # type: ignore[arg-type]

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://worker") as client:
        health = await client.get("/health")
        ui = await client.get("/ui-access/capabilities")
        session = await client.post("/sessions", json={"workspace_id": "workspace-runtime", "metadata": {}})
        action = await client.post(
            "/actions",
            json={"remote_session_id": "remote-session", "action_type": "navigate", "target": "https://example.com"},
        )
        close = await client.post("/sessions/remote-session/close")

    assert health.json()["reachable"] is True
    assert ui.json()["placeholder"] is True
    assert session.json()["remote_session_id"] == "remote-session"
    assert action.json()["remote_action_id"] == "remote-action"
    assert close.json()["message"] == "closed"
