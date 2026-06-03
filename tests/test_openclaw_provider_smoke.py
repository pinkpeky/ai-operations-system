"""OpenClaw provider readiness smoke script tests."""

from __future__ import annotations

import httpx
import pytest

from scripts.check_openclaw_provider import build_report


@pytest.mark.asyncio
async def test_openclaw_provider_smoke_passes_real_guarded_provider() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/openclaw/provider-diagnostics":
            return httpx.Response(
                200,
                json={
                    "success": True,
                    "provider": "openclaw_http",
                    "enabled": True,
                    "mock": False,
                    "configured": True,
                    "readiness_status": "openclaw_provider_configured_pending_capability_check",
                },
            )
        if request.url.path == "/openclaw/health":
            return httpx.Response(
                200,
                json={"success": True, "provider": "real", "reachable": True, "enabled": True, "mock": False},
            )
        if request.url.path == "/openclaw/capabilities":
            return httpx.Response(
                200,
                json={
                    "success": True,
                    "provider": "real",
                    "mock": False,
                    "capabilities": {"real_publish_submit": True, "publish_submit_guarded": True},
                    "actions": ["publish_submit_guarded"],
                },
            )
        return httpx.Response(404, json={})

    report = await build_report(
        base_url="http://worker.test",
        transport=httpx.MockTransport(handler),
    )

    assert report["success"] is True
    assert report["contract"] == "openclaw_provider_readiness_smoke"
    assert report["server_side_external_execution"] is False
    assert report["actual_publish_performed"] is False


@pytest.mark.asyncio
async def test_openclaw_provider_smoke_blocks_mock_provider() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/openclaw/provider-diagnostics":
            return httpx.Response(
                200,
                json={
                    "success": False,
                    "provider": "mock",
                    "enabled": True,
                    "mock": True,
                    "configured": False,
                    "readiness_status": "openclaw_provider_is_mock",
                },
            )
        if request.url.path == "/openclaw/health":
            return httpx.Response(
                200,
                json={"success": True, "provider": "mock", "reachable": True, "enabled": True, "mock": True},
            )
        if request.url.path == "/openclaw/capabilities":
            return httpx.Response(
                200,
                json={
                    "success": True,
                    "provider": "mock",
                    "mock": True,
                    "capabilities": {"real_publish_submit": False, "publish_submit_guarded": True},
                    "actions": ["publish_submit_guarded"],
                },
            )
        return httpx.Response(404, json={})

    report = await build_report(
        base_url="http://worker.test",
        transport=httpx.MockTransport(handler),
    )

    assert report["success"] is False
    assert "openclaw_provider_is_mock" in report["blocking_reasons"]
    assert "openclaw_health_not_ready" in report["blocking_reasons"]
    assert "openclaw_capabilities_not_ready" in report["blocking_reasons"]
