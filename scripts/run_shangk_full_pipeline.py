"""Run the ShangK scene-to-first-frame-to-video ComfyUI pipeline."""

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

from app.comfyui_runtime.workflow_materializer import ComfyUIWorkflowMaterializer


COMFY_ROOT = Path("E:/ComfyUI_cu130/ComfyUI")
COMFY_INPUT = COMFY_ROOT / "input"
COMFY_OUTPUT = COMFY_ROOT / "output"
SHANGK_INPUT = COMFY_INPUT / "商k"
SHANGK_OUTPUT = COMFY_OUTPUT / "商k"
DEFAULT_AGENT_OUTPUT = (
    PROJECT_ROOT
    / "deployment"
    / "comfyui"
    / "commercial_ktv_workflow"
    / "original_douyin_requirement_video_agent_output.json"
)
DEFAULT_REPORT_DIR = PROJECT_ROOT / "deployment" / "comfyui" / "commercial_ktv_workflow" / "shangk_full_pipeline"
QWEN_EDIT_WORKFLOW_NAME = "Qwen-Image-Edit_图生图_单图编辑(GGUF).json"
WAN_MODEL = "Wan\\Wan2.1-I2V_14B_480p_fp8_e4m3fn_scaled_KJ.safetensors"
INFINITETALK_MODEL = "Wan\\Wan2_1-InfiniteTalk-Single_fp8_e4m3fn_scaled_KJ.safetensors"


