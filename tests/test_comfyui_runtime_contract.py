"""ComfyUI runtime adapter contract tests."""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

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


def test_comfyui_runtime_diagnostics_are_no_network_by_default() -> None:
    """Diagnostics should explain blocked readiness without touching ComfyUI."""

    calls: list[tuple[str, float]] = []
    diagnostics = ComfyUIRuntimeService(
        settings=Settings(),
        http_get=lambda url, timeout: calls.append((url, timeout)) or {},
    ).diagnostics(workspace_id="workspace-comfyui")

    assert diagnostics.success is True
    assert diagnostics.provider == "disabled"
    assert diagnostics.readiness_status == "blocked"
    assert diagnostics.read_only_probe_ready is False
    assert diagnostics.external_request_attempted is False
    assert diagnostics.runtime_calls_enabled is False
    assert diagnostics.raw["no_network_call_performed"] is True
    assert calls == []
    assert any("provider_guarded" in reason for reason in diagnostics.blocking_reasons)
    assert any("COMFYUI_RUNTIME_PROVIDER=guarded" in action for action in diagnostics.recommended_actions)
    assert {check.key for check in diagnostics.diagnostics} >= {
        "provider_guarded",
        "runtime_enabled",
        "network_gate",
        "base_url_scheme",
        "base_url_host_allowlist",
        "read_only_probe_gate",
        "health_path_allowlist",
        "execution_boundary",
    }


def test_comfyui_runtime_diagnostics_report_ready_without_probe_call() -> None:
    """Readiness diagnostics should not run the live read-only probe."""

    settings = Settings(
        COMFYUI_RUNTIME_PROVIDER="guarded",
        COMFYUI_RUNTIME_ENABLED=True,
        COMFYUI_RUNTIME_ALLOW_NETWORK=True,
        COMFYUI_RUNTIME_BASE_URL="http://localhost:8188",
        COMFYUI_RUNTIME_ALLOWED_HOSTS="localhost",
        COMFYUI_RUNTIME_READ_ONLY_PROBE_ENABLED=True,
    )
    calls: list[tuple[str, float]] = []
    diagnostics = ComfyUIRuntimeService(
        settings=settings,
        http_get=lambda url, timeout: calls.append((url, timeout)) or {"status_code": 200},
    ).diagnostics(workspace_id="workspace-comfyui")

    assert diagnostics.provider == "guarded"
    assert diagnostics.readiness_status == "ready_for_read_only_probe"
    assert diagnostics.read_only_probe_ready is True
    assert diagnostics.blocking_reasons == []
    assert diagnostics.recommended_actions == []
    assert diagnostics.external_request_attempted is False
    assert diagnostics.raw["no_network_call_performed"] is True
    assert calls == []
    assert all(check.status == "pass" for check in diagnostics.diagnostics)
    assert "call_comfyui_system_stats_read_only" not in diagnostics.forbidden_actions


def test_comfyui_runtime_maintenance_runbook_is_no_network_and_actionable() -> None:
    """Maintenance runbook should translate diagnostics into operator steps without network calls."""

    calls: list[tuple[str, float]] = []
    runbook = ComfyUIRuntimeService(
        settings=Settings(),
        http_get=lambda url, timeout: calls.append((url, timeout)) or {"status_code": 200},
    ).maintenance_runbook(workspace_id="workspace-comfyui")

    assert runbook.phase == "62E"
    assert runbook.workspace_id == "workspace-comfyui"
    assert runbook.readiness_status == "blocked"
    assert runbook.external_request_attempted is False
    assert runbook.runtime_calls_enabled is False
    assert runbook.raw["no_network_call_performed"] is True
    assert runbook.raw["source_endpoint"] == "/api/v1/comfyui-runtime/diagnostics"
    assert runbook.snapshot_recommended is True
    assert "COMFYUI_RUNTIME_PROVIDER=guarded" in runbook.next_operator_action
    assert any(step.key == "check_provider_guarded" and step.blocking for step in runbook.steps)
    assert any("Save a diagnostic snapshot" in action for action in runbook.recovery_actions)
    assert "submit_prompt" in runbook.disabled_actions
    assert runbook.configuration_summary["provider"] == "disabled"
    assert calls == []


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
async def test_comfyui_runtime_diagnostic_snapshot_persists_without_network(session: AsyncSession) -> None:
    """Persisted diagnostics snapshots should retain readiness state without touching ComfyUI."""

    calls: list[tuple[str, float]] = []
    service = ComfyUIRuntimeService(
        settings=Settings(),
        http_get=lambda url, timeout: calls.append((url, timeout)) or {"status_code": 200},
    )

    snapshot = await service.create_diagnostic_snapshot(
        session,
        workspace_id="workspace-comfyui-snapshots",
        user_id="user-comfyui",
        operator_note="baseline before enabling guarded runtime",
        metadata={"source_page": "comfyui-operations"},
    )
    listed = await service.list_diagnostic_snapshots(
        session,
        workspace_id="workspace-comfyui-snapshots",
        limit=10,
    )

    assert snapshot.workspace_id == "workspace-comfyui-snapshots"
    assert snapshot.user_id == "user-comfyui"
    assert snapshot.readiness_status == "blocked"
    assert snapshot.external_request_attempted is False
    assert snapshot.runtime_calls_enabled is False
    assert snapshot.snapshot_payload["raw"]["no_network_call_performed"] is True
    assert snapshot.metadata["phase"] == "62D"
    assert snapshot.metadata["no_network_call_performed"] is True
    assert snapshot.metadata["source_page"] == "comfyui-operations"
    assert snapshot.operator_note == "baseline before enabling guarded runtime"
    assert len(listed.items) == 1
    assert listed.items[0].id == snapshot.id
    assert calls == []


