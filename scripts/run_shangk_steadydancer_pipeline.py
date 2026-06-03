"""Run ShangK first-frame action transfer with the SteadyDancer workflow."""

from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.comfyui_runtime.service import ComfyUIRuntimeService
from app.comfyui_runtime.workflow_materializer import ComfyUIWorkflowMaterializer
from scripts.run_shangk_full_pipeline import (
    COMFY_INPUT,
    COMFY_OUTPUT,
    SHANGK_INPUT,
    _contact_sheet,
    _duration_seconds,
    _ffprobe,
    _latest_file,
)
from scripts.run_shangk_reference_action_pipeline import (
    ROOT_FIRST_FRAME_NAME,
    ROOT_REFERENCE_VIDEO_NAME,
    _first_existing,
    _prune_prompt_to_outputs,
    _resolve_output_files,
    _video_fps,
    _workflow_from_source_id,
)


REPORT_DIR = PROJECT_ROOT / "deployment" / "comfyui" / "commercial_ktv_workflow" / "shangk_reference_action"
STEADYDANCER_WORKFLOW_SOURCE_ID = "comfyui_cu130_runtime_205d902be9f1"
OUTPUT_PREFIX = "商k/视频生成/shangk_steadydancer_action"
STEADYDANCER_MODEL = "Wan\\Wan21_SteadyDancer_fp16-Q5_K_S_fix_5d_tensor_from_fp8_e4m3fn_scaled_KJ.gguf"

