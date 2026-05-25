"""ComfyUI runtime adapter contract tests."""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes import comfyui_runtime as comfyui_runtime_routes
from app.comfyui_runtime import ComfyUIRuntimeService
from app.core.config import Settings, get_settings
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


def test_comfyui_runtime_prompt_submission_is_blocked_by_default() -> None:
    """Real prompt submission should stay disabled until explicit runtime gates are enabled."""

    post_calls: list[tuple[str, dict[str, object], float]] = []
    service = ComfyUIRuntimeService(
        settings=Settings(),
        http_post=lambda url, payload, timeout: post_calls.append((url, dict(payload), timeout)) or {},
    )

    result = service.submit_prompt_job(
        workspace_id="workspace-comfyui",
        prompt={"1": {"class_type": "CheckpointLoaderSimple"}},
        metadata={"source": "test"},
    )

    assert result.success is False
    assert result.external_request_attempted is False
    assert result.runtime_calls_enabled is False
    assert result.prompt_submission_enabled is False
    assert "COMFYUI_RUNTIME_PROVIDER=guarded" in str(result.error)
    assert post_calls == []


def test_comfyui_runtime_prompt_submission_calls_real_prompt_endpoint_when_enabled() -> None:
    """The guarded adapter should submit /prompt and read /history plus /queue when every gate is enabled."""

    settings = Settings(
        COMFYUI_RUNTIME_PROVIDER="guarded",
        COMFYUI_RUNTIME_ENABLED=True,
        COMFYUI_RUNTIME_ALLOW_NETWORK=True,
        COMFYUI_RUNTIME_BASE_URL="http://localhost:8188",
        COMFYUI_RUNTIME_ALLOWED_HOSTS="localhost",
        COMFYUI_RUNTIME_READ_ONLY_PROBE_ENABLED=True,
        COMFYUI_RUNTIME_PROMPT_SUBMISSION_ENABLED=True,
        COMFYUI_RUNTIME_ALLOWED_EXECUTION_PATHS="/prompt,/history,/queue",
        COMFYUI_RUNTIME_TIMEOUT_SECONDS=9,
    )
    post_calls: list[tuple[str, dict[str, object], float]] = []
    get_calls: list[tuple[str, float]] = []

    def fake_http_post(url: str, payload: dict[str, object], timeout: float) -> dict[str, object]:
        post_calls.append((url, payload, timeout))
        return {
            "status_code": 200,
            "json": {"prompt_id": "prompt-123", "number": 4, "node_errors": {}},
            "text": '{"prompt_id":"prompt-123"}',
        }

    def fake_http_get(url: str, timeout: float) -> dict[str, object]:
        get_calls.append((url, timeout))
        if url.endswith("/queue"):
            return {"status_code": 200, "json": {"queue_running": [], "queue_pending": []}, "text": "{}"}
        return {
            "status_code": 200,
            "json": {"prompt-123": {"outputs": {"9": {"images": [{"filename": "demo.png"}]}}}},
            "text": "{}",
        }

    service = ComfyUIRuntimeService(settings=settings, http_get=fake_http_get, http_post=fake_http_post)
    capabilities = service.capabilities(workspace_id="workspace-comfyui")
    submitted = service.submit_prompt_job(
        workspace_id="workspace-comfyui",
        prompt={"1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "demo.safetensors"}}},
        client_id="aiops-test-client",
        workflow={"nodes": []},
        metadata={"source": "test"},
    )
    history = service.prompt_history(workspace_id="workspace-comfyui", prompt_id="prompt-123")
    queue = service.queue_status(workspace_id="workspace-comfyui")

    assert "submit_comfyui_prompt_job" in capabilities.available_actions
    assert "submit_prompt" not in capabilities.disabled_actions
    assert capabilities.mock is False
    assert capabilities.raw["prompt_submission_ready"] is True
    assert submitted.success is True
    assert submitted.external_request_attempted is True
    assert submitted.runtime_calls_enabled is True
    assert submitted.prompt_submission_enabled is True
    assert submitted.prompt_id == "prompt-123"
    assert submitted.status_code == 200
    assert submitted.request_payload["client_id"] == "aiops-test-client"
    assert post_calls == [("http://localhost:8188/prompt", submitted.request_payload, 9.0)]
    assert history.success is True
    assert history.outputs["9"]["images"][0]["filename"] == "demo.png"
    assert queue.success is True
    assert queue.queue_running == []
    assert queue.queue_pending == []
    assert get_calls == [("http://localhost:8188/history/prompt-123", 9.0), ("http://localhost:8188/queue", 9.0)]


def test_comfyui_runtime_prompt_submission_rejects_unlisted_execution_path() -> None:
    """Execution path allowlists should block history and queue reads outside the configured paths."""

    settings = Settings(
        COMFYUI_RUNTIME_PROVIDER="guarded",
        COMFYUI_RUNTIME_ENABLED=True,
        COMFYUI_RUNTIME_ALLOW_NETWORK=True,
        COMFYUI_RUNTIME_BASE_URL="http://localhost:8188",
        COMFYUI_RUNTIME_ALLOWED_HOSTS="localhost",
        COMFYUI_RUNTIME_READ_ONLY_PROBE_ENABLED=True,
        COMFYUI_RUNTIME_PROMPT_SUBMISSION_ENABLED=True,
        COMFYUI_RUNTIME_ALLOWED_EXECUTION_PATHS="/prompt",
    )
    calls: list[tuple[str, float]] = []
    history = ComfyUIRuntimeService(
        settings=settings,
        http_get=lambda url, timeout: calls.append((url, timeout)) or {"status_code": 200},
    ).prompt_history(workspace_id="workspace-comfyui", prompt_id="prompt-123")

    assert history.success is False
    assert history.external_request_attempted is False
    assert history.runtime_calls_enabled is False
    assert "COMFYUI_RUNTIME_ALLOWED_EXECUTION_PATHS" in str(history.error)
    assert calls == []


def test_comfyui_runtime_video_resource_plan_is_blocked_by_default_without_network() -> None:
    """Video GPU admission should stay disabled until guarded runtime gates are explicit."""

    calls: list[tuple[str, float]] = []
    plan = ComfyUIRuntimeService(
        settings=Settings(),
        http_get=lambda url, timeout: calls.append((url, timeout)) or {"status_code": 200},
    ).video_resource_plan(workspace_id="workspace-comfyui", width=1280, height=720, frames=96)

    assert plan.success is False
    assert plan.admission_status == "blocked"
    assert plan.should_submit_now is False
    assert plan.system_stats_attempted is False
    assert plan.queue_status_attempted is False
    assert plan.external_request_attempted is False
    assert calls == []
    assert any("COMFYUI_RUNTIME_PROVIDER=guarded" in reason for reason in plan.blocking_reasons)


def test_comfyui_runtime_video_resource_plan_admits_and_video_submit_records_plan() -> None:
    """Video prompt submission should check /system_stats and /queue before calling /prompt."""

    settings = Settings(
        COMFYUI_RUNTIME_PROVIDER="guarded",
        COMFYUI_RUNTIME_ENABLED=True,
        COMFYUI_RUNTIME_ALLOW_NETWORK=True,
        COMFYUI_RUNTIME_BASE_URL="http://localhost:8188",
        COMFYUI_RUNTIME_ALLOWED_HOSTS="localhost",
        COMFYUI_RUNTIME_READ_ONLY_PROBE_ENABLED=True,
        COMFYUI_RUNTIME_PROMPT_SUBMISSION_ENABLED=True,
        COMFYUI_RUNTIME_ALLOWED_EXECUTION_PATHS="/prompt,/history,/queue",
        COMFYUI_RUNTIME_TIMEOUT_SECONDS=13,
    )
    get_calls: list[tuple[str, float]] = []
    post_calls: list[tuple[str, dict[str, object], float]] = []

    def fake_http_get(url: str, timeout: float) -> dict[str, object]:
        get_calls.append((url, timeout))
        if url.endswith("/system_stats"):
            return {
                "status_code": 200,
                "json": {
                    "devices": [
                        {
                            "name": "RTX Test",
                            "type": "cuda",
                            "vram_total": 24 * 1024 * 1024 * 1024,
                            "vram_free": 18 * 1024 * 1024 * 1024,
                        }
                    ]
                },
                "text": "{}",
            }
        if url.endswith("/queue"):
            return {"status_code": 200, "json": {"queue_running": [], "queue_pending": []}, "text": "{}"}
        return {"status_code": 404, "json": {}, "text": "{}"}

    def fake_http_post(url: str, payload: dict[str, object], timeout: float) -> dict[str, object]:
        post_calls.append((url, payload, timeout))
        return {"status_code": 200, "json": {"prompt_id": "video-prompt-1", "number": 2, "node_errors": {}}, "text": "{}"}

    service = ComfyUIRuntimeService(settings=settings, http_get=fake_http_get, http_post=fake_http_post)
    plan = service.video_resource_plan(
        workspace_id="workspace-comfyui",
        resource_profile="standard",
        width=1280,
        height=720,
        frames=96,
        estimated_vram_mb=4096,
        reserve_vram_mb=1024,
    )
    submitted = service.submit_prompt_job(
        workspace_id="workspace-comfyui",
        prompt={"1": {"class_type": "EmptyImage", "inputs": {"width": 1280, "height": 720}}},
        media_type="video",
        resource_profile="standard",
        frames=96,
        estimated_vram_mb=4096,
        reserve_vram_mb=1024,
        metadata={"source": "video-test"},
    )

    assert plan.success is True
    assert plan.admission_status == "admitted"
    assert plan.should_submit_now is True
    assert plan.selected_gpu["name"] == "RTX Test"
    assert plan.required_free_vram_mb == 5120
    assert submitted.success is True
    assert submitted.prompt_id == "video-prompt-1"
    assert submitted.metadata["video_resource_plan"]["admission_status"] == "admitted"
    assert submitted.request_payload["extra_data"]["aiops_video_resource_plan"]["selected_gpu"]["name"] == "RTX Test"
    assert post_calls == [("http://localhost:8188/prompt", submitted.request_payload, 13.0)]
    assert get_calls == [
        ("http://localhost:8188/system_stats", 13.0),
        ("http://localhost:8188/queue", 13.0),
        ("http://localhost:8188/system_stats", 13.0),
        ("http://localhost:8188/queue", 13.0),
    ]


def test_comfyui_runtime_video_endpoint_pool_selects_available_gpu_instance() -> None:
    """Video submissions should route to the ComfyUI endpoint whose GPU and queue can admit the job."""

    settings = Settings(
        COMFYUI_RUNTIME_PROVIDER="guarded",
        COMFYUI_RUNTIME_ENABLED=True,
        COMFYUI_RUNTIME_ALLOW_NETWORK=True,
        COMFYUI_RUNTIME_BASE_URL="http://localhost:8188",
        COMFYUI_RUNTIME_ALLOWED_HOSTS="localhost",
        COMFYUI_RUNTIME_READ_ONLY_PROBE_ENABLED=True,
        COMFYUI_RUNTIME_PROMPT_SUBMISSION_ENABLED=True,
        COMFYUI_RUNTIME_ALLOWED_EXECUTION_PATHS="/prompt,/history,/queue",
        COMFYUI_VIDEO_GPU_ENDPOINTS="gpu0|http://localhost:8188|0;gpu1|http://localhost:8189|0",
    )
    get_calls: list[tuple[str, float]] = []
    post_calls: list[tuple[str, dict[str, object], float]] = []

    def fake_http_get(url: str, timeout: float) -> dict[str, object]:
        get_calls.append((url, timeout))
        if url.startswith("http://localhost:8188") and url.endswith("/system_stats"):
            return {
                "status_code": 200,
                "json": {"devices": [{"index": 0, "name": "GPU 0", "vram_total": 24_000, "vram_free": 20_000}]},
                "text": "{}",
            }
        if url.startswith("http://localhost:8188") and url.endswith("/queue"):
            return {"status_code": 200, "json": {"queue_running": [{"prompt_id": "busy"}], "queue_pending": []}, "text": "{}"}
        if url.startswith("http://localhost:8189") and url.endswith("/system_stats"):
            return {
                "status_code": 200,
                "json": {"devices": [{"index": 0, "name": "GPU 1", "vram_total": 24_000, "vram_free": 18_000}]},
                "text": "{}",
            }
        if url.startswith("http://localhost:8189") and url.endswith("/queue"):
            return {"status_code": 200, "json": {"queue_running": [], "queue_pending": []}, "text": "{}"}
        return {"status_code": 404, "json": {}, "text": "{}"}

    def fake_http_post(url: str, payload: dict[str, object], timeout: float) -> dict[str, object]:
        post_calls.append((url, payload, timeout))
        return {"status_code": 200, "json": {"prompt_id": "video-prompt-gpu1", "number": 7, "node_errors": {}}, "text": "{}"}

    service = ComfyUIRuntimeService(settings=settings, http_get=fake_http_get, http_post=fake_http_post)
    plan = service.video_resource_plan(
        workspace_id="workspace-comfyui",
        estimated_vram_mb=4096,
        reserve_vram_mb=1024,
    )
    submitted = service.submit_prompt_job(
        workspace_id="workspace-comfyui",
        prompt={"1": {"class_type": "EmptyImage", "inputs": {"width": 1280, "height": 720}}},
        media_type="video",
        estimated_vram_mb=4096,
        reserve_vram_mb=1024,
    )

    assert plan.admission_status == "admitted"
    assert plan.selected_endpoint["name"] == "gpu1"
    assert plan.selected_endpoint["base_url"] == "http://localhost:8189"
    assert plan.selected_gpu["endpoint_name"] == "gpu1"
    assert len(plan.endpoint_plans) == 2
    assert plan.endpoint_plans[0]["admission_status"] == "queued"
    assert submitted.success is True
    assert submitted.base_url == "http://localhost:8189"
    assert submitted.prompt_id == "video-prompt-gpu1"
    assert submitted.request_payload["extra_data"]["aiops_video_resource_plan"]["selected_endpoint"]["name"] == "gpu1"
    assert post_calls == [("http://localhost:8189/prompt", submitted.request_payload, 30.0)]


def test_comfyui_runtime_video_submit_blocks_when_vram_is_insufficient() -> None:
    """Video prompt submission must not call /prompt when no GPU has enough free VRAM."""

    settings = Settings(
        COMFYUI_RUNTIME_PROVIDER="guarded",
        COMFYUI_RUNTIME_ENABLED=True,
        COMFYUI_RUNTIME_ALLOW_NETWORK=True,
        COMFYUI_RUNTIME_BASE_URL="http://localhost:8188",
        COMFYUI_RUNTIME_ALLOWED_HOSTS="localhost",
        COMFYUI_RUNTIME_READ_ONLY_PROBE_ENABLED=True,
        COMFYUI_RUNTIME_PROMPT_SUBMISSION_ENABLED=True,
        COMFYUI_RUNTIME_ALLOWED_EXECUTION_PATHS="/prompt,/history,/queue",
    )
    get_calls: list[tuple[str, float]] = []
    post_calls: list[tuple[str, dict[str, object], float]] = []

    def fake_http_get(url: str, timeout: float) -> dict[str, object]:
        get_calls.append((url, timeout))
        if url.endswith("/system_stats"):
            return {
                "status_code": 200,
                "json": {
                    "devices": [
                        {
                            "name": "Small GPU",
                            "type": "cuda",
                            "vram_total": 8 * 1024 * 1024 * 1024,
                            "vram_free": 2 * 1024 * 1024 * 1024,
                        }
                    ]
                },
                "text": "{}",
            }
        return {"status_code": 200, "json": {"queue_running": [], "queue_pending": []}, "text": "{}"}

    service = ComfyUIRuntimeService(
        settings=settings,
        http_get=fake_http_get,
        http_post=lambda url, payload, timeout: post_calls.append((url, payload, timeout)) or {},
    )
    submitted = service.submit_prompt_job(
        workspace_id="workspace-comfyui",
        prompt={"1": {"class_type": "EmptyImage", "inputs": {"width": 1920, "height": 1080}}},
        media_type="video",
        estimated_vram_mb=8192,
        reserve_vram_mb=2048,
    )

    assert submitted.success is False
    assert submitted.external_request_attempted is True
    assert submitted.runtime_calls_enabled is False
    assert submitted.metadata["prompt_submission_skipped"] is True
    assert submitted.metadata["video_resource_plan"]["admission_status"] == "blocked"
    assert "Insufficient free VRAM" in submitted.error
    assert post_calls == []
    assert get_calls == [("http://localhost:8188/system_stats", 30.0), ("http://localhost:8188/queue", 30.0)]


@pytest.mark.asyncio
async def test_comfyui_runtime_video_job_persists_resource_blocked_by_default(session: AsyncSession) -> None:
    """Persisted video jobs should record guarded resource blockers without calling ComfyUI by default."""

    get_calls: list[tuple[str, float]] = []
    post_calls: list[tuple[str, dict[str, object], float]] = []
    service = ComfyUIRuntimeService(
        settings=Settings(),
        http_get=lambda url, timeout: get_calls.append((url, timeout)) or {"status_code": 200},
        http_post=lambda url, payload, timeout: post_calls.append((url, dict(payload), timeout)) or {},
    )

    job = await service.create_video_job(
        session,
        workspace_id="workspace-comfyui-video-jobs",
        user_id="user-comfyui",
        prompt={"1": {"class_type": "EmptyImage", "inputs": {"width": 1280, "height": 720}}},
        resource_profile="standard",
        width=1280,
        height=720,
        frames=96,
        operator_note="default gates should block this job",
        metadata={"source_page": "comfyui-operations"},
    )
    listed = await service.list_video_jobs(session, workspace_id="workspace-comfyui-video-jobs", limit=10)

    assert job.workspace_id == "workspace-comfyui-video-jobs"
    assert job.user_id == "user-comfyui"
    assert job.job_status == "resource_blocked"
    assert job.runtime_prompt_id is None
    assert job.external_request_attempted is False
    assert job.runtime_calls_enabled is False
    assert job.prompt_submission_enabled is False
    assert job.resource_plan["admission_status"] == "blocked"
    assert job.metadata["phase"] == "66B"
    assert job.operator_note == "default gates should block this job"
    assert "COMFYUI_RUNTIME_PROVIDER=guarded" in str(job.failure_reason)
    refreshed = await service.refresh_video_job(
        session,
        workspace_id="workspace-comfyui-video-jobs",
        job_id=job.id,
        resubmit_if_waiting=False,
    )
    assert refreshed.job_status == "resource_blocked"
    assert "COMFYUI_RUNTIME_PROVIDER=guarded" in str(refreshed.failure_reason)
    assert len(listed.items) == 1
    assert listed.items[0].id == job.id
    assert get_calls == []
    assert post_calls == []


@pytest.mark.asyncio
async def test_comfyui_runtime_video_job_submits_polls_and_refreshes_outputs(session: AsyncSession) -> None:
    """Persisted video jobs should submit, poll history, and retain output files when every gate allows it."""

    settings = Settings(
        COMFYUI_RUNTIME_PROVIDER="guarded",
        COMFYUI_RUNTIME_ENABLED=True,
        COMFYUI_RUNTIME_ALLOW_NETWORK=True,
        COMFYUI_RUNTIME_BASE_URL="http://localhost:8188",
        COMFYUI_RUNTIME_ALLOWED_HOSTS="localhost",
        COMFYUI_RUNTIME_READ_ONLY_PROBE_ENABLED=True,
        COMFYUI_RUNTIME_PROMPT_SUBMISSION_ENABLED=True,
        COMFYUI_RUNTIME_ALLOWED_EXECUTION_PATHS="/prompt,/history,/queue",
        COMFYUI_RUNTIME_TIMEOUT_SECONDS=6,
    )
    get_calls: list[tuple[str, float]] = []
    post_calls: list[tuple[str, dict[str, object], float]] = []

    def fake_http_get(url: str, timeout: float) -> dict[str, object]:
        get_calls.append((url, timeout))
        if url.endswith("/system_stats"):
            return {
                "status_code": 200,
                "json": {"devices": [{"name": "Video GPU", "vram_total": 24_000, "vram_free": 20_000}]},
                "text": "{}",
            }
        if url.endswith("/queue"):
            return {"status_code": 200, "json": {"queue_running": [], "queue_pending": []}, "text": "{}"}
        if url.endswith("/history/video-job-prompt-1"):
            return {
                "status_code": 200,
                "json": {
                    "video-job-prompt-1": {
                        "outputs": {
                            "9": {
                                "gifs": [{"filename": "clip.gif", "subfolder": "video", "type": "output"}],
                                "videos": [{"filename": "clip.mp4", "subfolder": "video", "type": "output"}],
                            }
                        }
                    }
                },
                "text": "{}",
            }
        return {"status_code": 404, "json": {}, "text": "{}"}

    def fake_http_post(url: str, payload: dict[str, object], timeout: float) -> dict[str, object]:
        post_calls.append((url, payload, timeout))
        return {"status_code": 200, "json": {"prompt_id": "video-job-prompt-1", "number": 8, "node_errors": {}}, "text": "{}"}

    service = ComfyUIRuntimeService(settings=settings, http_get=fake_http_get, http_post=fake_http_post)
    job = await service.create_video_job(
        session,
        workspace_id="workspace-comfyui-video-output",
        user_id="user-comfyui",
        prompt={"1": {"class_type": "EmptyImage", "inputs": {"width": 1280, "height": 720}}},
        workflow={"name": "server_configured_video_workflow"},
        resource_profile="standard",
        width=1280,
        height=720,
        frames=96,
        estimated_vram_mb=4096,
        reserve_vram_mb=1024,
        metadata={"source_page": "comfyui-operations"},
    )
    refreshed = await service.refresh_video_job(
        session,
        workspace_id="workspace-comfyui-video-output",
        job_id=job.id,
        metadata={"source_page": "comfyui-operations"},
    )

    assert job.job_status == "output_ready"
    assert job.runtime_prompt_id == "video-job-prompt-1"
    assert job.runtime_base_url == "http://localhost:8188"
    assert job.resource_plan["admission_status"] == "admitted"
    assert job.selected_gpu["name"] == "Video GPU"
    assert {output["filename"] for output in job.outputs} == {"clip.gif", "clip.mp4"}
    assert "produced 2 output file" in str(job.result_summary)
    assert refreshed.job_status == "output_ready"
    assert refreshed.runtime_prompt_id == "video-job-prompt-1"
    assert len(refreshed.outputs) == 2
    assert post_calls == [("http://localhost:8188/prompt", job.submit_payload, 6.0)]
    assert get_calls == [
        ("http://localhost:8188/system_stats", 6.0),
        ("http://localhost:8188/queue", 6.0),
        ("http://localhost:8188/history/video-job-prompt-1", 6.0),
        ("http://localhost:8188/queue", 6.0),
        ("http://localhost:8188/history/video-job-prompt-1", 6.0),
        ("http://localhost:8188/queue", 6.0),
    ]


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
    readiness_check = await service.create_post_manual_readiness_check(
        session,
        workspace_id="workspace-comfyui-config-requests",
        evidence_id=verified_evidence.id,
        user_id="user-comfyui",
        operator_note="compare readiness after manual apply",
        metadata={"source_page": "comfyui-operations"},
    )
    listed_readiness_checks = await service.list_post_manual_readiness_checks(
        session,
        workspace_id="workspace-comfyui-config-requests",
        limit=10,
    )
    ready_readiness_check = await service.update_post_manual_readiness_check_status(
        session,
        workspace_id="workspace-comfyui-config-requests",
        check_id=readiness_check.id,
        status="ready_for_review",
        reviewer_notes="ready to compare",
    )
    rejected_readiness_check = await service.update_post_manual_readiness_check_status(
        session,
        workspace_id="workspace-comfyui-config-requests",
        check_id=readiness_check.id,
        status="rejected",
        reviewer_notes="blocked gates still need maintainer action",
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
    assert readiness_check.workspace_id == "workspace-comfyui-config-requests"
    assert readiness_check.user_id == "user-comfyui"
    assert readiness_check.manual_apply_evidence_id == verified_evidence.id
    assert readiness_check.config_change_request_id == approved.id
    assert readiness_check.check_status == "draft"
    assert readiness_check.comparison_status == "blocked"
    assert readiness_check.readiness_status_current == "blocked"
    assert readiness_check.external_request_attempted is False
    assert readiness_check.runtime_calls_enabled is False
    assert readiness_check.health_probe_executed is False
    assert readiness_check.api_config_mutation_performed is False
    assert readiness_check.manual_evidence_status == "verified"
    assert readiness_check.manual_config_applied is True
    assert readiness_check.service_restart_reported is True
    assert readiness_check.metadata["phase"] == "62H"
    assert readiness_check.metadata["no_network_call_performed"] is True
    assert readiness_check.metadata["source_page"] == "comfyui-operations"
    assert readiness_check.comparison_results["health_probe_executed"] is False
    assert readiness_check.current_diagnostics_payload["raw"]["no_network_call_performed"] is True
    assert any("read_only_probe_ready_current" in item for item in readiness_check.blocking_reasons)
    assert len(listed_readiness_checks.items) == 1
    assert listed_readiness_checks.items[0].id == readiness_check.id
    assert ready_readiness_check.check_status == "ready_for_review"
    assert rejected_readiness_check.check_status == "rejected"
    assert rejected_readiness_check.api_config_mutation_performed is False
    assert calls == []


@pytest.mark.asyncio
async def test_comfyui_runtime_guarded_probe_execution_is_approval_gated(session: AsyncSession) -> None:
    """Guarded probe execution should call /system_stats only after explicit execution approval."""

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

    service = ComfyUIRuntimeService(settings=settings, http_get=fake_http_get)
    change_request = await service.create_config_change_request(
        session,
        workspace_id="workspace-comfyui-guarded-exec",
        user_id="user-comfyui",
        change_reason="ready guarded config",
        metadata={"source_page": "comfyui-operations"},
    )
    await service.update_config_change_request_status(
        session,
        workspace_id="workspace-comfyui-guarded-exec",
        request_id=change_request.id,
        status="ready_for_review",
    )
    approved_request = await service.update_config_change_request_status(
        session,
        workspace_id="workspace-comfyui-guarded-exec",
        request_id=change_request.id,
        status="approved_for_manual_apply",
    )
    evidence = await service.create_manual_apply_evidence(
        session,
        workspace_id="workspace-comfyui-guarded-exec",
        request_id=approved_request.id,
        user_id="user-comfyui",
        service_restart_reported=True,
        metadata={"source_page": "comfyui-operations"},
    )
    await service.update_manual_apply_evidence_status(
        session,
        workspace_id="workspace-comfyui-guarded-exec",
        evidence_id=evidence.id,
        status="ready_for_review",
    )
    verified_evidence = await service.update_manual_apply_evidence_status(
        session,
        workspace_id="workspace-comfyui-guarded-exec",
        evidence_id=evidence.id,
        status="verified",
    )
    readiness_check = await service.create_post_manual_readiness_check(
        session,
        workspace_id="workspace-comfyui-guarded-exec",
        evidence_id=verified_evidence.id,
        user_id="user-comfyui",
        metadata={"source_page": "comfyui-operations"},
    )
    await service.update_post_manual_readiness_check_status(
        session,
        workspace_id="workspace-comfyui-guarded-exec",
        check_id=readiness_check.id,
        status="ready_for_review",
    )
    approved_readiness_check = await service.update_post_manual_readiness_check_status(
        session,
        workspace_id="workspace-comfyui-guarded-exec",
        check_id=readiness_check.id,
        status="approved_for_read_only_probe",
    )
    execution = await service.create_guarded_probe_execution(
        session,
        workspace_id="workspace-comfyui-guarded-exec",
        check_id=approved_readiness_check.id,
        user_id="user-comfyui",
        operator_note="prepare guarded read-only probe",
        metadata={"source_page": "comfyui-operations"},
    )
    listed = await service.list_guarded_probe_executions(
        session,
        workspace_id="workspace-comfyui-guarded-exec",
        limit=10,
    )
    ready_execution = await service.update_guarded_probe_execution_status(
        session,
        workspace_id="workspace-comfyui-guarded-exec",
        execution_id=execution.id,
        status="ready_for_approval",
        reviewer_notes="ready for execution approval",
    )
    approved_execution = await service.update_guarded_probe_execution_status(
        session,
        workspace_id="workspace-comfyui-guarded-exec",
        execution_id=execution.id,
        status="approved_for_execution",
        reviewer_notes="approve one read-only system_stats probe",
    )

    assert calls == []
    assert approved_readiness_check.check_status == "approved_for_read_only_probe"
    assert approved_readiness_check.guarded_probe_ready is True
    assert execution.execution_status == "draft"
    assert execution.probe_result_status == "not_started"
    assert execution.post_manual_readiness_check_id == approved_readiness_check.id
    assert execution.manual_apply_evidence_id == verified_evidence.id
    assert execution.config_change_request_id == approved_request.id
    assert execution.read_only_probe_ready_current is True
    assert execution.guarded_probe_ready is True
    assert execution.external_request_attempted is False
    assert execution.health_probe_executed is False
    assert execution.read_only_probe_attempted is False
    assert execution.runtime_calls_enabled is False
    assert execution.api_config_mutation_performed is False
    assert execution.probe_request["url"] == "http://localhost:8188/system_stats"
    assert execution.metadata["phase"] == "62J"
    assert execution.metadata["no_network_call_performed"] is True
    assert len(listed.items) == 1
    assert listed.items[0].id == execution.id
    assert ready_execution.execution_status == "ready_for_approval"
    assert ready_execution.external_request_attempted is False
    assert approved_execution.execution_status == "approved_for_execution"
    assert calls == []

    executed = await service.execute_guarded_probe_execution(
        session,
        workspace_id="workspace-comfyui-guarded-exec",
        execution_id=approved_execution.id,
        reviewer_notes="executed one approved read-only probe",
        metadata={"source_page": "comfyui-operations"},
    )

    assert calls == [("http://localhost:8188/system_stats", 5.0)]
    assert executed.execution_status == "succeeded"
    assert executed.probe_result_status == "reachable"
    assert executed.external_request_attempted is True
    assert executed.health_probe_executed is True
    assert executed.read_only_probe_attempted is True
    assert executed.runtime_calls_enabled is False
    assert executed.api_config_mutation_performed is False
    assert executed.probe_status_code == 200
    assert executed.probe_latency_ms is not None
    assert executed.probe_response["reachable"] is True
    assert executed.probe_response["raw"]["probe_path"] == "/system_stats"
    assert executed.metadata["phase"] == "62J"
    assert executed.metadata["no_network_call_performed"] is False
    assert executed.metadata["external_request_attempted"] is True


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
    app.dependency_overrides[get_settings] = lambda: settings
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
        created_readiness_check = await client.post(
            f"/api/v1/comfyui-runtime/manual-apply-evidence/{created_apply_evidence.json()['id']}/post-manual-readiness-checks",
            headers=headers,
            json={"operator_note": "compare post manual readiness", "metadata": {"source_page": "comfyui-operations"}},
        )
        readiness_check_list = await client.get("/api/v1/comfyui-runtime/post-manual-readiness-checks?limit=5", headers=headers)
        ready_readiness_check = await client.post(
            f"/api/v1/comfyui-runtime/post-manual-readiness-checks/{created_readiness_check.json()['id']}/ready",
            headers=headers,
            json={"reviewer_notes": "ready to compare"},
        )
        rejected_readiness_check = await client.post(
            f"/api/v1/comfyui-runtime/post-manual-readiness-checks/{created_readiness_check.json()['id']}/reject",
            headers=headers,
            json={"reviewer_notes": "blocked gates remain"},
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
    assert created_readiness_check.status_code == 200
    assert created_readiness_check.json()["workspace_id"] == "workspace-comfyui-api"
    assert created_readiness_check.json()["user_id"] == "user-comfyui"
    assert created_readiness_check.json()["manual_apply_evidence_id"] == created_apply_evidence.json()["id"]
    assert created_readiness_check.json()["check_status"] == "draft"
    assert created_readiness_check.json()["comparison_status"] == "blocked"
    assert created_readiness_check.json()["health_probe_executed"] is False
    assert created_readiness_check.json()["api_config_mutation_performed"] is False
    assert created_readiness_check.json()["external_request_attempted"] is False
    assert created_readiness_check.json()["runtime_calls_enabled"] is False
    assert created_readiness_check.json()["metadata"]["phase"] == "62H"
    assert created_readiness_check.json()["comparison_results"]["health_probe_executed"] is False
    assert readiness_check_list.status_code == 200
    assert len(readiness_check_list.json()["items"]) == 1
    assert ready_readiness_check.status_code == 200
    assert ready_readiness_check.json()["check_status"] == "ready_for_review"
    assert rejected_readiness_check.status_code == 200
    assert rejected_readiness_check.json()["check_status"] == "rejected"
    assert rejected_readiness_check.json()["api_config_mutation_performed"] is False
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


@pytest.mark.asyncio
async def test_comfyui_runtime_video_resource_plan_api(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """API should expose guarded video GPU and queue admission planning."""

    settings = Settings(
        COMFYUI_RUNTIME_PROVIDER="guarded",
        COMFYUI_RUNTIME_ENABLED=True,
        COMFYUI_RUNTIME_ALLOW_NETWORK=True,
        COMFYUI_RUNTIME_BASE_URL="http://localhost:8188",
        COMFYUI_RUNTIME_ALLOWED_HOSTS="localhost",
        COMFYUI_RUNTIME_READ_ONLY_PROBE_ENABLED=True,
        COMFYUI_RUNTIME_PROMPT_SUBMISSION_ENABLED=True,
        COMFYUI_RUNTIME_ALLOWED_EXECUTION_PATHS="/prompt,/history,/queue",
        COMFYUI_RUNTIME_TIMEOUT_SECONDS=17,
    )
    get_calls: list[tuple[str, float]] = []

    def fake_http_get(url: str, timeout: float) -> dict[str, object]:
        get_calls.append((url, timeout))
        if url.endswith("/system_stats"):
            return {
                "status_code": 200,
                "json": {"devices": [{"name": "API GPU", "vram_total": 20 * 1024 * 1024 * 1024, "vram_free": 12 * 1024 * 1024 * 1024}]},
                "text": "{}",
            }
        return {"status_code": 200, "json": {"queue_running": [], "queue_pending": []}, "text": "{}"}

    monkeypatch.setattr(comfyui_runtime_routes, "get_settings", lambda: settings)
    monkeypatch.setattr(ComfyUIRuntimeService, "_default_http_get", staticmethod(fake_http_get))

    app = FastAPI()
    app.add_exception_handler(AppError, app_error_handler)
    app.include_router(comfyui_runtime_routes.router, prefix="/api/v1")
    app.dependency_overrides[get_settings] = lambda: settings

    headers = {"X-Workspace-Id": "workspace-comfyui-video-api", "X-User-Id": "user-comfyui"}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        plan = await client.post(
            "/api/v1/comfyui-runtime/video-resource-plans",
            headers=headers,
            json={"width": 1280, "height": 720, "frames": 96, "estimated_vram_mb": 4096, "reserve_vram_mb": 1024},
        )

    assert plan.status_code == 200
    assert plan.json()["workspace_id"] == "workspace-comfyui-video-api"
    assert plan.json()["admission_status"] == "admitted"
    assert plan.json()["should_submit_now"] is True
    assert plan.json()["selected_gpu"]["name"] == "API GPU"
    assert get_calls == [("http://localhost:8188/system_stats", 17.0), ("http://localhost:8188/queue", 17.0)]


@pytest.mark.asyncio
async def test_comfyui_runtime_video_job_api_persists_and_refreshes(monkeypatch, session: AsyncSession) -> None:  # type: ignore[no-untyped-def]
    """API should expose persisted ComfyUI video jobs for dashboard and client status views."""

    settings = Settings()
    monkeypatch.setattr(comfyui_runtime_routes, "get_settings", lambda: settings)

    async def override_get_session():  # type: ignore[no-untyped-def]
        yield session

    app = FastAPI()
    app.add_exception_handler(AppError, app_error_handler)
    app.include_router(comfyui_runtime_routes.router, prefix="/api/v1")
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[comfyui_runtime_routes.get_session] = override_get_session

    headers = {"X-Workspace-Id": "workspace-comfyui-video-job-api", "X-User-Id": "user-comfyui"}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        created = await client.post(
            "/api/v1/comfyui-runtime/video-jobs",
            headers=headers,
            json={
                "prompt": {"1": {"class_type": "EmptyImage", "inputs": {"width": 1280, "height": 720}}},
                "workflow": {"name": "server_configured_video_workflow"},
                "operator_note": "api default blocked",
                "metadata": {"source_page": "comfyui-operations"},
            },
        )
        listed = await client.get("/api/v1/comfyui-runtime/video-jobs?limit=5", headers=headers)
        fetched = await client.get(f"/api/v1/comfyui-runtime/video-jobs/{created.json()['id']}", headers=headers)
        refreshed = await client.post(
            f"/api/v1/comfyui-runtime/video-jobs/{created.json()['id']}/refresh",
            headers=headers,
            json={"poll_history": True, "resubmit_if_waiting": True, "metadata": {"source_page": "comfyui-operations"}},
        )

    assert created.status_code == 200
    assert created.json()["workspace_id"] == "workspace-comfyui-video-job-api"
    assert created.json()["user_id"] == "user-comfyui"
    assert created.json()["job_status"] == "resource_blocked"
    assert created.json()["runtime_prompt_id"] is None
    assert created.json()["resource_plan"]["admission_status"] == "blocked"
    assert created.json()["metadata"]["phase"] == "66B"
    assert listed.status_code == 200
    assert len(listed.json()["items"]) == 1
    assert fetched.status_code == 200
    assert fetched.json()["id"] == created.json()["id"]
    assert refreshed.status_code == 200
    assert refreshed.json()["job_status"] == "resource_blocked"


@pytest.mark.asyncio
async def test_comfyui_runtime_real_prompt_adapter_api(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """API should expose guarded real prompt submission, history, and queue reads."""

    settings = Settings(
        COMFYUI_RUNTIME_PROVIDER="guarded",
        COMFYUI_RUNTIME_ENABLED=True,
        COMFYUI_RUNTIME_ALLOW_NETWORK=True,
        COMFYUI_RUNTIME_BASE_URL="http://localhost:8188",
        COMFYUI_RUNTIME_ALLOWED_HOSTS="localhost",
        COMFYUI_RUNTIME_READ_ONLY_PROBE_ENABLED=True,
        COMFYUI_RUNTIME_PROMPT_SUBMISSION_ENABLED=True,
        COMFYUI_RUNTIME_ALLOWED_EXECUTION_PATHS="/prompt,/history,/queue",
        COMFYUI_RUNTIME_TIMEOUT_SECONDS=11,
    )
    post_calls: list[tuple[str, dict[str, object], float]] = []
    get_calls: list[tuple[str, float]] = []

    def fake_http_post(url: str, payload: dict[str, object], timeout: float) -> dict[str, object]:
        post_calls.append((url, payload, timeout))
        return {"status_code": 200, "json": {"prompt_id": "api-prompt-1", "number": 1, "node_errors": {}}, "text": "{}"}

    def fake_http_get(url: str, timeout: float) -> dict[str, object]:
        get_calls.append((url, timeout))
        if url.endswith("/queue"):
            return {"status_code": 200, "json": {"queue_running": [], "queue_pending": []}, "text": "{}"}
        return {"status_code": 200, "json": {"api-prompt-1": {"outputs": {"4": {"images": []}}}}, "text": "{}"}

    monkeypatch.setattr(comfyui_runtime_routes, "get_settings", lambda: settings)
    monkeypatch.setattr(ComfyUIRuntimeService, "_default_http_post_json", staticmethod(fake_http_post))
    monkeypatch.setattr(ComfyUIRuntimeService, "_default_http_get", staticmethod(fake_http_get))

    app = FastAPI()
    app.add_exception_handler(AppError, app_error_handler)
    app.include_router(comfyui_runtime_routes.router, prefix="/api/v1")
    app.dependency_overrides[get_settings] = lambda: settings

    headers = {"X-Workspace-Id": "workspace-comfyui-real-api", "X-User-Id": "user-comfyui"}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        submitted = await client.post(
            "/api/v1/comfyui-runtime/prompt-jobs",
            headers=headers,
            json={
                "client_id": "aiops-api-test",
                "prompt": {"1": {"class_type": "PreviewImage", "inputs": {}}},
                "workflow": {"nodes": []},
                "metadata": {"phase": "65A"},
            },
        )
        history = await client.get("/api/v1/comfyui-runtime/prompt-jobs/api-prompt-1/history", headers=headers)
        queue = await client.get("/api/v1/comfyui-runtime/queue", headers=headers)

    assert submitted.status_code == 200
    assert submitted.json()["success"] is True
    assert submitted.json()["workspace_id"] == "workspace-comfyui-real-api"
    assert submitted.json()["prompt_id"] == "api-prompt-1"
    assert submitted.json()["runtime_calls_enabled"] is True
    assert history.status_code == 200
    assert history.json()["success"] is True
    assert history.json()["outputs"]["4"]["images"] == []
    assert queue.status_code == 200
    assert queue.json()["success"] is True
    assert post_calls == [("http://localhost:8188/prompt", submitted.json()["request_payload"], 11.0)]
    assert get_calls == [("http://localhost:8188/history/api-prompt-1", 11.0), ("http://localhost:8188/queue", 11.0)]


@pytest.mark.asyncio
async def test_comfyui_runtime_guarded_probe_execution_api(monkeypatch, session: AsyncSession) -> None:  # type: ignore[no-untyped-def]
    """API should expose the approval-gated guarded probe execution chain."""

    settings = Settings(
        COMFYUI_RUNTIME_PROVIDER="guarded",
        COMFYUI_RUNTIME_ENABLED=True,
        COMFYUI_RUNTIME_ALLOW_NETWORK=True,
        COMFYUI_RUNTIME_BASE_URL="http://localhost:8188",
        COMFYUI_RUNTIME_ALLOWED_HOSTS="localhost",
        COMFYUI_RUNTIME_READ_ONLY_PROBE_ENABLED=True,
        COMFYUI_RUNTIME_TIMEOUT_SECONDS=7,
    )
    calls: list[tuple[str, float]] = []

    def fake_http_get(url: str, timeout: float) -> dict[str, object]:
        calls.append((url, timeout))
        return {"status_code": 200, "json": {"system": {"os": "api-test"}}, "text": '{"system":{}}'}

    monkeypatch.setattr(comfyui_runtime_routes, "get_settings", lambda: settings)
    monkeypatch.setattr(ComfyUIRuntimeService, "_default_http_get", staticmethod(fake_http_get))

    async def override_get_session():  # type: ignore[no-untyped-def]
        yield session

    app = FastAPI()
    app.add_exception_handler(AppError, app_error_handler)
    app.include_router(comfyui_runtime_routes.router, prefix="/api/v1")
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[comfyui_runtime_routes.get_session] = override_get_session

    headers = {"X-Workspace-Id": "workspace-comfyui-guarded-api", "X-User-Id": "user-comfyui"}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        created_config_request = await client.post(
            "/api/v1/comfyui-runtime/config-change-requests",
            headers=headers,
            json={"change_reason": "api guarded probe", "metadata": {"source_page": "comfyui-operations"}},
        )
        await client.post(
            f"/api/v1/comfyui-runtime/config-change-requests/{created_config_request.json()['id']}/ready",
            headers=headers,
            json={"reviewer_notes": "ready"},
        )
        approved_config_request = await client.post(
            f"/api/v1/comfyui-runtime/config-change-requests/{created_config_request.json()['id']}/approve",
            headers=headers,
            json={"reviewer_notes": "approved"},
        )
        created_apply_evidence = await client.post(
            f"/api/v1/comfyui-runtime/config-change-requests/{approved_config_request.json()['id']}/manual-apply-evidence",
            headers=headers,
            json={
                "service_restart_reported": True,
                "restart_evidence": {"restart_mode": "manual_api_restart"},
                "metadata": {"source_page": "comfyui-operations"},
            },
        )
        await client.post(
            f"/api/v1/comfyui-runtime/manual-apply-evidence/{created_apply_evidence.json()['id']}/ready",
            headers=headers,
            json={"reviewer_notes": "ready"},
        )
        verified_apply_evidence = await client.post(
            f"/api/v1/comfyui-runtime/manual-apply-evidence/{created_apply_evidence.json()['id']}/verify",
            headers=headers,
            json={"reviewer_notes": "verified"},
        )
        created_readiness_check = await client.post(
            f"/api/v1/comfyui-runtime/manual-apply-evidence/{verified_apply_evidence.json()['id']}/post-manual-readiness-checks",
            headers=headers,
            json={"operator_note": "ready comparison", "metadata": {"source_page": "comfyui-operations"}},
        )
        await client.post(
            f"/api/v1/comfyui-runtime/post-manual-readiness-checks/{created_readiness_check.json()['id']}/ready",
            headers=headers,
            json={"reviewer_notes": "ready"},
        )
        approved_readiness_check = await client.post(
            f"/api/v1/comfyui-runtime/post-manual-readiness-checks/{created_readiness_check.json()['id']}/approve",
            headers=headers,
            json={"reviewer_notes": "approved for read-only probe"},
        )
        created_execution = await client.post(
            f"/api/v1/comfyui-runtime/post-manual-readiness-checks/{approved_readiness_check.json()['id']}/guarded-probe-executions",
            headers=headers,
            json={"operator_note": "create guarded probe execution", "metadata": {"source_page": "comfyui-operations"}},
        )
        execution_list = await client.get("/api/v1/comfyui-runtime/guarded-probe-executions?limit=5", headers=headers)
        ready_execution = await client.post(
            f"/api/v1/comfyui-runtime/guarded-probe-executions/{created_execution.json()['id']}/ready",
            headers=headers,
            json={"reviewer_notes": "ready"},
        )
        approved_execution = await client.post(
            f"/api/v1/comfyui-runtime/guarded-probe-executions/{created_execution.json()['id']}/approve",
            headers=headers,
            json={"reviewer_notes": "approve one read-only probe"},
        )
        executed = await client.post(
            f"/api/v1/comfyui-runtime/guarded-probe-executions/{created_execution.json()['id']}/execute",
            headers=headers,
            json={"reviewer_notes": "execute read-only probe"},
        )

    assert calls == [("http://localhost:8188/system_stats", 7.0)]
    assert created_readiness_check.status_code == 200
    assert created_readiness_check.json()["comparison_status"] == "ready_for_guarded_read_only_probe"
    assert approved_readiness_check.status_code == 200
    assert approved_readiness_check.json()["check_status"] == "approved_for_read_only_probe"
    assert created_execution.status_code == 200
    assert created_execution.json()["workspace_id"] == "workspace-comfyui-guarded-api"
    assert created_execution.json()["user_id"] == "user-comfyui"
    assert created_execution.json()["execution_status"] == "draft"
    assert created_execution.json()["external_request_attempted"] is False
    assert created_execution.json()["health_probe_executed"] is False
    assert created_execution.json()["api_config_mutation_performed"] is False
    assert created_execution.json()["metadata"]["phase"] == "62J"
    assert execution_list.status_code == 200
    assert len(execution_list.json()["items"]) == 1
    assert ready_execution.status_code == 200
    assert ready_execution.json()["execution_status"] == "ready_for_approval"
    assert approved_execution.status_code == 200
    assert approved_execution.json()["execution_status"] == "approved_for_execution"
    assert executed.status_code == 200
    assert executed.json()["execution_status"] == "succeeded"
    assert executed.json()["probe_result_status"] == "reachable"
    assert executed.json()["external_request_attempted"] is True
    assert executed.json()["health_probe_executed"] is True
    assert executed.json()["read_only_probe_attempted"] is True
    assert executed.json()["runtime_calls_enabled"] is False
    assert executed.json()["probe_status_code"] == 200
    assert executed.json()["probe_response"]["reachable"] is True