@pytest.mark.asyncio
async def test_comfyui_runtime_config_change_request_persists_without_network(session: AsyncSession) -> None:
    """Config change requests should record runbook recommendations without mutating runtime settings."""

    calls: list[tuple[str, float]] = []
    service = ComfyUIRuntimeService(
        settings=Settings(),
        http_get=lambda url, timeout: calls.append((url, timeout)) or {"status_code": 200},
    )

    change_request = await service.create_config_change_request(
        session,
        workspace_id="workspace-comfyui-config-requests",
        user_id="user-comfyui",
        change_reason="prepare guarded provider settings for review",
        operator_note="do not apply automatically",
        metadata={"source_page": "comfyui-operations"},
    )
    listed = await service.list_config_change_requests(
        session,
        workspace_id="workspace-comfyui-config-requests",
        limit=10,
    )
    ready = await service.update_config_change_request_status(
        session,
        workspace_id="workspace-comfyui-config-requests",
        request_id=change_request.id,
        status="ready_for_review",
        reviewer_notes="ready for maintainer review",
    )
    approved = await service.update_config_change_request_status(
        session,
        workspace_id="workspace-comfyui-config-requests",
        request_id=change_request.id,
        status="approved_for_manual_apply",
        reviewer_notes="approved for a human maintainer only",
    )
    evidence = await service.create_manual_apply_evidence(
        session,
        workspace_id="workspace-comfyui-config-requests",
        request_id=approved.id,
        user_id="user-comfyui",
        service_restart_reported=True,
        restart_evidence={"restart_mode": "manual_api_restart"},
        rollback_notes="restore previous COMFYUI_RUNTIME_* values if readiness regresses",
        verification_notes="no-network diagnostics captured after manual apply",
        operator_note="human changed env outside the API",
        metadata={"source_page": "comfyui-operations"},
    )
    listed_evidence = await service.list_manual_apply_evidence(
        session,
        workspace_id="workspace-comfyui-config-requests",
        limit=10,
    )
    ready_evidence = await service.update_manual_apply_evidence_status(
        session,
        workspace_id="workspace-comfyui-config-requests",
        evidence_id=evidence.id,
        status="ready_for_review",
        reviewer_notes="ready to verify",
    )
    verified_evidence = await service.update_manual_apply_evidence_status(
        session,
        workspace_id="workspace-comfyui-config-requests",
        evidence_id=evidence.id,
        status="verified",
        reviewer_notes="verified metadata evidence",
    )

    assert change_request.workspace_id == "workspace-comfyui-config-requests"
    assert change_request.user_id == "user-comfyui"
    assert change_request.change_status == "draft"
    assert change_request.readiness_status == "blocked"
    assert change_request.external_request_attempted is False
    assert change_request.runtime_calls_enabled is False
    assert change_request.config_mutation_performed is False
    assert change_request.metadata["phase"] == "62F"
    assert change_request.metadata["no_network_call_performed"] is True
    assert change_request.metadata["config_mutation_performed"] is False
    assert change_request.metadata["source_page"] == "comfyui-operations"
    assert change_request.operator_note == "do not apply automatically"
    assert any(item["source_check"] == "provider_guarded" for item in change_request.requested_changes)
    assert "submit_prompt" in change_request.disabled_actions
    assert change_request.runbook_payload["raw"]["no_network_call_performed"] is True
    assert len(listed.items) == 1
    assert listed.items[0].id == change_request.id
    assert ready.change_status == "ready_for_review"
    assert ready.reviewer_notes == "ready for maintainer review"
    assert ready.config_mutation_performed is False
    assert approved.change_status == "approved_for_manual_apply"
    assert evidence.workspace_id == "workspace-comfyui-config-requests"
    assert evidence.user_id == "user-comfyui"
    assert evidence.config_change_request_id == approved.id
    assert evidence.evidence_status == "draft"
    assert evidence.readiness_status_before == "blocked"
    assert evidence.readiness_status_after == "blocked"
    assert evidence.external_request_attempted is False
    assert evidence.runtime_calls_enabled is False
    assert evidence.api_config_mutation_performed is False
    assert evidence.manual_config_applied is True
    assert evidence.service_restart_reported is True
    assert evidence.metadata["phase"] == "62G"
    assert evidence.metadata["no_network_call_performed"] is True
    assert evidence.metadata["api_config_mutation_performed"] is False
    assert evidence.metadata["source_page"] == "comfyui-operations"
    assert evidence.verification_results["health_probe_executed"] is False
    assert evidence.diagnostics_payload["raw"]["no_network_call_performed"] is True
    assert evidence.operator_note == "human changed env outside the API"
    assert len(listed_evidence.items) == 1
    assert listed_evidence.items[0].id == evidence.id
    assert ready_evidence.evidence_status == "ready_for_review"
    assert verified_evidence.evidence_status == "verified"
    assert verified_evidence.api_config_mutation_performed is False
    assert calls == []