PROMPT = (
    "A fictional adult AI female singer in a black sequined mini dress performs the reference video's standing KTV singer dance. "
    "Use the reference video only for body motion, pose sequence, rhythm, camera timing, and microphone performance. "
    "Keep the first frame identity, target ShangK room, blue neon lighting, sofa, table, glossy floor reflections, and microphone. "
    "She sings toward the camera, holds the wireless microphone, shifts weight, sways, raises her arm, and performs light dance gestures."
)
NEGATIVE = (
    "static still frame, no movement, seated, sitting, missing microphone, duplicated person, deformed face, bad hands, extra fingers, "
    "broken legs, body melting, severe flicker, copied reference video background, silver dress, subtitles, watermark, low quality, blur"
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8188")
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--reference-dir", type=Path, default=SHANGK_INPUT / "视频参考")
    parser.add_argument("--width", type=int, default=480)
    parser.add_argument("--height", type=int, default=832)
    parser.add_argument("--fps", type=float, default=16.0)
    parser.add_argument("--steps", type=int, default=4)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--timeout-seconds", type=int, default=14400)
    args = parser.parse_args()

    run_id = args.run_id or f"shangk_steadydancer_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.environ["COMFYUI_RUNTIME_BASE_URL"] = args.base_url
    os.environ["COMFYUI_VIDEO_GPU_ENDPOINTS"] = f"default|{args.base_url}|0"
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    (COMFY_OUTPUT / "商k" / "视频生成").mkdir(parents=True, exist_ok=True)

    reference_video = _latest_file(args.reference_dir, {".mp4", ".mov", ".mkv", ".webm"})
    reference_input = COMFY_INPUT / ROOT_REFERENCE_VIDEO_NAME
    shutil.copy2(reference_video, reference_input)
    first_frame_input = COMFY_INPUT / ROOT_FIRST_FRAME_NAME
    if not first_frame_input.exists():
        fallback = COMFY_INPUT / "商k" / ROOT_FIRST_FRAME_NAME
        if fallback.exists():
            shutil.copy2(fallback, first_frame_input)
    if not first_frame_input.exists():
        raise FileNotFoundError(f"Standing first frame not found in ComfyUI input: {first_frame_input}")

    reference_probe = _ffprobe(reference_input)
    duration_seconds = _duration_seconds(reference_probe) or 1.0
    source_fps = _video_fps(reference_probe) or 30.0
    whole_seconds = max(1, int(math.ceil(duration_seconds)))
    generation_frames = whole_seconds * int(round(args.fps)) + 1

    materializer = ComfyUIWorkflowMaterializer()
    workflow = _workflow_from_source_id(STEADYDANCER_WORKFLOW_SOURCE_ID)
    object_info = _get_json(f"{args.base_url.rstrip('/')}/object_info")
    result = materializer.materialize_api_prompt(
        source_workflow_path=workflow["workflow_path"],
        parameter_plan={
            "positive_prompt": PROMPT,
            "negative_prompt": NEGATIVE,
            "width": args.width,
            "height": args.height,
            "fps": args.fps,
        },
        stage_key="shangk_steadydancer_action",
        run_id=run_id,
        input_assets={"approved_keyframe_name": first_frame_input.name, "reference_video_name": reference_input.name},
        node_overrides={
            "75": {
                "video": reference_input.name,
                "force_rate": args.fps,
                "custom_width": args.width,
                "custom_height": args.height,
                "frame_load_cap": generation_frames,
                "skip_first_frames": 0,
                "select_every_nth": 1,
                "format": "AnimateDiff",
            },
            "76": {"image": first_frame_input.name},
            "202": {
                "model": STEADYDANCER_MODEL,
                "base_precision": "fp16_fast",
                "quantization": "disabled",
                "load_device": "offload_device",
                "attention_mode": "sageattn",
                "rms_norm_function": "default",
            },
            "214": {"Number": str(whole_seconds)},
            "215": {"value": args.fps},
            "219": {"Number": str(args.width)},
            "220": {"Number": str(args.height)},
            "189": {"text": PROMPT},
            "92": {"negative_prompt": NEGATIVE, "use_disk_cache": False},
            "119": {
                "steps": args.steps,
                "cfg": 1.0,
                "shift": 5.0,
                "seed": args.seed,
                "force_offload": True,
                "denoise_strength": 1.0,
                "batched_cfg": False,
            },
            "122": {"steps": args.steps, "shift": 5.0, "scheduler": "dpm++_sde"},
            "142": {
                "frame_rate": args.fps,
                "filename_prefix": OUTPUT_PREFIX,
                "format": "video/h264-mp4",
                "save_output": True,
                "trim_to_audio": False,
            },
        },
        output_prefix=OUTPUT_PREFIX,
        object_info=object_info,
    )

    prompt_path = Path(result.api_prompt_path)
    prompt = json.loads(prompt_path.read_text(encoding="utf-8"))
    prompt = _prune_prompt_to_outputs(prompt, output_node_ids={"142"})
    _drop_links_to_missing_nodes(prompt, optional_inputs={"compile_args"})
    patched_preflight = materializer.preflight_api_prompt(prompt, object_info=object_info)
    if not patched_preflight["prompt_ready"]:
        raise RuntimeError(
            f"Patched SteadyDancer preflight failed: {patched_preflight['missing_node_types']} "
            f"{patched_preflight['unresolved_inputs'][:8]}; "
            f"initial_preflight={result.missing_node_types} {result.unresolved_inputs[:8]}"
        )
    prompt_path.write_text(json.dumps(prompt, ensure_ascii=False, indent=2), encoding="utf-8")

    service = ComfyUIRuntimeService()
    workflow_payload = json.loads(Path(result.materialization.materialized_workflow_path).read_text(encoding="utf-8"))
    submit = service.submit_prompt_job(
        prompt=prompt,
        workflow=workflow_payload,
        client_id=f"aiops-{run_id}-steadydancer",
        workspace_id="local-runtime",
        media_type="video",
        resource_profile="standard",
        width=args.width,
        height=args.height,
        frames=generation_frames,
        fps=args.fps,
        duration_seconds=duration_seconds,
        metadata={"purpose": "shangk_steadydancer_action_transfer", "run_id": run_id},
    )
    if not submit.success or not submit.prompt_id:
        raise RuntimeError(f"SteadyDancer submit failed: {submit.error or submit.node_errors}")

    history = _poll_history_direct(
        prompt_id=submit.prompt_id,
        base_url=submit.base_url or args.base_url,
        timeout_seconds=args.timeout_seconds,
    )
    outputs = _history_outputs_direct(history, submit.prompt_id)
    files = _resolve_output_files(outputs)
    video = _first_existing(files, {".mp4", ".mov", ".webm", ".mkv"})
    if video is None:
        raise RuntimeError(f"SteadyDancer produced no video. prompt_id={submit.prompt_id}")

    raw_named = COMFY_OUTPUT / "商k" / "视频生成" / f"{run_id}_raw_480x832.mp4"
    shutil.copy2(video, raw_named)
    raw_contact = REPORT_DIR / f"{run_id}_raw_contact.jpg"
    _contact_sheet(raw_named, raw_contact)
    delivery_video = COMFY_OUTPUT / "商k" / "视频生成" / f"{run_id}_delivery_1080x1920.mp4"
    _make_delivery_video(
        generated_video=raw_named,
        reference_video=reference_input,
        output_path=delivery_video,
        source_fps=source_fps,
        duration_seconds=duration_seconds,
    )
    delivery_contact = REPORT_DIR / f"{run_id}_delivery_contact.jpg"
    _contact_sheet(delivery_video, delivery_contact)

    report = {
        "status": "success",
        "run_id": run_id,
        "workflow": workflow,
        "prompt_id": submit.prompt_id,
        "source_reference_video": str(reference_video),
        "reference_input": str(reference_input),
        "first_frame_input": str(first_frame_input),
        "duration_seconds": duration_seconds,
        "generation_frames": generation_frames,
        "generation_fps": args.fps,
        "prompt": PROMPT,
        "negative_prompt": NEGATIVE,
        "materialized_workflow_path": result.materialization.materialized_workflow_path,
        "api_prompt_path": str(prompt_path),
        "raw_video": str(raw_named),
        "raw_probe": _ffprobe(raw_named),
        "raw_contact_sheet": str(raw_contact),
        "delivery_video": str(delivery_video),
        "delivery_probe": _ffprobe(delivery_video),
        "delivery_contact_sheet": str(delivery_contact),
        "history_status": _history_status_direct(history, submit.prompt_id),
        "output_files": files,
        "submit": submit.model_dump(mode="json"),
    }
    report_path = REPORT_DIR / f"{run_id}_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"report": str(report_path), "raw_video": str(raw_named), "delivery_video": str(delivery_video)}, ensure_ascii=False, indent=2))


def _get_json(url: str) -> Any:
    request = Request(url, headers={"Accept": "application/json"}, method="GET")
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def _poll_history_direct(*, prompt_id: str, base_url: str, timeout_seconds: int) -> dict[str, Any]:
    deadline = time.monotonic() + timeout_seconds
    last_payload: dict[str, Any] = {}
    while time.monotonic() < deadline:
        last_payload = _get_json(f"{base_url.rstrip('/')}/history/{prompt_id}")
        item = last_payload.get(prompt_id, {}) if isinstance(last_payload, dict) else {}
        outputs = item.get("outputs") if isinstance(item, dict) else None
        status = item.get("status") if isinstance(item, dict) else None
        if outputs or (isinstance(status, dict) and status.get("completed")):
            return last_payload
        time.sleep(10)
    return last_payload


def _history_outputs_direct(history: dict[str, Any], prompt_id: str) -> dict[str, Any]:
    item = history.get(prompt_id) if isinstance(history, dict) else None
    if not isinstance(item, dict):
        return {}
    outputs = item.get("outputs")
    return outputs if isinstance(outputs, dict) else {}


def _drop_links_to_missing_nodes(prompt: dict[str, Any], *, optional_inputs: set[str]) -> None:
    node_ids = {str(node_id) for node_id in prompt}
    for node in prompt.values():
        if not isinstance(node, dict):
            continue
        inputs = node.get("inputs")
        if not isinstance(inputs, dict):
            continue
        for input_name in list(inputs):
            value = inputs[input_name]
            if (
                input_name in optional_inputs
                and isinstance(value, list)
                and len(value) == 2
                and str(value[0]) not in node_ids
            ):
                inputs.pop(input_name, None)


def _history_status_direct(history: dict[str, Any], prompt_id: str) -> dict[str, Any]:
    item = history.get(prompt_id) if isinstance(history, dict) else None
    if not isinstance(item, dict):
        return {}
    status = item.get("status")
    return status if isinstance(status, dict) else {}


def _make_delivery_video(
    *,
    generated_video: Path,
    reference_video: Path,
    output_path: Path,
    source_fps: float,
    duration_seconds: float,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    vf = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps={fps},setsar=1".format(
        fps=max(1, round(source_fps))
    )
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(generated_video),
            "-i",
            str(reference_video),
            "-map",
            "0:v:0",
            "-map",
            "1:a:0?",
            "-vf",
            vf,
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-shortest",
            "-t",
            f"{duration_seconds:.3f}",
            str(output_path),
        ],
        check=True,
    )


if __name__ == "__main__":
    main()
