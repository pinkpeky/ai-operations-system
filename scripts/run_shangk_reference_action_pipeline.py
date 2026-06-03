"""Run ShangK reference-action replication through ComfyUI.

This route is for the original Douyin-style requirement:
scene image -> fictional standing singer first frame -> reference-video action transfer.
It does not mutate imported ComfyUI source workflows.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


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
    _first_existing,
    _get_json,
    _history_outputs,
    _latest_file,
    _load_json,
    _poll_history,
    _resolve_output_files,
)


REPORT_DIR = PROJECT_ROOT / "deployment" / "comfyui" / "commercial_ktv_workflow" / "shangk_reference_action"
RAG_DOCS = PROJECT_ROOT / "deployment" / "comfyui" / "commercial_ktv_workflow" / "cu130_runtime_workflow_rag_documents.jsonl"

DUAL_QWEN_EDIT_WORKFLOW_SOURCE_ID = "comfyui_cu130_runtime_db72516e6fee"
ACTION_WORKFLOW_SOURCE_ID = "comfyui_cu130_runtime_9e91bb89ecd3"

ROOT_SCENE_NAME = "shangk_scene_source.png"
ROOT_REFERENCE_VIDEO_NAME = "shangk_reference_video.mp4"
ROOT_POSE_REFERENCE_NAME = "shangk_pose_reference_frame.jpg"
ROOT_FIRST_FRAME_NAME = "shangk_standing_mic_first_frame.png"
ROOT_CHARACTER_SCENE_VIDEO_NAME = "shangk_character_scene_video.mp4"

FIRST_FRAME_PREFIX = "商k/首图生成/shangk_standing_mic_first_frame"
ACTION_VIDEO_PREFIX = "商k/视频生成/shangk_action_transfer"

FIRST_FRAME_PROMPT = (
    "Use image 1 strictly as the target ShangK private-room background. "
    "Use image 2 only as a pose and performance reference: standing female singer, wireless microphone held near mouth, "
    "singing, light dance posture, confident camera-facing stage presence. Create one new fictional adult AI female singer, "
    "not the real person from image 2, clearly beautiful and normal, full body visible, standing on the open floor in image 1, "
    "sparkling silver-black short stage dress, high heels, natural face, normal hands and fingers, normal body proportions, "
    "premium Douyin commercial photography, vertical 9:16. Preserve image 1 room layout, neon blue lighting, sofa/table/screen "
    "position and glossy reflections, but do not make her sit and do not place her behind the table."
)
FIRST_FRAME_NEGATIVE = (
    "seated, sitting, leaning on sofa, table blocking body, no microphone, hidden hands, cropped feet, deformed face, "
    "asymmetrical eyes, bad hands, extra fingers, missing fingers, extra limbs, broken arms, broken legs, duplicate person, "
    "childlike, old face, male, real-person cutout, pasted portrait, watermark, subtitles, QR code, Douyin UI, low quality, blur"
)

ACTION_PROMPT = (
    "Use the reference video only for pose, body motion, performance rhythm, camera timing, and audio timing. "
    "Replace the person with the fictional adult AI female singer from the reference image, preserving her black sequined dress, "
    "natural face, body proportions, and microphone. Keep the generated ShangK scene background from the target scene image/video, "
    "not the reference video's room. Preserve the standing singer performance: holding a wireless microphone, singing, dancing lightly, "
    "body sway, arm movement, face orientation, camera awareness, and vertical KTV stage energy. The result should be a usable "
    "short-video ad segment in the selected ShangK room."
)
ACTION_NEGATIVE = (
    "seated, sitting, static talking head, no microphone, microphone missing, distorted face, bad hands, extra fingers, "
    "extra limbs, broken body, duplicate person, heavy flicker, subtitles, watermark, unreadable text, scene jump, "
    "background melting, copied reference video background, silver dress from reference video, low quality, blurry face, wrong gender, childlike"
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8188")
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--report-dir", type=Path, default=REPORT_DIR)
    parser.add_argument("--scene-dir", type=Path, default=SHANGK_INPUT / "场景")
    parser.add_argument("--reference-dir", type=Path, default=SHANGK_INPUT / "视频参考")
    parser.add_argument("--generation-width", type=int, default=480)
    parser.add_argument("--generation-height", type=int, default=832)
    parser.add_argument("--generation-fps", type=float, default=16.0)
    parser.add_argument("--frame-load-cap", type=int, default=0, help="0 means load the full reference video at generation fps.")
    parser.add_argument("--sampler-steps", type=int, default=6)
    parser.add_argument("--sampler-seed", type=int, default=42)
    parser.add_argument("--seed-timeout-seconds", type=int, default=1200)
    parser.add_argument("--video-timeout-seconds", type=int, default=14400)
    parser.add_argument("--reuse-first-frame", action="store_true")
    parser.add_argument("--skip-video", action="store_true")
    args = parser.parse_args()

    run_id = args.run_id or f"shangk_reference_action_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.environ["COMFYUI_RUNTIME_BASE_URL"] = args.base_url
    os.environ["COMFYUI_VIDEO_GPU_ENDPOINTS"] = f"default|{args.base_url}|0"

    args.report_dir.mkdir(parents=True, exist_ok=True)
    (COMFY_OUTPUT / "商k" / "首图生成").mkdir(parents=True, exist_ok=True)
    (COMFY_OUTPUT / "商k" / "视频生成").mkdir(parents=True, exist_ok=True)

    scene_path = _latest_file(args.scene_dir, {".png", ".jpg", ".jpeg", ".webp"})
    reference_video = _latest_file(args.reference_dir, {".mp4", ".mov", ".mkv", ".webm"})
    scene_input = _copy_to_comfy_input(scene_path, ROOT_SCENE_NAME)
    reference_input = _copy_to_comfy_input(reference_video, ROOT_REFERENCE_VIDEO_NAME)
    pose_reference_input = COMFY_INPUT / ROOT_POSE_REFERENCE_NAME
    _extract_pose_reference_frame(reference_input, pose_reference_input)

    reference_probe = _ffprobe(reference_input)
    reference_duration = _duration_seconds(reference_probe)
    source_fps = _video_fps(reference_probe) or 30.0
    materializer = ComfyUIWorkflowMaterializer()
    service = ComfyUIRuntimeService()

    first_frame_input = COMFY_INPUT / ROOT_FIRST_FRAME_NAME
    first_frame_report: dict[str, Any]
    if args.reuse_first_frame and first_frame_input.exists():
        seed_image = first_frame_input
        first_frame_report = {"reused": True, "registered_input_image": str(first_frame_input)}
    else:
        seed_image, first_frame_report = _run_first_frame_stage(
            materializer=materializer,
            service=service,
            base_url=args.base_url,
            run_id=run_id,
            scene_name=scene_input.name,
            pose_reference_name=pose_reference_input.name,
            timeout_seconds=args.seed_timeout_seconds,
        )
        shutil.copy2(seed_image, first_frame_input)
        shutil.copy2(seed_image, COMFY_INPUT / "商k" / ROOT_FIRST_FRAME_NAME)
        first_frame_report["registered_input_image"] = str(first_frame_input)

    character_scene_video = COMFY_INPUT / ROOT_CHARACTER_SCENE_VIDEO_NAME
    _make_scene_background_video(
        scene_image=first_frame_input,
        output_path=character_scene_video,
        width=args.generation_width,
        height=args.generation_height,
        fps=args.generation_fps,
        duration_seconds=reference_duration,
    )

    video_report: dict[str, Any] | None = None
    delivery_video: Path | None = None
    if not args.skip_video:
        video_path, video_report = _run_action_stage(
            materializer=materializer,
            service=service,
            base_url=args.base_url,
            run_id=run_id,
            reference_video_name=reference_input.name,
            first_frame_name=first_frame_input.name,
            background_video_name=character_scene_video.name,
            width=args.generation_width,
            height=args.generation_height,
            generation_fps=args.generation_fps,
            frame_load_cap=args.frame_load_cap,
            duration_seconds=reference_duration,
            steps=args.sampler_steps,
            seed=args.sampler_seed,
            timeout_seconds=args.video_timeout_seconds,
        )
        delivery_video = COMFY_OUTPUT / "商k" / "视频生成" / f"{run_id}_delivery_1080x1920.mp4"
        _make_delivery_video(
            generated_video=video_path,
            reference_video=reference_input,
            output_path=delivery_video,
            source_fps=source_fps,
            duration_seconds=reference_duration,
        )
        video_report["delivery_video"] = str(delivery_video)
        video_report["delivery_probe"] = _ffprobe(delivery_video)
        video_report["delivery_contact_sheet"] = str(args.report_dir / f"{run_id}_delivery_contact.jpg")
        _contact_sheet(delivery_video, Path(video_report["delivery_contact_sheet"]))

    report = {
        "status": "success",
        "run_id": run_id,
        "base_url": args.base_url,
        "scene_path": str(scene_path),
        "scene_input": str(scene_input),
        "reference_video_path": str(reference_video),
        "reference_video_input": str(reference_input),
        "pose_reference_input": str(pose_reference_input),
        "character_scene_video_input": str(character_scene_video),
        "reference_probe": reference_probe,
        "reference_duration_seconds": reference_duration,
        "source_fps": source_fps,
        "generation_width": args.generation_width,
        "generation_height": args.generation_height,
        "generation_fps": args.generation_fps,
        "frame_load_cap": args.frame_load_cap,
        "first_frame_prompt": FIRST_FRAME_PROMPT,
        "first_frame_negative": FIRST_FRAME_NEGATIVE,
        "action_prompt": ACTION_PROMPT,
        "action_negative": ACTION_NEGATIVE,
        "first_frame": first_frame_report,
        "video": video_report,
    }
    report_path = args.report_dir / f"{run_id}_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"report": str(report_path), "first_frame": str(first_frame_input), "delivery_video": str(delivery_video) if delivery_video else None}, ensure_ascii=False, indent=2))


def _run_first_frame_stage(
    *,
    materializer: ComfyUIWorkflowMaterializer,
    service: ComfyUIRuntimeService,
    base_url: str,
    run_id: str,
    scene_name: str,
    pose_reference_name: str,
    timeout_seconds: int,
) -> tuple[Path, dict[str, Any]]:
    workflow = _workflow_from_source_id(DUAL_QWEN_EDIT_WORKFLOW_SOURCE_ID)
    object_info = _get_json(f"{base_url.rstrip('/')}/object_info")
    result = materializer.materialize(
        source_workflow_path=workflow["workflow_path"],
        parameter_plan={"positive_prompt": FIRST_FRAME_PROMPT, "negative_prompt": FIRST_FRAME_NEGATIVE},
        stage_key="shangk_standing_mic_first_frame",
        run_id=run_id,
        input_assets={"scene_image_name": scene_name},
        node_overrides={
            "8": {"image": scene_name},
            "7": {"image": pose_reference_name},
            "3": {"prompt": FIRST_FRAME_PROMPT},
            "4": {"prompt": FIRST_FRAME_NEGATIVE},
            "2": {"steps": 6, "cfg": 1, "sampler_name": "sa_solver", "scheduler": "beta", "denoise": 1},
            "9": {"width": 720, "height": 1280, "batch_size": 1},
            "15": {"filename_prefix": FIRST_FRAME_PREFIX},
        },
        output_prefix=FIRST_FRAME_PREFIX,
    )
    materialized_path = Path(result.materialized_workflow_path)
    workflow_payload = _load_json(materialized_path)
    for node in workflow_payload.get("nodes", []) or []:
        if str(node.get("id")) == "15":
            node["mode"] = 0
    materialized_path.write_text(json.dumps(workflow_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    prompt = materializer.to_api_prompt(workflow_payload, object_info=object_info)
    preflight = materializer.preflight_api_prompt(prompt, object_info=object_info)
    if not preflight["prompt_ready"]:
        raise RuntimeError(f"First-frame preflight failed: {preflight['missing_node_types']} {preflight['unresolved_inputs'][:8]}")
    api_prompt_path = materialized_path.with_suffix(".api_prompt.json")
    api_prompt_path.write_text(json.dumps(prompt, ensure_ascii=False, indent=2), encoding="utf-8")
    submit = service.submit_prompt_job(
        prompt=prompt,
        workflow=workflow_payload,
        client_id=f"aiops-{run_id}-first-frame",
        workspace_id="local-runtime",
        media_type="image",
        metadata={"purpose": "shangk_reference_action_first_frame", "run_id": run_id},
    )
    history = _poll_history(
        service=service,
        prompt_id=submit.prompt_id,
        base_url=submit.base_url,
        timeout_seconds=timeout_seconds,
    ) if submit.success and submit.prompt_id else {}
    outputs = _history_outputs(history, submit.prompt_id)
    files = _resolve_output_files(outputs)
    image = _first_existing(files, {".png", ".jpg", ".jpeg", ".webp"})
    if image is None:
        raise RuntimeError(f"First-frame generation produced no image: {submit.error or submit.node_errors}")
    return image, {
        "workflow": workflow,
        "prompt_id": submit.prompt_id,
        "materialized_workflow_path": str(materialized_path),
        "api_prompt_path": str(api_prompt_path),
        "output_image": str(image),
        "output_files": files,
        "submit": submit.model_dump(mode="json"),
    }


def _run_action_stage(
    *,
    materializer: ComfyUIWorkflowMaterializer,
    service: ComfyUIRuntimeService,
    base_url: str,
    run_id: str,
    reference_video_name: str,
    first_frame_name: str,
    background_video_name: str,
    width: int,
    height: int,
    generation_fps: float,
    frame_load_cap: int,
    duration_seconds: float | None,
    steps: int,
    seed: int,
    timeout_seconds: int,
) -> tuple[Path, dict[str, Any]]:
    workflow = _workflow_from_source_id(ACTION_WORKFLOW_SOURCE_ID)
    object_info = _get_json(f"{base_url.rstrip('/')}/object_info")
    result = materializer.materialize_api_prompt(
        source_workflow_path=workflow["workflow_path"],
        parameter_plan={
            "positive_prompt": ACTION_PROMPT,
            "negative_prompt": ACTION_NEGATIVE,
            "width": width,
            "height": height,
            "fps": generation_fps,
        },
        stage_key="shangk_reference_action_video",
        run_id=run_id,
        input_assets={"approved_keyframe_name": first_frame_name, "reference_video_name": reference_video_name},
        node_overrides={
            "57": {"image": first_frame_name},
            "63": {
                "video": reference_video_name,
                "force_rate": generation_fps,
                "custom_width": width,
                "custom_height": height,
                "frame_load_cap": frame_load_cap,
                "skip_first_frames": 0,
                "select_every_nth": 1,
                "format": "AnimateDiff",
            },
            "65": {"positive_prompt": ACTION_PROMPT, "negative_prompt": ACTION_NEGATIVE},
            "150": {"value": width},
            "151": {"value": height},
            "205": {"draw_head": True},
            "27": {"steps": steps, "cfg": 1, "shift": 5, "seed": seed, "force_offload": True, "scheduler": "euler"},
            "30": {
                "frame_rate": generation_fps,
                "filename_prefix": ACTION_VIDEO_PREFIX,
                "format": "video/h264-mp4",
                "save_output": True,
                "trim_to_audio": False,
            },
        },
        output_prefix=ACTION_VIDEO_PREFIX,
        object_info=object_info,
    )
    if not result.prompt_ready:
        raise RuntimeError(f"Action preflight failed: {result.missing_node_types} {result.unresolved_inputs[:8]}")

    prompt_path = Path(result.api_prompt_path)
    prompt = _load_json(prompt_path)
    if "27" in prompt:
        prompt["27"].setdefault("inputs", {}).pop("context_options", None)
    prompt["900"] = {
        "class_type": "VHS_LoadVideo",
        "inputs": {
            "video": background_video_name,
            "force_rate": generation_fps,
            "custom_width": width,
            "custom_height": height,
            "frame_load_cap": frame_load_cap,
            "skip_first_frames": 0,
            "select_every_nth": 1,
            "format": "AnimateDiff",
        },
    }
    if "62" in prompt:
        prompt["62"].setdefault("inputs", {})["bg_images"] = ["900", 0]
    if "30" in prompt and "42" in prompt:
        prompt["30"]["inputs"]["images"] = ["42", 0]
    prompt = _prune_prompt_to_outputs(prompt, output_node_ids={"30"})
    patched_preflight = materializer.preflight_api_prompt(prompt, object_info=object_info)
    if not patched_preflight["prompt_ready"]:
        raise RuntimeError(
            f"Patched action preflight failed: {patched_preflight['missing_node_types']} "
            f"{patched_preflight['unresolved_inputs'][:8]}"
        )
    prompt_path.write_text(json.dumps(prompt, ensure_ascii=False, indent=2), encoding="utf-8")

    workflow_payload = _load_json(result.materialization.materialized_workflow_path)
    submit = service.submit_prompt_job(
        prompt=prompt,
        workflow=workflow_payload,
        client_id=f"aiops-{run_id}-action",
        workspace_id="local-runtime",
        media_type="video",
        resource_profile="standard",
        width=width,
        height=height,
        frames=_estimated_generation_frames(frame_load_cap=frame_load_cap, duration_seconds=duration_seconds, fps=generation_fps),
        fps=generation_fps,
        duration_seconds=duration_seconds,
        metadata={"purpose": "shangk_reference_action_transfer", "run_id": run_id},
    )
    history = _poll_history(
        service=service,
        prompt_id=submit.prompt_id,
        base_url=submit.base_url,
        timeout_seconds=timeout_seconds,
    ) if submit.success and submit.prompt_id else {}
    outputs = _history_outputs(history, submit.prompt_id)
    status = _history_status(history, submit.prompt_id)
    if str(status.get("status_str") or "").lower() == "error":
        raise RuntimeError(f"Action generation failed: {json.dumps(status, ensure_ascii=False)[:4000]}")
    files = _resolve_output_files(outputs)
    video = _first_existing(files, {".mp4", ".mov", ".webm", ".mkv"})
    if video is None:
        raise RuntimeError(f"Action generation produced no video: {submit.error or submit.node_errors}")
    contact_sheet = REPORT_DIR / f"{run_id}_generated_contact.jpg"
    _contact_sheet(video, contact_sheet)
    return video, {
        "workflow": workflow,
        "prompt_id": submit.prompt_id,
        "materialized_workflow_path": result.materialization.materialized_workflow_path,
        "api_prompt_path": str(prompt_path),
        "api_prompt_patches": {
            "node_27_removed": ["context_options"],
            "node_30_images": ["42", 0],
            "node_62_bg_images": ["900", 0],
            "added_node_900": "VHS_LoadVideo static target scene background",
            "pruned_output_nodes": True,
        },
        "output_video": str(video),
        "output_probe": _ffprobe(video),
        "output_contact_sheet": str(contact_sheet),
        "output_files": files,
        "submit": submit.model_dump(mode="json"),
    }


def _workflow_from_source_id(source_id: str) -> dict[str, Any]:
    for line in RAG_DOCS.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        if item.get("source_id") == source_id:
            metadata = dict(item.get("metadata") or {})
            return {
                "workflow_id": item.get("source_id"),
                "workflow_name": metadata.get("workflow_name"),
                "category": metadata.get("category"),
                "capabilities": metadata.get("capabilities") or [],
                "workflow_path": metadata.get("workflow_path"),
                "workflow_path_exists": Path(str(metadata.get("workflow_path") or "")).exists(),
            }
    raise RuntimeError(f"Workflow source_id not found: {source_id}")


def _copy_to_comfy_input(source: Path, name: str) -> Path:
    target = COMFY_INPUT / name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return target


def _extract_pose_reference_frame(video_path: Path, output_path: Path, *, timestamp_seconds: float = 3.0) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-ss",
            f"{timestamp_seconds:.3f}",
            "-i",
            str(video_path),
            "-frames:v",
            "1",
            str(output_path),
        ],
        check=True,
    )


def _make_scene_background_video(
    *,
    scene_image: Path,
    output_path: Path,
    width: int,
    height: int,
    fps: float,
    duration_seconds: float | None,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    duration = max(1.0, float(duration_seconds or 1.0))
    vf = (
        f"scale={width}:{height}:force_original_aspect_ratio=increase,"
        f"crop={width}:{height},fps={fps},setsar=1"
    )
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-loop",
            "1",
            "-i",
            str(scene_image),
            "-t",
            f"{duration:.3f}",
            "-vf",
            vf,
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            str(output_path),
        ],
        check=True,
    )


def _video_fps(probe: dict[str, Any]) -> float | None:
    for stream in probe.get("streams", []) or []:
        if stream.get("codec_type") != "video":
            continue
        value = stream.get("avg_frame_rate") or stream.get("r_frame_rate")
        if not value or value == "0/0":
            return None
        if "/" in str(value):
            numerator, denominator = str(value).split("/", 1)
            try:
                den = float(denominator)
                return float(numerator) / den if den else None
            except ValueError:
                return None
        try:
            return float(value)
        except ValueError:
            return None
    return None


def _estimated_generation_frames(*, frame_load_cap: int, duration_seconds: float | None, fps: float) -> int:
    if frame_load_cap > 0:
        return frame_load_cap
    if duration_seconds and duration_seconds > 0:
        return max(1, int(math.ceil(duration_seconds * fps)))
    return 96


def _prune_prompt_to_outputs(prompt: dict[str, Any], *, output_node_ids: set[str]) -> dict[str, Any]:
    keep: set[str] = set()

    def visit(node_id: str) -> None:
        if node_id in keep or node_id not in prompt:
            return
        keep.add(node_id)
        inputs = prompt.get(node_id, {}).get("inputs", {})
        if not isinstance(inputs, dict):
            return
        for value in inputs.values():
            if isinstance(value, list) and len(value) == 2 and str(value[0]) in prompt:
                visit(str(value[0]))

    for output_node_id in output_node_ids:
        visit(str(output_node_id))
    return {node_id: node for node_id, node in prompt.items() if node_id in keep}


def _history_status(history: dict[str, Any], prompt_id: str | None) -> dict[str, Any]:
    if not prompt_id or not isinstance(history, dict):
        return {}
    item = history.get(prompt_id)
    if not isinstance(item, dict):
        return {}
    status = item.get("status")
    return dict(status) if isinstance(status, dict) else {}


def _make_delivery_video(
    *,
    generated_video: Path,
    reference_video: Path,
    output_path: Path,
    source_fps: float,
    duration_seconds: float | None,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    vf = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps={fps},setsar=1".format(
        fps=max(1, round(source_fps))
    )
    command = [
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
    ]
    if duration_seconds:
        command.extend(["-t", f"{duration_seconds:.3f}"])
    command.append(str(output_path))
    subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