@pytest.mark.asyncio
async def test_comfyui_runtime_contract_api(monkeypatch, session: AsyncSession) -> None:  # type: ignore[no-untyped-def]
    """API should expose health and capabilities without a database or ComfyUI call."""

    settings = Settings()
    monkeypatch.setattr(comfyui_runtime_routes, "get_settings", lambda: settings)

    async def override_get_session():  # type: ignore[no-untyped-def]
        yield session

    app = FastAPI()
    app.add_exception_handler(AppError, app_error_handler)
    app.include_router(comfyui_runtime_routes.router, prefix="/api/v1")
    app.dependency_overrides[comfyui_runtime_routes.get_settings] = lambda: settings
    app.dependency_overrides[comfyui_runtime_routes.get_session] = override_get_session

    headers = {"X-Workspace-Id": "workspace-comfyui-api", "X-User-Id": "user-comfyui"}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        health = await client.get("/api/v1/comfyui-runtime/health", headers=headers)
        capabilities = await client.get("/api/v1/comfyui-runtime/capabilities", headers=headers)
        diagnostics = await client.get("/api/v1/comfyui-runtime/diagnostics", headers=headers)
        runbook = await client.get("/api/v1/comfyui-runtime/maintenance-runbook", headers=headers)
        created_config_request = await client.post(
            "/api/v1/comfyui-runtime/config-change-requests",
            headers=headers,
            json={"change_reason": "api review", "operator_note": "metadata only", "metadata": {"source_page": "comfyui-operations"}},
        )
        config_request_list = await client.get("/api/v1/comfyui-runtime/config-change-requests?limit=5", headers=headers)
        ready_config_request = await client.post(
            f"/api/v1/comfyui-runtime/config-change-requests/{created_config_request.json()['id']}/ready",
            headers=headers,
            json={"reviewer_notes": "send to maintainer"},
        )
        approved_config_request = await client.post(
            f"/api/v1/comfyui-runtime/config-change-requests/{created_config_request.json()['id']}/approve",
            headers=headers,
            json={"reviewer_notes": "approved for manual maintainer apply"},
        )
        created_apply_evidence = await client.post(
            f"/api/v1/comfyui-runtime/config-change-requests/{created_config_request.json()['id']}/manual-apply-evidence",
            headers=headers,
            json={
                "service_restart_reported": True,
                "restart_evidence": {"restart_mode": "manual_api_restart"},
                "rollback_notes": "restore previous runtime env values",
                "verification_notes": "no-network diagnostics captured",
                "operator_note": "operator manually applied approved values",
                "metadata": {"source_page": "comfyui-operations"},
            },
        )
        apply_evidence_list = await client.get("/api/v1/comfyui-runtime/manual-apply-evidence?limit=5", headers=headers)
        ready_apply_evidence = await client.post(
            f"/api/v1/comfyui-runtime/manual-apply-evidence/{created_apply_evidence.json()['id']}/ready",
            headers=headers,
            json={"reviewer_notes": "ready to verify"},
        )
        verified_apply_evidence = await client.post(
            f"/api/v1/comfyui-runtime/manual-apply-evidence/{created_apply_evidence.json()['id']}/verify",
            headers=headers,
            json={"reviewer_notes": "verified"},
        )
        created_snapshot = await client.post(
            "/api/v1/comfyui-runtime/diagnostic-snapshots",
            headers=headers,
            json={"operator_note": "saved from api test", "metadata": {"source_page": "comfyui-operations"}},
        )
        snapshot_list = await client.get("/api/v1/comfyui-runtime/diagnostic-snapshots?limit=5", headers=headers)

    assert health.status_code == 200
    assert health.json()["workspace_id"] == "workspace-comfyui-api"
    assert health.json()["runtime_calls_enabled"] is False
    assert health.json()["read_only_probe_attempted"] is False
    assert capabilities.status_code == 200
    assert "submit_prompt" in capabilities.json()["disabled_actions"]
    assert diagnostics.status_code == 200
    assert diagnostics.json()["workspace_id"] == "workspace-comfyui-api"
    assert diagnostics.json()["external_request_attempted"] is False
    assert diagnostics.json()["readiness_status"] == "blocked"
    assert "provider_guarded" in diagnostics.json()["diagnostics"][0]["key"]
    assert runbook.status_code == 200
    assert runbook.json()["workspace_id"] == "workspace-comfyui-api"
    assert runbook.json()["phase"] == "62E"
    assert runbook.json()["external_request_attempted"] is False
    assert runbook.json()["runtime_calls_enabled"] is False
    assert runbook.json()["steps"][0]["key"] == "check_provider_guarded"
    assert "Save a diagnostic snapshot" in " ".join(runbook.json()["recovery_actions"])
    assert created_config_request.status_code == 200
    assert created_config_request.json()["workspace_id"] == "workspace-comfyui-api"
    assert created_config_request.json()["user_id"] == "user-comfyui"
    assert created_config_request.json()["change_status"] == "draft"
    assert created_config_request.json()["metadata"]["phase"] == "62F"
    assert created_config_request.json()["config_mutation_performed"] is False
    assert created_config_request.json()["external_request_attempted"] is False
    assert config_request_list.status_code == 200
    assert len(config_request_list.json()["items"]) == 1
    assert ready_config_request.status_code == 200
    assert ready_config_request.json()["change_status"] == "ready_for_review"
    assert ready_config_request.json()["config_mutation_performed"] is False
    assert approved_config_request.status_code == 200
    assert approved_config_request.json()["change_status"] == "approved_for_manual_apply"
    assert created_apply_evidence.status_code == 200
    assert created_apply_evidence.json()["workspace_id"] == "workspace-comfyui-api"
    assert created_apply_evidence.json()["user_id"] == "user-comfyui"
    assert created_apply_evidence.json()["evidence_status"] == "draft"
    assert created_apply_evidence.json()["config_change_request_id"] == created_config_request.json()["id"]
    assert created_apply_evidence.json()["service_restart_reported"] is True
    assert created_apply_evidence.json()["external_request_attempted"] is False
    assert created_apply_evidence.json()["runtime_calls_enabled"] is False
    assert created_apply_evidence.json()["api_config_mutation_performed"] is False
    assert created_apply_evidence.json()["metadata"]["phase"] == "62G"
    assert created_apply_evidence.json()["verification_results"]["health_probe_executed"] is False
    assert apply_evidence_list.status_code == 200
    assert len(apply_evidence_list.json()["items"]) == 1
    assert ready_apply_evidence.status_code == 200
    assert ready_apply_evidence.json()["evidence_status"] == "ready_for_review"
    assert verified_apply_evidence.status_code == 200
    assert verified_apply_evidence.json()["evidence_status"] == "verified"
    assert verified_apply_evidence.json()["api_config_mutation_performed"] is False
    assert created_snapshot.status_code == 200
    assert created_snapshot.json()["workspace_id"] == "workspace-comfyui-api"
    assert created_snapshot.json()["user_id"] == "user-comfyui"
    assert created_snapshot.json()["operator_note"] == "saved from api test"
    assert created_snapshot.json()["metadata"]["phase"] == "62D"
    assert created_snapshot.json()["external_request_attempted"] is False
    assert snapshot_list.status_code == 200
    assert snapshot_list.json()["workspace_id"] == "workspace-comfyui-api"
    assert len(snapshot_list.json()["items"]) == 1
    assert snapshot_list.json()["items"][0]["id"] == created_snapshot.json()["id"]
