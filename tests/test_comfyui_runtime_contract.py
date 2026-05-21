"""ComfyUI runtime adapter contract tests."""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api.routes import comfyui_runtime as comfyui_runtime_routes
from app.comfyui_runtime import ComfyUIRuntimeService
from app.core.config import Settings
from app.core.errors import AppError, app_error_handler


def test_comfyui_runtime_contract_is_disabled_by_default() -> None:
    """Default runtime contract should be visible but non-executing."""

    service = ComfyUIRuntimeService(settings=Settings())

    health = service.health_check(workspace_id="workspace-comfyui")
    capabilities = service.capabilities(workspace_id="workspace-comfyui")

    assert health.success is True
    assert health.provider == "disabled"
    assert health.enabled is False
    assert health.reachable is False
    assert health.external_request_attempted is False
    assert health.runtime_calls_enabled is False
    assert health.raw["no_network_call_performed"] is True
    assert "submit_prompt" in capabilities.disabled_actions
    assert "contract_read" in capabilities.available_actions


def test_comfyui_runtime_contract_normalizes_guarded_config_without_calling_network() -> None:
    """Even guarded settings should not perform a live ComfyUI probe in Phase 62A."""

    settings = Settings(
        COMFYUI_RUNTIME_PROVIDER="guarded",
        COMFYUI_RUNTIME_ENABLED=True,
        COMFYUI_RUNTIME_ALLOW_NETWORK=True,
        COMFYUI_RUNTIME_BASE_URL="http://localhost:8188",
        COMFYUI_RUNTIME_ALLOWED_HOSTS="localhost",
    )
    health = ComfyUIRuntimeService(settings=settings).health_check(workspace_id="workspace-comfyui")

    assert health.provider == "guarded"
    assert health.enabled is True
    assert health.network_allowed is True
    assert health.reachable is False
    assert health.external_request_attempted is False
    assert health.raw["config_ready_for_future_probe"] is True
    assert "not implemented in Phase 62A" in str(health.error)


@pytest.mark.asyncio
async def test_comfyui_runtime_contract_api(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """API should expose health and capabilities without a database or ComfyUI call."""

    settings = Settings()
    monkeypatch.setattr(comfyui_runtime_routes, "get_settings", lambda: settings)

    app = FastAPI()
    app.add_exception_handler(AppError, app_error_handler)
    app.include_router(comfyui_runtime_routes.router, prefix="/api/v1")
    app.dependency_overrides[comfyui_runtime_routes.get_settings] = lambda: settings

    headers = {"X-Workspace-Id": "workspace-comfyui-api", "X-User-Id": "user-comfyui"}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        health = await client.get("/api/v1/comfyui-runtime/health", headers=headers)
        capabilities = await client.get("/api/v1/comfyui-runtime/capabilities", headers=headers)

    assert health.status_code == 200
    assert health.json()["workspace_id"] == "workspace-comfyui-api"
    assert health.json()["runtime_calls_enabled"] is False
    assert capabilities.status_code == 200
    assert "submit_prompt" in capabilities.json()["disabled_actions"]