FIRST_FRAME_PROMPT = (
    "Use the supplied ShangK private-room scene as the exact background. Create a premium vertical commercial "
    "first frame for a high-end KTV/private club short video. Add one fictional adult AI female commercial lead "
    "inside the room, beautiful and elegant, confident nightlife host temperament, refined black evening outfit, "
    "natural face, normal hands, normal body proportions, standing or leaning naturally near the sofa/table area "
    "without blocking the key room features. Preserve the room layout, sofa, table, microphone, bottles, screen, "
    "neon wall lines, glossy floor reflections, dark luxury lighting, camera perspective, and 9:16 composition. "
    "The image should look like a polished Douyin commercial opening frame, not a selfie, not a collage, not a real-person cutout."
)
FIRST_FRAME_NEGATIVE = (
    "distorted face, asymmetrical eyes, bad hands, extra fingers, missing fingers, extra limbs, broken body, childlike, "
    "old face, male, real person cutout, pasted portrait, duplicate people, crowd, watermark, subtitles, QR code, Douyin UI, "
    "changed room layout, messy background, severe blur, plastic skin, low quality"
)
VIDEO_PROMPT = (
    "Keep the approved AI female lead identity and the ShangK KTV room unchanged. Generate a stable vertical commercial "
    "short-video shot with a premium nightlife advertising feel. The subject reacts naturally to the reference audio, "
    "with subtle body turn, elegant shoulder movement, small hand gesture, slight head movement, confident gaze, and "
    "controlled camera-like motion. Preserve facial beauty, outfit, sofa, table, microphone, bottles, screen, neon lines, "
    "glossy reflections, and the original 9:16 framing. The shot should feel like a usable commercial scene segment, "
    "not only a static talking head."
)
VIDEO_NEGATIVE = (
    "distorted face, asymmetrical eyes, bad hands, extra fingers, extra limbs, broken body, childlike appearance, "
    "real person cutout, watermark, unreadable text, changed room layout, severe flicker, plastic skin, heavy camera shake, "
    "large dance movement, scene jump, duplicate person, background melting"
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8188")
    parser.add_argument("--agent-output", type=Path, default=DEFAULT_AGENT_OUTPUT)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--scene-dir", type=Path, default=SHANGK_INPUT / "场景")
    parser.add_argument("--reference-dir", type=Path, default=SHANGK_INPUT / "视频参考")
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--fps", type=float, default=24.0)
    parser.add_argument("--max-duration-seconds", type=float, default=15.0)
    parser.add_argument("--scale-to-length", type=int, default=640)
    parser.add_argument("--first-frame-prompt", default=FIRST_FRAME_PROMPT)
    parser.add_argument("--first-frame-negative", default=FIRST_FRAME_NEGATIVE)
    parser.add_argument("--video-prompt", default=VIDEO_PROMPT)
    parser.add_argument("--video-negative", default=VIDEO_NEGATIVE)
    parser.add_argument("--seed-timeout-seconds", type=int, default=1200)
    parser.add_argument("--video-timeout-seconds", type=int, default=3600)
    args = parser.parse_args()

    run_id = args.run_id or f"shangk_full_pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.environ["COMFYUI_RUNTIME_BASE_URL"] = args.base_url
    os.environ["COMFYUI_VIDEO_GPU_ENDPOINTS"] = f"default|{args.base_url}|0"

    from app.comfyui_runtime.service import ComfyUIRuntimeService

    args.report_dir.mkdir(parents=True, exist_ok=True)
    (SHANGK_OUTPUT / "首图生成").mkdir(parents=True, exist_ok=True)
    (SHANGK_OUTPUT / "视频生成").mkdir(parents=True, exist_ok=True)
    SHANGK_INPUT.mkdir(parents=True, exist_ok=True)

    scene_path = _latest_file(args.scene_dir, {".png", ".jpg", ".jpeg", ".webp"})
    reference_video = _latest_file(args.reference_dir, {".mp4", ".mov", ".mkv", ".webm"})
    reference_info = _ffprobe(reference_video)
    reference_duration = _duration_seconds(reference_info) or args.max_duration_seconds
    duration = min(reference_duration, args.max_duration_seconds)
    frames = max(1, int(math.ceil(duration * args.fps)))

    audio_path = SHANGK_INPUT / "shangk_reference_audio.wav"
    _extract_audio(reference_video, audio_path, duration_seconds=duration)

    scene_name = _input_relative_name(scene_path)
    audio_name = _input_relative_name(audio_path)
    object_info = _get_json(f"{args.base_url.rstrip('/')}/object_info")
    materializer = ComfyUIWorkflowMaterializer()
    service = ComfyUIRuntimeService()

    seed_workflow = _workflow_from_rag(QWEN_EDIT_WORKFLOW_NAME)
    if not seed_workflow:
        raise RuntimeError(f"Workflow not found in RAG documents: {QWEN_EDIT_WORKFLOW_NAME}")

    seed_result = materializer.materialize_api_prompt(
        source_workflow_path=seed_workflow["workflow_path"],
        parameter_plan={
            "positive_prompt": args.first_frame_prompt,
            "negative_prompt": args.first_frame_negative,
        },
        stage_key="shangk_first_frame",
        run_id=run_id,
        input_assets={"scene_image_name": scene_name},
        node_overrides={
            "3": {"steps": 4, "cfg": 1, "sampler_name": "euler", "scheduler": "simple", "denoise": 1},
            "60": {"filename_prefix": "商k/首图生成/shangk_first_frame"},
            "76": {"prompt": args.first_frame_prompt},
            "77": {"prompt": args.first_frame_negative},
            "78": {"image": scene_name},
        },
        output_prefix="商k/首图生成/shangk_first_frame",
        object_info=object_info,
    )
    if not seed_result.prompt_ready:
        raise RuntimeError(f"Seed prompt preflight failed: {seed_result.missing_node_types} {seed_result.unresolved_inputs[:5]}")

    seed_prompt = _load_json(seed_result.api_prompt_path)
    seed_workflow_payload = _load_json(seed_result.materialization.materialized_workflow_path)
    seed_submit = service.submit_prompt_job(
        prompt=seed_prompt,
        workflow=seed_workflow_payload,
        client_id=f"aiops-{run_id}-seed",
        workspace_id="local-runtime",
        media_type="image",
        metadata={"purpose": "shangk_qwen_first_frame", "run_id": run_id},
    )
    seed_history = _poll_history(
        service=service,
        prompt_id=seed_submit.prompt_id,
        base_url=seed_submit.base_url,
        timeout_seconds=args.seed_timeout_seconds,
    ) if seed_submit.success and seed_submit.prompt_id else {}
    seed_outputs = _history_outputs(seed_history, seed_submit.prompt_id)
    seed_files = _resolve_output_files(seed_outputs)
    seed_image = _first_existing(seed_files, {".png", ".jpg", ".jpeg", ".webp"})
    if not seed_image:
        raise RuntimeError(f"Seed generation did not produce an image: {seed_submit.error or seed_submit.node_errors}")

    approved_seed_input = SHANGK_INPUT / "shangk_approved_first_frame.png"
    shutil.copy2(seed_image, approved_seed_input)
    approved_seed_name = _input_relative_name(approved_seed_input)

    video_workflow = _selected_digital_human_workflow(args.agent_output)
    video_result = materializer.materialize_api_prompt(
        source_workflow_path=video_workflow["workflow_path"],
        parameter_plan={
            "positive_prompt": args.video_prompt,
            "negative_prompt": args.video_negative,
            "fps": args.fps,
            "frames": frames,
        },
        stage_key="shangk_video",
        run_id=run_id,
        input_assets={
            "approved_keyframe_name": approved_seed_name,
            "scene_image_name": approved_seed_name,
            "voice_audio_name": audio_name,
        },
        node_overrides={
            "319": {"value": args.scale_to_length},
            "320": {"value": frames},
            "122": {"model": WAN_MODEL},
            "120": {"model": INFINITETALK_MODEL},
            "131": {
                "filename_prefix": "商k/视频生成/shangk_final_video",
                "frame_rate": args.fps,
                "trim_to_audio": False,
            },
        },
        output_prefix="商k/视频生成/shangk_final_video",
        object_info=object_info,
    )
    if not video_result.prompt_ready:
        raise RuntimeError(f"Video prompt preflight failed: {video_result.missing_node_types} {video_result.unresolved_inputs[:5]}")

    video_prompt = _load_json(video_result.api_prompt_path)
    video_workflow_payload = _load_json(video_result.materialization.materialized_workflow_path)
    video_submit = service.submit_prompt_job(
        prompt=video_prompt,
        workflow=video_workflow_payload,
        client_id=f"aiops-{run_id}-video",
        workspace_id="local-runtime",
        media_type="video",
        resource_profile="standard",
        width=368,
        height=640,
        frames=frames,
        fps=args.fps,
        duration_seconds=duration,
        metadata={"purpose": "shangk_first_frame_to_video", "run_id": run_id},
    )
    video_history = _poll_history(
        service=service,
        prompt_id=video_submit.prompt_id,
        base_url=video_submit.base_url,
        timeout_seconds=args.video_timeout_seconds,
    ) if video_submit.success and video_submit.prompt_id else {}
    video_outputs = _history_outputs(video_history, video_submit.prompt_id)
    video_files = _resolve_output_files(video_outputs)
    video_path = _first_existing(video_files, {".mp4", ".mov", ".webm", ".mkv"})
    if not video_path:
        raise RuntimeError(f"Video generation did not produce a video: {video_submit.error or video_submit.node_errors}")

    video_probe = _ffprobe(video_path)
    contact_sheet = args.report_dir / f"{run_id}_contact.jpg"
    _contact_sheet(video_path, contact_sheet)

    report = {
        "status": "success",
        "run_id": run_id,
        "base_url": args.base_url,
        "scene_path": str(scene_path),
        "reference_video_path": str(reference_video),
        "reference_video_info": reference_info,
        "audio_path": str(audio_path),
        "duration_seconds_used": duration,
        "fps": args.fps,
        "frames_requested": frames,
        "first_frame_prompt": args.first_frame_prompt,
        "first_frame_negative": args.first_frame_negative,
        "video_prompt": args.video_prompt,
        "video_negative": args.video_negative,
        "first_frame": {
            "workflow": seed_workflow,
            "prompt_id": seed_submit.prompt_id,
            "materialized_workflow_path": seed_result.materialization.materialized_workflow_path,
            "api_prompt_path": seed_result.api_prompt_path,
            "output_image": str(seed_image),
            "registered_input_image": str(approved_seed_input),
            "output_files": seed_files,
            "submit": seed_submit.model_dump(mode="json"),
        },
        "video": {
            "workflow": video_workflow,
            "prompt_id": video_submit.prompt_id,
            "materialized_workflow_path": video_result.materialization.materialized_workflow_path,
            "api_prompt_path": video_result.api_prompt_path,
            "output_video": str(video_path),
            "output_files": video_files,
            "probe": video_probe,
            "submit": video_submit.model_dump(mode="json"),
        },
        "contact_sheet": str(contact_sheet),
        "quality_note": (
            "Full ShangK smoke-to-delivery pipeline: reference audio extracted, scene replaced by selected scene image, "
            "Qwen first frame generated, and InfiniteTalk video rendered to the requested output folder."
        ),
    }
    report_path = args.report_dir / f"{run_id}_report.json"
    history_seed_path = args.report_dir / f"{run_id}_seed_history.json"
    history_video_path = args.report_dir / f"{run_id}_video_history.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    history_seed_path.write_text(json.dumps(seed_history, ensure_ascii=False, indent=2), encoding="utf-8")
    history_video_path.write_text(json.dumps(video_history, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({
        "status": "success",
        "run_id": run_id,
        "first_frame": str(seed_image),
        "registered_first_frame": str(approved_seed_input),
        "video": str(video_path),
        "contact_sheet": str(contact_sheet),
        "report": str(report_path),
    }, ensure_ascii=False, indent=2))


def _latest_file(root: Path, suffixes: set[str]) -> Path:
    if not root.exists():
        raise FileNotFoundError(f"Directory not found: {root}")
    files = [path for path in root.rglob("*") if path.is_file() and path.suffix.lower() in suffixes]
    if not files:
        raise FileNotFoundError(f"No files with suffix {sorted(suffixes)} under {root}")
    return sorted(files, key=lambda path: path.stat().st_mtime, reverse=True)[0]


def _input_relative_name(path: Path) -> str:
    return path.resolve().relative_to(COMFY_INPUT.resolve()).as_posix()


def _get_json(url: str) -> Any:
    request = Request(url, headers={"Accept": "application/json"}, method="GET")
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


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
                "workflow_id": item.get("source_id"),
                "workflow_name": metadata.get("workflow_name"),
                "category": metadata.get("category"),
                "capabilities": metadata.get("capabilities") or [],
                "workflow_path": metadata.get("workflow_path"),
                "workflow_path_exists": Path(str(metadata.get("workflow_path") or "")).exists(),
            }
    return None


def _selected_digital_human_workflow(agent_output_path: Path) -> dict[str, Any]:
    agent_output = _load_json(agent_output_path)
    selected = (
        agent_output.get("execution_package", {})
        .get("workflow_stages", {})
        .get("digital_human_i2v", {})
        .get("selected", [])
    )
    if not selected:
        raise RuntimeError("No digital_human_i2v workflow selected in agent output.")
    return dict(selected[0])


def _extract_audio(video_path: Path, output_wav: Path, *, duration_seconds: float) -> None:
    output_wav.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(video_path),
        "-t",
        f"{duration_seconds:.3f}",
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        str(output_wav),
    ]
    subprocess.run(command, check=True)


