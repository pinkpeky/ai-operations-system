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

    calls: list[tuple[str, float]] = []
    service = ComfyUIRuntimeService(settings=Settings(), http_get=lambda url, timeout: calls.append((url, timeout)) or {})

    health = service.health_check(workspace_id="workspace-comfyui")
    capabilities = service.capabilities(workspace_id="workspace-comfyui")

    assert health.success is True
    assert health.provider == "disabled"
    assert health.enabled is False
    assert health.reachable is False
    assert health.external_request_attempted is False
    assert health.runtime_calls_enabled is False
    assert health.read_only_probe_enabled is False
    assert health.read_only_probe_attempted is False
    assert health.health_path == "/system_stats"
    assert health.allowed_health_paths == ["/system_stats"]
    assert health.raw["no_network_call_performed"] is True
    assert calls == []
    assert "submit_prompt" in capabilities.disabled_actions
    assert "call_comfyui_system_stats_read_only" in capabilities.disabled_actions
    assert "contract_read" in capabilities.available_actions


def test_comfyui_runtime_contract_normalizes_guarded_config_without_calling_network() -> None:
    """Guarded settings still need the explicit read-only probe switch before network calls."""

    settings = Settings(
        COMFYUI_RUNTIME_PROVIDER="guarded",
        COMFYUI_RUNTIME_ENABLED=True,
        COMFYUI_RUNTIME_ALLOW_NETWORK=True,
        COMFYUI_RUNTIME_BASE_URL="http://localhost:8188",
        COMFYUI_RUNTIME_ALLOWED_HOSTS="localhost",
    )
    calls: list[tuple[str, float]] = []
    health = ComfyUIRuntimeService(
        settings=settings,
        http_get=lambda url, timeout: calls.append((url, timeout)) or {},
    ).health_check(workspace_id="workspace-comfyui")

    assert health.provider == "guarded"
    assert health.enabled is True
    assert health.network_allowed is True
    assert health.reachable is False
    assert health.external_request_attempted is False
    assert health.read_only_probe_enabled is False
    assert health.read_only_probe_attempted is False
    assert health.raw["config_ready_for_read_only_probe"] is True
    assert calls == []
    assert "READ_ONLY_PROBE_ENABLED=false" in str(health.error)


def test_comfyui_runtime_guarded_read_only_probe_calls_allowed_system_stats() -> None:
    """The only live call in Phase 62B is an explicitly enabled read-only health probe."""

    settings = Settings(
        COMFYUI_RUNTIME_PROVIDER="guarded",
        COMFYUI_RUNTIME_ENABLED=True,
        COMFYUI_RUNTIME_ALLOW_NETWORK=True,
        COMFYUI_RUNTIME_BASE_URL="http://localhost:8188",
        COMFYUI_RUNTIME_ALLOWED_HOSTS="localhost",
        COMFYUI_RUNTIME_READ_ONLY_PROBE_ENABLED=True,
        COMFYUI_RUNTIME_TIMEOUT_SECONDS=5,
    )
    calls: list[tuple[str, float]] = []

    def fake_http_get(url: str, timeout: float) -> dict[str, object]:
        calls.append((url, timeout))
        return {"status_code": 200, "json": {"system": {"os": "test"}}, "text": '{"system":{}}'}

    health = ComfyUIRuntimeService(settings=settings, http_get=fake_http_get).health_check(
        workspace_id="workspace-comfyui",
    )
    capabilities = ComfyUIRuntimeService(settings=settings, http_get=fake_http_get).capabilities(
        workspace_id="workspace-comfyui",
    )

    assert calls == [("http://localhost:8188/system_stats", 5.0)]
    assert health.provider == "guarded"
    assert health.reachable is True
    assert health.mock is False
    assert health.external_request_attempted is True
    assert health.runtime_calls_enabled is False
    assert health.read_only_probe_enabled is True
    assert health.read_only_probe_attempted is True
    assert health.probe_status_code == 200
    assert health.probe_latency_ms is not None
    assert health.error is None
    assert health.raw["no_network_call_performed"] is False
    assert health.raw["probe_path"] == "/system_stats"
    assert health.raw["probe_response_summary"]["json_keys"] == ["system"]
    assert "call_comfyui_system_stats_read_only" in capabilities.available_actions
    assert "call_comfyui_system_stats_read_only" not in capabilities.disabled_actions


def test_comfyui_runtime_guarded_read_only_probe_rejects_unlisted_path() -> None:
    """The read-only probe should not call paths outside COMFYUI_RUNTIME_ALLOWED_HEALTH_PATHS."""

    settings = Settings(
        COMFYUI_RUNTIME_PROVIDER="guarded",
        COMFYUI_RUNTIME_ENABLED=True,
        COMFYUI_RUNTIME_ALLOW_NETWORK=True,
        COMFYUI_RUNTIME_BASE_URL="http://localhost:8188",
        COMFYUI_RUNTIME_ALLOWED_HOSTS="localhost",
        COMFYUI_RUNTIME_READ_ONLY_PROBE_ENABLED=True,
        COMFYUI_RUNTIME_HEALTH_PATH="/queue",
        COMFYUI_RUNTIME_ALLOWED_HEALTH_PATHS="/system_stats",
    )
    calls: list[tuple[str, float]] = []
    health = ComfyUIRuntimeService(
        settings=settings,
        http_get=lambda url, timeout: calls.append((url, timeout)) or {"status_code": 200},
    ).health_check(workspace_id="workspace-comfyui")

    assert health.external_request_attempted is False
    assert health.read_only_probe_enabled is True
    assert health.read_only_probe_attempted is False
    assert health.health_path == "/queue"
    assert health.allowed_health_paths == ["/system_stats"]
    assert health.raw["health_path_allowed"] is False
    assert calls == []
    assert "ALLOWED_HEALTH_PATHS" in str(health.error)


def test_comfyui_runtime_guarded_read_only_probe_reports_network_error() -> None:
    """Probe failures should be reported without enabling execution calls."""

    settings = Settings(
        COMFYUI_RUNTIME_PROVIDER="guarded",
        COMFYUI_RUNTIME_ENABLED=True,
        COMFYUI_RUNTIME_ALLOW_NETWORK=True,
        COMFYUI_RUNTIME_BASE_URL="http://localhost:8188",
        COMFYUI_RUNTIME_ALLOWED_HOSTS="localhost",
        COMFYUI_RUNTIME_READ_ONLY_PROBE_ENABLED=True,
    )
    calls: list[tuple[str, float]] = []

    def failing_http_get(url: str, timeout: float) -> dict[str, object]:
        calls.append((url, timeout))
        raise TimeoutError("simulated timeout")

    health = ComfyUIRuntimeService(settings=settings, http_get=failing_http_get).health_check(
        workspace_id="workspace-comfyui",
    )

    assert calls == [("http://localhost:8188/system_stats", 30.0)]
    assert health.reachable is False
    assert health.external_request_attempted is True
    assert health.runtime_calls_enabled is False
    assert health.read_only_probe_attempted is True
    assert health.probe_status_code is None
    assert "TimeoutError" in str(health.error)


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
    assert health.json()["read_only_probe_attempted"] is False
    assert capabilities.status_code == 200
    assert "submit_prompt" in capabilities.json()["disabled_actions"]
