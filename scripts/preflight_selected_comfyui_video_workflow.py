"""Build and preflight the selected ComfyUI video workflow without queue submission."""

from __future__ import annotations

import argparse
import json
import sys
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
    / "original_douyin_requirement_comfyui_preflight.json"
)
DEFAULT_COMFYUI_INPUT_DIR = Path("E:/ComfyUI_cu130/ComfyUI/input")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent-output", type=Path, default=DEFAULT_AGENT_OUTPUT)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--base-url", default="http://127.0.0.1:8188")
    parser.add_argument("--run-id", default="original_douyin_requirement_preflight")
    parser.add_argument("--stage-key", default="digital_human_i2v")
    parser.add_argument("--comfyui-input-dir", type=Path, default=DEFAULT_COMFYUI_INPUT_DIR)
    parser.add_argument("--scene-image-name", default="scene_ai_virtual_host_seed.png")
    parser.add_argument("--voice-audio-name", default="voiceover.wav")
    parser.add_argument("--source-video-name", default="douyin_7575632283172932870.mp4")
    parser.add_argument("--frames", type=int, default=None, help="Override the selected InfiniteTalk frame constant node.")
    parser.add_argument("--scale-to-length", type=int, default=None, help="Override the selected keyframe scale constant node.")
    parser.add_argument("--wan-model", default=None, help="Override WanVideoModelLoader node 122 model.")
    parser.add_argument("--multitalk-model", default=None, help="Override MultiTalkModelLoader node 120 model.")
    args = parser.parse_args()

    agent_output = json.loads(args.agent_output.read_text(encoding="utf-8"))
    execution_package = agent_output["execution_package"]
    selected_workflow = execution_package["selected_primary_workflow"]
    source_workflow_path = Path(selected_workflow["workflow_path"])
    parameter_plan = dict(execution_package.get("parameter_plan") or {})

    object_info = _get_json(f"{args.base_url.rstrip('/')}/object_info")
    node_overrides = _node_overrides(
        frames=args.frames,
        scale_to_length=args.scale_to_length,
        wan_model=args.wan_model,
        multitalk_model=args.multitalk_model,
    )
    materializer = ComfyUIWorkflowMaterializer()
    result = materializer.materialize_api_prompt(
        source_workflow_path=source_workflow_path,
        parameter_plan=parameter_plan,
        stage_key=args.stage_key,
        run_id=args.run_id,
        input_assets={
            "approved_keyframe_name": args.scene_image_name,
            "scene_image_name": args.scene_image_name,
            "voice_audio_name": args.voice_audio_name,
            "source_video_name": args.source_video_name,
        },
        node_overrides=node_overrides,
        object_info=object_info,
    )

    required_assets = [
        {"role": "scene_ai_virtual_host_keyframe", "name": args.scene_image_name},
        {"role": "voice_or_song_audio", "name": args.voice_audio_name},
    ]
    asset_preflight = _asset_preflight(args.comfyui_input_dir, required_assets)
    report = {
        "status": "ready_for_queue_submit" if result.prompt_ready and asset_preflight["asset_ready"] else "blocked",
        "queue_submission_attempted": False,
        "base_url": args.base_url,
        "object_info_node_type_count": len(object_info) if isinstance(object_info, dict) else 0,
        "source_workflow_path": str(source_workflow_path),
        "materialized_workflow_path": result.materialization.materialized_workflow_path,
        "api_prompt_path": result.api_prompt_path,
        "graph_format": result.materialization.graph_format,
        "source_workflow_original_unchanged": result.materialization.original_unchanged,
        "api_prompt_node_count": result.api_prompt_node_count,
        "prompt_structurally_ready": result.prompt_ready,
        "missing_node_types": result.missing_node_types,
        "unresolved_inputs_count": len(result.unresolved_inputs),
        "unresolved_inputs_sample": result.unresolved_inputs[:50],
        "asset_preflight": asset_preflight,
        "selected_workflow": selected_workflow,
        "parameter_plan": parameter_plan,
        "node_overrides": node_overrides,
        "next_required_action": _next_required_action(result.prompt_ready, asset_preflight["missing_assets"]),
    }
    args.report_path.parent.mkdir(parents=True, exist_ok=True)
    args.report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({key: report[key] for key in _summary_keys()}, ensure_ascii=False, indent=2))


def _get_json(url: str) -> Any:
    request = Request(url, headers={"Accept": "application/json"}, method="GET")
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def _asset_preflight(input_dir: Path, required_assets: list[dict[str, str]]) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    missing: list[dict[str, str]] = []
    for asset in required_assets:
        path = input_dir / asset["name"]
        item = {
            "role": asset["role"],
            "name": asset["name"],
            "path": str(path),
            "exists": path.exists(),
            "size_bytes": path.stat().st_size if path.exists() else None,
        }
        checks.append(item)
        if not item["exists"]:
            missing.append({"role": asset["role"], "name": asset["name"], "path": str(path)})
    return {
        "comfyui_input_dir": str(input_dir),
        "asset_ready": not missing,
        "missing_assets": missing,
        "checks": checks,
    }


def _node_overrides(
    *,
    frames: int | None,
    scale_to_length: int | None,
    wan_model: str | None,
    multitalk_model: str | None,
) -> dict[str, dict[str, Any]]:
    overrides: dict[str, dict[str, Any]] = {}
    if frames is not None:
        overrides["320"] = {"value": max(1, int(frames))}
    if scale_to_length is not None:
        overrides["319"] = {"value": max(64, int(scale_to_length))}
    if wan_model:
        overrides.setdefault("122", {})["model"] = wan_model
    if multitalk_model:
        overrides.setdefault("120", {})["model"] = multitalk_model
    return overrides


def _next_required_action(prompt_ready: bool, missing_assets: list[dict[str, str]]) -> str:
    if not prompt_ready:
        return "Fix missing node types or required inputs before any ComfyUI queue submission."
    if missing_assets:
        names = ", ".join(item["name"] for item in missing_assets)
        return f"Place required runtime assets into the ComfyUI input directory before queue submission: {names}."
    return "Prompt and runtime assets are ready for guarded short video queue submission."


def _summary_keys() -> list[str]:
    return [
        "status",
        "queue_submission_attempted",
        "source_workflow_original_unchanged",
        "api_prompt_node_count",
        "prompt_structurally_ready",
        "missing_node_types",
        "unresolved_inputs_count",
        "asset_preflight",
        "next_required_action",
        "api_prompt_path",
    ]


if __name__ == "__main__":
    main()