def _ffprobe(path: Path) -> dict[str, Any]:
    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "stream=index,codec_type,codec_name,width,height,avg_frame_rate,duration,nb_frames:format=duration,size",
        "-of",
        "json",
        str(path),
    ]
    result = subprocess.run(command, check=True, capture_output=True, text=True, encoding="utf-8")
    return json.loads(result.stdout)


def _duration_seconds(probe: dict[str, Any]) -> float | None:
    duration = (probe.get("format") or {}).get("duration")
    try:
        return float(duration)
    except (TypeError, ValueError):
        return None


def _poll_history(
    *,
    service: Any,
    prompt_id: str | None,
    base_url: str,
    timeout_seconds: int,
    poll_interval_seconds: int = 10,
) -> dict[str, Any]:
    if not prompt_id:
        return {}
    deadline = time.monotonic() + timeout_seconds
    last_payload: dict[str, Any] = {}
    while time.monotonic() < deadline:
        history = service.prompt_history(workspace_id="local-runtime", prompt_id=prompt_id, base_url=base_url)
        last_payload = history.response_payload
        item = last_payload.get(prompt_id, {}) if isinstance(last_payload, dict) else {}
        outputs = item.get("outputs") if isinstance(item, dict) else None
        status = item.get("status") if isinstance(item, dict) else None
        if outputs or (isinstance(status, dict) and status.get("completed")):
            return last_payload
        time.sleep(max(1, poll_interval_seconds))
    return last_payload


