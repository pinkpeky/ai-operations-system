"""Generate an AI virtual-host keyframe from a clean KTV scene image."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import time
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.comfyui_runtime.workflow_materializer import ComfyUIWorkflowMaterializer


DEFAULT_AGENT_OUTPUT = (
    PROJECT_ROOT
    / "deployment"
    / "comfyui"
    / "commercial_ktv_workflow"
    / "original_douyin_requirement_video_agent_output.json"
)
DEFAULT_REPORT = (
    PROJECT_ROOT
    / "deployment"
    / "comfyui"
    / "commercial_ktv_workflow"
    / "original_douyin_requirement_ai_host_seed_result.json"
)
DEFAULT_SCENE = (
    PROJECT_ROOT
    / "storage"
    / "digital_human_assets"
    / "ktv-backend-20260527"
    / "4551e9fc-3866-408e-8f7f-8d12ca961ccc.jpg"
)
DEFAULT_COMFYUI_INPUT = Path("E:/ComfyUI_cu130/ComfyUI/input")
DEFAULT_COMFYUI_OUTPUT = Path("E:/ComfyUI_cu130/ComfyUI/output")
DEFAULT_WORKFLOW_NAME = "Qwen-Image-Edit_图生图_单图编辑(GGUF).json"


POSITIVE_PROMPT = (
    "Edit the supplied KTV private-room scene into a realistic vertical commercial keyframe. "
    "Add one fictional adult East Asian AI female host standing naturally in the room, elegant and beautiful, "
    "normal face, normal hands, normal full-body proportions, tasteful black business-evening dress, confident presenter posture, "
    "soft smile, looking toward camera. Preserve the original room layout, sofa, table, screen, glass wall, blue neon lighting, "
    "camera perspective, reflections, and upscale KTV atmosphere. The host must look generated and fictional, not a real person cutout. "
    "No collage, no subtitles, no watermark, no Douyin UI, no extra people."
)
NEGATIVE_PROMPT = (
    "distorted face, asymmetrical eyes, bad hands, extra fingers, extra limbs, broken body, childlike appearance, "
    "real person cutout, pasted portrait, watermark, subtitles, QR code, Douyin interface, collage, multiple panels, "
    "changed room layout, plastic skin, severe blur, low quality"
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent-output", type=Path, default=DEFAULT_AGENT_OUTPUT)
    parser.add_argument("--scene-image", type=Path, default=DEFAULT_SCENE)
    parser.add_argument("--scene-image-name", default="ktv_clean_scene_for_ai_host.jpg")
    parser.add_argument("--output-seed-name", default="scene_ai_virtual_host_seed_v2.png")
    parser.add_argument("--base-url", default="http://127.0.0.1:8188")
    parser.add_argument("--comfyui-input-dir", type=Path, default=DEFAULT_COMFYUI_INPUT)
    parser.add_argument("--comfyui-output-dir", type=Path, default=DEFAULT_COMFYUI_OUTPUT)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--run-id", default="original_douyin_requirement_ai_host_seed")
    parser.add_argument("--stage-key", default="ai_virtual_host_seed")
    parser.add_argument("--workflow-name", default=DEFAULT_WORKFLOW_NAME)
    parser.add_argument("--workflow-rank", type=int, default=None)
    parser.add_argument("--positive-prompt", default=POSITIVE_PROMPT)
    parser.add_argument("--negative-prompt", default=NEGATIVE_PROMPT)
    parser.add_argument("--timeout-seconds", type=int, default=900)
    parser.add_argument("--poll-interval-seconds", type=int, default=5)
    args = parser.parse_args()

    args.comfyui_input_dir.mkdir(parents=True, exist_ok=True)
    scene_input_path = args.comfyui_input_dir / args.scene_image_name
    shutil.copy2(args.scene_image, scene_input_path)

    agent_output = json.loads(args.agent_output.read_text(encoding="utf-8"))
    workflow = _selected_seed_workflow(agent_output, workflow_name=args.workflow_name, rank=args.workflow_rank)
    source_workflow_path = Path(workflow["workflow_path"])
    object_info = _get_json(f"{args.base_url.rstrip('/')}/object_info")

    materializer = ComfyUIWorkflowMaterializer()
    result = materializer.materialize_api_prompt(
        source_workflow_path=source_workflow_path,
        parameter_plan={
            "positive_prompt": args.positive_prompt,
            "negative_prompt": args.negative_prompt,
        },
        stage_key=args.stage_key,
        run_id=args.run_id,
        input_assets={"scene_image_name": args.scene_image_name},
        node_overrides=_node_overrides(
            workflow_name=str(workflow.get("workflow_name") or ""),
            scene_image_name=args.scene_image_name,
            output_prefix=f"aiops/{args.run_id}/{args.stage_key}/ai_virtual_host_seed",
            positive_prompt=args.positive_prompt,
            negative_prompt=args.negative_prompt,
        ),
        output_prefix=f"aiops/{args.run_id}/{args.stage_key}/ai_virtual_host_seed",
        object_info=object_info,
    )

    report: dict[str, Any] = {
        "status": "blocked" if not result.prompt_ready else "prompt_ready",
        "queue_submission_attempted": False,
        "base_url": args.base_url,
        "selected_workflow": workflow,
        "scene_source_path": str(args.scene_image),
        "scene_input_path": str(scene_input_path),
        "materialized_workflow_path": result.materialization.materialized_workflow_path,
        "api_prompt_path": result.api_prompt_path,
        "source_workflow_original_unchanged": result.materialization.original_unchanged,
        "api_prompt_node_count": result.api_prompt_node_count,
        "positive_prompt": args.positive_prompt,
        "negative_prompt": args.negative_prompt,
        "missing_node_types": result.missing_node_types,
        "unresolved_inputs": result.unresolved_inputs[:100],
    }
    if not result.prompt_ready:
        _write_report(args.report_path, report)
        print(json.dumps(_summary(report), ensure_ascii=False, indent=2))
        return

    os.environ["COMFYUI_RUNTIME_BASE_URL"] = args.base_url
    from app.comfyui_runtime.service import ComfyUIRuntimeService

    api_prompt = json.loads(Path(result.api_prompt_path).read_text(encoding="utf-8"))
    materialized_workflow = json.loads(Path(result.materialization.materialized_workflow_path).read_text(encoding="utf-8"))
    submit = ComfyUIRuntimeService().submit_prompt_job(
        prompt=api_prompt,
        workflow=materialized_workflow,
        client_id=f"aiops-{args.run_id}",
        workspace_id="local-runtime",
        media_type="image",
        metadata={
            "purpose": "original_douyin_requirement_ai_virtual_host_seed",
            "api_prompt_path": result.api_prompt_path,
        },
    )
    report["queue_submission_attempted"] = submit.external_request_attempted
    report["submit_response"] = submit.model_dump(mode="json")
    if not submit.success or not submit.prompt_id:
        report["status"] = "submit_failed"
        _write_report(args.report_path, report)
        print(json.dumps(_summary(report), ensure_ascii=False, indent=2))
        return

    history = _poll_history(
        base_url=args.base_url,
        prompt_id=submit.prompt_id,
        timeout_seconds=args.timeout_seconds,
        poll_interval_seconds=args.poll_interval_seconds,
    )
    history_path = args.report_path.with_name(args.report_path.stem + "_history.json")
    history_path.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")
    outputs = history.get(submit.prompt_id, {}).get("outputs", {}) if isinstance(history, dict) else {}
    output_files = _resolve_output_files(outputs, output_dir=args.comfyui_output_dir)
    seed_candidate = _first_existing_image(output_files)
    if seed_candidate:
        registered_seed = args.comfyui_input_dir / args.output_seed_name
        shutil.copy2(seed_candidate, registered_seed)
    else:
        registered_seed = None

    item = history.get(submit.prompt_id, {}) if isinstance(history, dict) else {}
    report.update(
        {
            "status": "success" if registered_seed else "output_missing",
            "prompt_id": submit.prompt_id,
            "history_path": str(history_path),
            "history_status": item.get("status"),
            "outputs": output_files,
            "registered_seed_path": str(registered_seed) if registered_seed else None,
            "registered_seed_name": args.output_seed_name if registered_seed else None,
        }
    )
    _write_report(args.report_path, report)
    print(json.dumps(_summary(report), ensure_ascii=False, indent=2))


def _selected_seed_workflow(
    agent_output: dict[str, Any],
    *,
    workflow_name: str | None,
    rank: int | None,
) -> dict[str, Any]:
    if workflow_name:
        workflow = _workflow_from_rag(workflow_name)
        if workflow:
            return workflow

    selected = (
        agent_output.get("execution_package", {})
        .get("workflow_stages", {})
        .get("ai_virtual_host_seed", {})
        .get("selected", [])
    )
    if rank is not None:
        for item in selected:
            if int(item.get("rank") or 0) == rank:
                return dict(item)
    if selected:
        return dict(selected[0])
    raise ValueError("No ai_virtual_host_seed workflow candidates found.")


def _workflow_from_rag(workflow_name: str) -> dict[str, Any] | None:
    rag_path = PROJECT_ROOT / "deployment" / "comfyui" / "commercial_ktv_workflow" / "cu130_runtime_workflow_rag_documents.jsonl"
    if not rag_path.exists():
        return None
    for line in rag_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        metadata = dict(item.get("metadata") or {})
        if metadata.get("workflow_name") == workflow_name:
            return {
                "rank": None,
                "score": None,
                "workflow_id": item.get("source_id"),
                "workflow_name": metadata.get("workflow_name"),
                "category": metadata.get("category"),
                "capabilities": metadata.get("capabilities") or [],
                "workflow_path": metadata.get("workflow_path"),
                "workflow_path_exists": Path(str(metadata.get("workflow_path") or "")).exists(),
                "runtime_readiness": metadata.get("runtime_readiness"),
                "requires_prompt_validation": metadata.get("requires_prompt_validation"),
                "model_refs_missing": metadata.get("model_refs_missing") or [],
                "missing_executable_node_types": metadata.get("missing_executable_node_types") or [],
                "selection_reason": "stable_single_image_qwen_edit_candidate",
            }
    return None


def _node_overrides(
    *,
    workflow_name: str,
    scene_image_name: str,
    output_prefix: str,
    positive_prompt: str,
    negative_prompt: str,
) -> dict[str, dict[str, Any]]:
    if workflow_name == DEFAULT_WORKFLOW_NAME:
        return {
            "3": {"steps": 4, "cfg": 1, "sampler_name": "euler", "scheduler": "simple", "denoise": 1},
            "60": {"filename_prefix": output_prefix},
            "76": {"prompt": positive_prompt},
            "77": {"prompt": negative_prompt},
            "78": {"image": scene_image_name},
        }
    return {
        "7": {"image": scene_image_name},
        "8": {"filename_prefix": output_prefix},
        "15": {"prompt": negative_prompt},
        "16": {"file_path": "", "dictionary_name": "[filename]", "label": "TextBatch", "mode": "index"},
        "34": {"text": positive_prompt},
        "63": {"Number": "1"},
    }


def _get_json(url: str) -> Any:
    request = Request(url, headers={"Accept": "application/json"}, method="GET")
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def _poll_history(
    *,
    base_url: str,
    prompt_id: str,
    timeout_seconds: int,
    poll_interval_seconds: int,
) -> dict[str, Any]:
    deadline = time.monotonic() + timeout_seconds
    url = f"{base_url.rstrip('/')}/history/{prompt_id}"
    while time.monotonic() < deadline:
        history = _get_json(url)
        item = history.get(prompt_id) if isinstance(history, dict) else None
        if isinstance(item, dict) and item.get("status"):
            return history
        time.sleep(max(1, poll_interval_seconds))
    return _get_json(url)


def _resolve_output_files(outputs: dict[str, Any], *, output_dir: Path) -> list[dict[str, Any]]:
    files: list[dict[str, Any]] = []
    for node_id, payload in outputs.items():
        if not isinstance(payload, dict):
            continue
        for key, values in payload.items():
            if not isinstance(values, list):
                continue
            for value in values:
                if not isinstance(value, dict) or not value.get("filename"):
                    continue
                path = output_dir / str(value.get("subfolder") or "") / str(value["filename"])
                files.append(
                    {
                        "node_id": str(node_id),
                        "key": str(key),
                        "filename": value.get("filename"),
                        "subfolder": value.get("subfolder") or "",
                        "type": value.get("type"),
                        "format": value.get("format"),
                        "path": str(path),
                        "exists": path.exists(),
                        "size_bytes": path.stat().st_size if path.exists() else None,
                    }
                )
    return files


def _first_existing_image(files: list[dict[str, Any]]) -> Path | None:
    for item in files:
        path = Path(str(item.get("path") or ""))
        if path.exists() and path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
            return path
    return None


def _write_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


def _summary(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": report.get("status"),
        "queue_submission_attempted": report.get("queue_submission_attempted"),
        "prompt_id": report.get("prompt_id") or report.get("submit_response", {}).get("prompt_id"),
        "source_workflow_original_unchanged": report.get("source_workflow_original_unchanged"),
        "missing_node_types": report.get("missing_node_types"),
        "unresolved_inputs_count": len(report.get("unresolved_inputs") or []),
        "registered_seed_path": report.get("registered_seed_path"),
        "api_prompt_path": report.get("api_prompt_path"),
    }


if __name__ == "__main__":
    main()
