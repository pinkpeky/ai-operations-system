"""LLM 测试 API 路由模块。

该接口只用于验证 Phase 2.5 的 LLM Client Layer，不承担任务调度或队列消费职责。
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends

from app.agents.llm_client import LLMClient
from app.comfyui_runtime.service import ComfyUIRuntimeService
from app.core.config import Settings, get_settings
from app.core.errors import AppError
from app.core.workspace_context import WorkspaceContext, get_workspace_context
from app.schemas.llm import LLMHealthResponse, LLMRequest, LLMResourcePlanRequest, LLMResourcePlanResponse, LLMResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/llm", tags=["llm"])


def _parse_gpu_indexes(value: str, *, fallback: list[int]) -> list[int]:
    indexes: list[int] = []
    for item in str(value or "").replace(";", ",").split(","):
        clean = item.strip()
        if not clean:
            continue
        try:
            index = int(clean)
        except ValueError:
            continue
        if index >= 0 and index not in indexes:
            indexes.append(index)
    return indexes or fallback


def _unique_ints(values: list[int]) -> list[int]:
    seen: set[int] = set()
    result: list[int] = []
    for value in values:
        if value >= 0 and value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _comfyui_busy_gpu_indexes(resource_plan: dict[str, Any]) -> list[int]:
    busy: list[int] = []
    for endpoint in resource_plan.get("endpoint_plans", []):
        if not isinstance(endpoint, dict):
            continue
        running = int(endpoint.get("queue_running_count") or 0)
        pending = int(endpoint.get("queue_pending_count") or 0)
        if running <= 0 and pending <= 0:
            continue
        gpu_index = endpoint.get("gpu_index")
        if isinstance(gpu_index, int):
            busy.append(gpu_index)
            continue
        selected_gpu = endpoint.get("selected_gpu")
        if isinstance(selected_gpu, dict) and isinstance(selected_gpu.get("index"), int):
            busy.append(int(selected_gpu["index"]))
    return _unique_ints(busy)


@router.get("/health", response_model=LLMHealthResponse)
async def llm_health() -> LLMHealthResponse:
    """检查当前 LLM Provider 是否可用。"""

    try:
        client = LLMClient()
        return await client.health_check()
    except Exception as exc:
        logger.exception("LLM health API failed")
        raise AppError(str(exc) or "LLM health check failed", status_code=500) from exc


@router.post("/resource-plan", response_model=LLMResourcePlanResponse)
async def llm_resource_plan(
    request: LLMResourcePlanRequest,
    context: WorkspaceContext = Depends(get_workspace_context),
    settings: Settings = Depends(get_settings),
) -> LLMResourcePlanResponse:
    """Plan GPU strategy for an LLM request while respecting ComfyUI runtime pressure."""

    try:
        provider = settings.llm_provider.strip().lower()
        model = settings.local_llm_model if provider == "local" else settings.server_llm_model
        total_fallback = list(range(settings.llm_gpu_total_devices))
        default_indexes = _parse_gpu_indexes(settings.llm_gpu_default_devices, fallback=total_fallback)
        single_indexes = _parse_gpu_indexes(settings.llm_gpu_single_devices, fallback=default_indexes[:1] or total_fallback[:1])

        comfyui_probe_error: str | None = None
        try:
            comfyui_plan = ComfyUIRuntimeService(settings=settings).video_resource_plan(
                workspace_id=context.workspace_id,
                resource_profile="standard",
                width=1280,
                height=720,
                frames=96,
                fps=24,
                priority=request.priority,
                allow_queue=True,
                metadata={"source": "llm_resource_plan", **request.metadata},
            )
            comfyui_payload = comfyui_plan.model_dump(mode="json")
        except Exception as exc:  # noqa: BLE001 - planning must degrade instead of blocking LLM chat.
            comfyui_probe_error = str(exc)
            comfyui_payload = {
                "admission_status": "unknown",
                "queue_running_count": 0,
                "queue_pending_count": 0,
                "gpu_devices": [],
                "endpoint_plans": [],
                "blocking_reasons": [f"ComfyUI probe failed: {exc.__class__.__name__}"],
                "recommended_actions": ["Confirm ComfyUI base URL from inside the API container before relying on live GPU admission."],
            }
        discovered_gpu_indexes = _unique_ints(
            [
                int(device.get("index"))
                for device in comfyui_payload.get("gpu_devices", [])
                if isinstance(device, dict) and isinstance(device.get("index"), int)
            ]
        )
        all_gpu_indexes = _unique_ints(discovered_gpu_indexes + default_indexes + total_fallback)
        busy_gpu_indexes = _comfyui_busy_gpu_indexes(comfyui_payload)
        comfyui_active = bool(busy_gpu_indexes) or int(comfyui_payload.get("queue_running_count") or 0) > 0
        available_gpu_indexes = [index for index in all_gpu_indexes if index not in busy_gpu_indexes]

        runtime_notes: list[str] = []
        recommended_actions: list[str] = []
        blocking_reasons: list[str] = []
        if not settings.llm_gpu_strategy_enabled:
            recommended_indexes = default_indexes[:1] or all_gpu_indexes[:1]
            mode = "strategy_disabled"
            admission_status = "admitted"
            should_run_now = True
            max_concurrent = 1
            runtime_notes.append("LLM GPU strategy is disabled; using the configured default provider behavior.")
        elif comfyui_active:
            recommended_indexes = [index for index in available_gpu_indexes if index in default_indexes] or available_gpu_indexes[:1]
            max_concurrent = settings.llm_gpu_max_concurrent_with_comfyui
            if recommended_indexes:
                recommended_indexes = recommended_indexes[:1]
                mode = "single_idle_gpu_with_comfyui"
                admission_status = "admitted"
                should_run_now = True
                runtime_notes.append("ComfyUI has active or queued work; LLM is constrained to one idle GPU.")
            else:
                mode = "queued_waiting_for_idle_gpu"
                admission_status = "queued" if request.allow_queue else "blocked"
                should_run_now = False
                blocking_reasons.append("No idle GPU is available while ComfyUI has active or queued work.")
                recommended_actions.append("Wait for the ComfyUI queue to drain, or move ComfyUI to a dedicated GPU endpoint.")
        else:
            recommended_indexes = [index for index in default_indexes if index in all_gpu_indexes] or default_indexes or all_gpu_indexes
            max_concurrent = settings.llm_gpu_max_concurrent_without_comfyui
            mode = "dual_gpu_llm" if len(recommended_indexes) >= 2 else "single_gpu_llm"
            admission_status = "admitted"
            should_run_now = True
            runtime_notes.append("No active ComfyUI queue detected; LLM may use the configured multi-GPU device set.")
        if comfyui_probe_error:
            runtime_notes.append(f"ComfyUI probe failed, using configured LLM GPU defaults: {comfyui_probe_error}")

        recommended_indexes = _unique_ints(recommended_indexes)
        cuda_visible_devices = ",".join(str(index) for index in recommended_indexes) if recommended_indexes else None
        ollama_options: dict[str, Any] = {
            "num_gpu": -1 if len(recommended_indexes) >= 2 else 999,
            "main_gpu": recommended_indexes[0] if recommended_indexes else None,
            "num_batch": settings.local_llm_num_batch,
        }
        if len(recommended_indexes) >= 2 and not comfyui_active:
            runtime_notes.append(
                "Dual 5090 mode is performance-first; around 50% utilization per GPU can still happen when decoding is request-bound, but the model is allowed to spread across both cards."
            )
            recommended_actions.append(
                "Restart Ollama with OLLAMA_SCHED_SPREAD=true after changing GPU strategy so the running daemon picks up multi-GPU scheduling preferences."
            )
        recommended_actions.append(
            "For Ollama, per-request CUDA_VISIBLE_DEVICES is advisory; make sure the local LLM service or worker launcher applies this plan."
        )

        return LLMResourcePlanResponse(
            success=admission_status in {"admitted", "queued"},
            provider=provider,
            model=model,
            workspace_id=context.workspace_id,
            strategy_enabled=settings.llm_gpu_strategy_enabled,
            mode=mode,
            admission_status=admission_status,
            should_run_now=should_run_now,
            recommended_gpu_indexes=recommended_indexes,
            cuda_visible_devices=cuda_visible_devices,
            max_concurrent_llm_requests=max_concurrent,
            comfyui_active=comfyui_active,
            comfyui_busy_gpu_indexes=busy_gpu_indexes,
            available_gpu_indexes=available_gpu_indexes,
            ollama_options={key: value for key, value in ollama_options.items() if value is not None},
            runtime_notes=runtime_notes,
            recommended_actions=list(dict.fromkeys(recommended_actions)),
            blocking_reasons=blocking_reasons,
            comfyui_resource_plan=comfyui_payload,
        )
    except Exception as exc:
        logger.exception("LLM resource plan API failed")
        raise AppError(str(exc) or "LLM resource plan failed", status_code=500) from exc


@router.post("/test", response_model=LLMResponse)
async def test_llm(request: LLMRequest) -> LLMResponse:
    """测试 LLM Client Layer。"""

    try:
        client = LLMClient()
        response = await client.generate(request)
        logger.info(
            "LLM test API completed",
            extra={"provider": response.provider, "model": response.model},
        )
        return response
    except ValueError as exc:
        logger.warning("LLM test API received invalid request", extra={"error": str(exc)})
        raise AppError(str(exc), status_code=400) from exc
    except Exception as exc:
        logger.exception("LLM test API failed")
        raise AppError(str(exc) or "LLM test failed", status_code=500) from exc