def _history_outputs(history: dict[str, Any], prompt_id: str | None) -> dict[str, Any]:
    if not prompt_id or not isinstance(history, dict):
        return {}
    item = history.get(prompt_id)
    if not isinstance(item, dict):
        return {}
    outputs = item.get("outputs")
    return outputs if isinstance(outputs, dict) else {}


def _resolve_output_files(outputs: dict[str, Any]) -> list[dict[str, Any]]:
    files: list[dict[str, Any]] = []
    for node_id, payload in (outputs or {}).items():
        if not isinstance(payload, dict):
            continue
        for key, values in payload.items():
            if not isinstance(values, list):
                continue
            for value in values:
                if not isinstance(value, dict) or not value.get("filename"):
                    continue
                explicit = value.get("fullpath")
                path = Path(str(explicit)) if explicit else COMFY_OUTPUT / str(value.get("subfolder") or "") / str(value["filename"])
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


def _first_existing(files: list[dict[str, Any]], suffixes: set[str]) -> Path | None:
    for item in files:
        path = Path(str(item.get("path") or ""))
        if path.exists() and path.suffix.lower() in suffixes:
            return path
    return None


def _contact_sheet(video_path: Path, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(video_path),
            "-vf",
            "fps=1,scale=240:-1,tile=6x1",
            "-frames:v",
            "1",
            str(output_path),
        ],
        check=True,
    )


if __name__ == "__main__":
    main()
