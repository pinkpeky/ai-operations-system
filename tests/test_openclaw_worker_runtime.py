"""worker_client OpenClaw runtime API tests."""

import pytest
import httpx
from httpx import ASGITransport, AsyncClient

from worker_client.config import WorkerClientConfig
from worker_client.openclaw.http_provider import HttpOpenClawProvider
from worker_client.openclaw.schemas import OpenClawActionRequest
from worker_client.runtime import create_worker_client_app


@pytest.mark.asyncio
async def test_worker_client_runtime_openclaw_routes() -> None:
    """worker_client serve app 应暴露 /openclaw/* mock routes。"""

    config = WorkerClientConfig(
        server_url="http://localhost:8000",
        worker_name="test-worker",
        worker_type="playwright",
        workspace_id="workspace-openclaw-runtime",
        capabilities={"browser": "chromium", "openclaw": True},
    )
    app = create_worker_client_app(config)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://worker") as client:
        health = await client.get("/openclaw/health")
        capabilities = await client.get("/openclaw/capabilities")
        diagnostics = await client.get("/openclaw/provider-diagnostics")
        action = await client.post(
            "/openclaw/actions",
            json={"action_type": "mock_inspect", "target": "https://example.com", "input_payload": {"x": 1}},
        )
        publish_submit = await client.post(
            "/openclaw/actions",
            json={
                "action_type": "publish_submit_guarded",
                "target": "douyin",
                "metadata": {"operator_final_submit_confirmed": True},
            },
        )

    assert health.status_code == 200
    assert health.json()["provider"] == "mock"
    assert diagnostics.status_code == 200
    assert diagnostics.json()["contract"] == "openclaw_provider_configuration_preflight"
    assert diagnostics.json()["readiness_status"] == "openclaw_provider_is_mock"
    assert diagnostics.json()["missing_config"] == ["WORKER_CLIENT_OPENCLAW_PROVIDER"]
    assert "WORKER_CLIENT_OPENCLAW_API_KEY" in diagnostics.json()["secret_fields_redacted"]
    assert capabilities.json()["capabilities"]["real_openclaw"] is False
    assert capabilities.json()["capabilities"]["publish_dry_run"] is True
    assert capabilities.json()["capabilities"]["publish_submit_guarded"] is True
    assert capabilities.json()["capabilities"]["real_publish_submit"] is False
    assert action.json()["success"] is True
    assert action.json()["output_payload"]["real_openclaw_called"] is False
    assert action.json()["output_payload"]["actual_publish_performed"] is False
    assert publish_submit.json()["success"] is False
    assert publish_submit.json()["error"] == "real_publish_provider_not_configured"
    assert publish_submit.json()["output_payload"]["actual_publish_performed"] is False
    assert publish_submit.json()["output_payload"]["requires_real_openclaw_provider"] is True


@pytest.mark.asyncio
async def test_worker_client_runtime_openclaw_http_provider_missing_base_url_is_not_mock() -> None:
    config = WorkerClientConfig(
        server_url="http://localhost:8000",
        worker_name="test-worker",
        worker_type="playwright",
        workspace_id="workspace-openclaw-runtime",
        capabilities={"browser": "chromium", "openclaw": True},
        openclaw={"enabled": True, "provider": "openclaw_http", "base_url": ""},
    )
    app = create_worker_client_app(config)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://worker") as client:
        health = await client.get("/openclaw/health")
        capabilities = await client.get("/openclaw/capabilities")
        diagnostics = await client.get("/openclaw/provider-diagnostics")
        publish_submit = await client.post(
            "/openclaw/actions",
            json={
                "action_type": "publish_submit_guarded",
                "target": "douyin",
                "metadata": {"operator_final_submit_confirmed": True},
            },
        )

    assert health.json()["provider"] == "openclaw_http"
    assert health.json()["mock"] is False
    assert health.json()["success"] is False
    assert health.json()["error"] == "openclaw_http_base_url_required"
    assert diagnostics.json()["provider"] == "openclaw_http"
    assert diagnostics.json()["mock"] is False
    assert diagnostics.json()["success"] is False
    assert diagnostics.json()["readiness_status"] == "openclaw_http_base_url_required"
    assert diagnostics.json()["base_url_configured"] is False
    assert diagnostics.json()["missing_config"] == ["WORKER_CLIENT_OPENCLAW_BASE_URL"]
    assert capabilities.json()["mock"] is False
    assert capabilities.json()["capabilities"]["real_publish_submit"] is False
    assert publish_submit.json()["mock"] is False
    assert publish_submit.json()["success"] is False
    assert publish_submit.json()["error"] == "openclaw_http_base_url_required"
    assert publish_submit.json()["output_payload"]["actual_publish_performed"] is False


@pytest.mark.asyncio
async def test_http_openclaw_provider_accepts_real_submit_evidence() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["authorization"] == "Bearer test-secret"
        if request.url.path == "/openclaw/health":
            return httpx.Response(
                200,
                json={
                    "success": True,
                    "provider": "real-openclaw",
                    "reachable": True,
                    "enabled": True,
                    "mock": False,
                    "version": "real-1",
                },
            )
        if request.url.path == "/openclaw/capabilities":
            return httpx.Response(
                200,
                json={
                    "success": True,
                    "provider": "real-openclaw",
                    "mock": False,
                    "capabilities": {
                        "openclaw": True,
                        "real_openclaw": True,
                        "platform_automation": True,
                        "publish_dry_run": True,
                        "publish_submit_guarded": True,
                        "real_publish_submit": True,
                    },
                    "actions": ["publish_dry_run", "publish_submit_guarded"],
                },
            )
        if request.url.path == "/openclaw/actions":
            return httpx.Response(
                200,
                json={
                    "success": True,
                    "action_type": "publish_submit_guarded",
                    "provider": "real-openclaw",
                    "mock": False,
                    "duration_ms": 12,
                    "output_payload": {
                        "real_openclaw_called": True,
                        "actual_publish_performed": True,
                        "platform_content_id": "douyin-item-1",
                    },
                },
            )
        return httpx.Response(404, json={"error": "missing"})

    provider = HttpOpenClawProvider(
        provider_name="openclaw_http",
        base_url="http://openclaw.local",
        api_key="test-secret",
        transport=httpx.MockTransport(handler),
    )

    health = await provider.health_check()
    capabilities = await provider.list_capabilities()
    submit = await provider.execute_action(
        OpenClawActionRequest(
            action_type="publish_submit_guarded",
            target="douyin",
            metadata={"operator_final_submit_confirmed": True},
        )
    )

    assert health.success is True
    assert health.mock is False
    assert capabilities.capabilities["real_publish_submit"] is True
    assert submit.success is True
    assert submit.mock is False
    assert submit.output_payload["actual_publish_performed"] is True
    assert submit.output_payload["real_openclaw_called"] is True


@pytest.mark.asyncio
async def test_http_openclaw_provider_rejects_submit_without_real_evidence() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "success": True,
                "action_type": "publish_submit_guarded",
                "provider": "real-openclaw",
                "mock": False,
                "duration_ms": 5,
                "output_payload": {"platform_content_id": "missing-real-evidence"},
            },
        )

    provider = HttpOpenClawProvider(
        provider_name="openclaw_http",
        base_url="http://openclaw.local",
        transport=httpx.MockTransport(handler),
    )

    submit = await provider.execute_action(
        OpenClawActionRequest(action_type="publish_submit_guarded", target="douyin")
    )

    assert submit.success is False
    assert submit.mock is False
    assert submit.error == "real_publish_evidence_missing_from_provider"
    assert submit.output_payload["actual_publish_performed"] is False
