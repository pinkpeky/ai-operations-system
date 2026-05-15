"""Worker Client registration tests."""

from __future__ import annotations

import json

import httpx
import pytest

from worker_client.config import WorkerClientConfig, load_worker_state
from worker_client.registration import register_worker


@pytest.mark.asyncio
async def test_worker_client_register_saves_state(tmp_path) -> None:
    """register 应调用 AI Server 并把 worker_id/worker_secret 保存到本地 state。"""

    state_path = tmp_path / "worker_state.json"
    config = WorkerClientConfig(
        server_url="http://ai-server.test",
        worker_name="customer-worker",
        worker_type="playwright",
        workspace_id="workspace-a",
        worker_base_url="http://customer-machine:9100",
        state_path=state_path,
        capabilities={"browser": "chromium", "screenshot": True},
    )

    async def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content.decode("utf-8"))
        assert request.headers["X-Workspace-Id"] == "workspace-a"
        assert body["worker_name"] == "customer-worker"
        assert body["base_url"] == "http://customer-machine:9100"
        assert "worker_secret" not in body
        return httpx.Response(201, json={"id": "worker-id-1", "worker_secret": "secret-once"})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        result = await register_worker(config, http_client=client)

    loaded = load_worker_state(state_path)
    assert result.registered is True
    assert result.worker_id == "worker-id-1"
    assert loaded is not None
    assert loaded.worker_secret == "secret-once"
    assert loaded.worker_base_url == "http://customer-machine:9100"


@pytest.mark.asyncio
async def test_worker_client_register_reuses_existing_state(tmp_path) -> None:
    """已有 state 时默认不重复注册。"""

    state_path = tmp_path / "worker_state.json"
    state_path.write_text(
        json.dumps(
            {
                "worker_id": "existing-worker",
                "worker_secret": "secret",
                "server_url": "http://ai-server.test",
                "worker_name": "worker",
                "workspace_id": "workspace",
                "worker_base_url": "http://localhost:9100",
            }
        ),
        encoding="utf-8",
    )
    config = WorkerClientConfig(
        server_url="http://ai-server.test",
        worker_name="worker",
        worker_type="playwright",
        workspace_id="workspace",
        state_path=state_path,
    )

    result = await register_worker(config)

    assert result.registered is False
    assert result.worker_id == "existing-worker"


@pytest.mark.asyncio
async def test_worker_client_register_refreshes_state_when_base_url_changed(tmp_path) -> None:
    """配置中的 worker_base_url 变化时不能复用旧 state，否则 Server 会继续访问旧地址。"""

    state_path = tmp_path / "worker_state.json"
    state_path.write_text(
        json.dumps(
            {
                "worker_id": "existing-worker",
                "worker_secret": "old-secret",
                "server_url": "http://ai-server.test",
                "worker_name": "worker",
                "workspace_id": "workspace",
                "worker_base_url": "http://127.0.0.1:9100",
            }
        ),
        encoding="utf-8",
    )
    config = WorkerClientConfig(
        server_url="http://ai-server.test",
        worker_name="worker",
        worker_type="playwright",
        workspace_id="workspace",
        worker_base_url="http://10.16.188.11:9100",
        state_path=state_path,
    )

    async def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content.decode("utf-8"))
        assert body["base_url"] == "http://10.16.188.11:9100"
        return httpx.Response(201, json={"id": "refreshed-worker", "worker_secret": "new-secret"})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        result = await register_worker(config, http_client=client)

    loaded = load_worker_state(state_path)
    assert result.registered is True
    assert result.worker_id == "refreshed-worker"
    assert loaded is not None
    assert loaded.worker_secret == "new-secret"
    assert loaded.worker_base_url == "http://10.16.188.11:9100"
