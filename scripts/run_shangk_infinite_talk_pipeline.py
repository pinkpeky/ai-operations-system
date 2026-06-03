"""Run the validated ShangK first-frame + InfiniteTalk video workflow."""

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
from urllib.error import HTTPError
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
TEMPLATE_DIR = PROJECT_ROOT / "deployment" / "comfyui" / "commercial_ktv_workflow" / "shangk_infinite_talk"
DEFAULT_PROMPT_TEMPLATE = TEMPLATE_DIR / "user_good_sample.prompt.json"
DEFAULT_WORKFLOW_TEMPLATE = TEMPLATE_DIR / "user_good_sample.workflow.json"
DEFAULT_REPORT_DIR = TEMPLATE_DIR / "runs"
DEFAULT_PROMPT = "对着观众唱歌并摇摆身体跳舞"
DEFAULT_NEGATIVE = (
    "bright tones, overexposed, static, blurred details, subtitles, watermark, worst quality, low quality, "
    "ugly, incomplete, extra fingers, poorly drawn hands, poorly drawn faces, deformed, disfigured, "
    "misshapen limbs, fused fingers, still picture, messy background, three legs, many people in the background"
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8188")
    parser.add_argument("--prompt-template", type=Path, default=DEFAULT_PROMPT_TEMPLATE)
    parser.add_argument("--workflow-template", type=Path, default=DEFAULT_WORKFLOW_TEMPLATE)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--reference-video", type=Path, default=None)
    parser.add_argument("--reference-dir", type=Path, default=SHANGK_INPUT / "视频参考")
    parser.add_argument("--first-frame", type=Path, default=COMFY_INPUT / "shangk_standing_mic_first_frame.png")
    parser.add_argument("--audio", type=Path, default=None)
    parser.add_argument("--prompt", default=DEFAULT_PROMPT)
    parser.add_argument("--negative-prompt", default=DEFAULT_NEGATIVE)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--fps", type=float, default=16.0)
    parser.add_argument("--steps", type=int, default=4)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--shift", type=float, default=11.0)
    parser.add_argument("--scale-to-length", type=int, default=1280)
    parser.add_argument("--timeout-seconds", type=int, default=14400)
    args = parser.parse_args()

    run_id = args.run_id or f"shangk_infinite_talk_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.environ["COMFYUI_RUNTIME_BASE_URL"] = args.base_url
    os.environ["COMFYUI_VIDEO_GPU_ENDPOINTS"] = f"default|{args.base_url}|0"
    args.report_dir.mkdir(parents=True, exist_ok=True)
    (SHANGK_OUTPUT / "视频生成").mkdir(parents=True, exist_ok=True)
    COMFY_INPUT.mkdir(parents=True, exist_ok=True)

    first_frame_input = _prepare_first_frame(args.first_frame)
    audio_input, reference_video = _prepare_audio(args.audio, args.reference_video, args.reference_dir)
    prompt = _load_json(args.prompt_template)
    workflow = _load_json(args.workflow_template) if args.workflow_template.exists() else {}
    seed = args.seed if args.seed is not None else int(time.time_ns() % 1_000_000_000_000_000)

    _patch_prompt(
        prompt,
        first_frame_name=first_frame_input.name,
        audio_name=audio_input.name,
        prompt_text=args.prompt,
        negative_prompt=args.negative_prompt,
        run_id=run_id,
        fps=args.fps,
        steps=args.steps,
        seed=seed,
        shift=args.shift,
        scale_to_length=args.scale_to_length,
    )

    object_info = _get_json(f"{args.base_url.rstrip('/')}/object_info")
    preflight = ComfyUIWorkflowMaterializer().preflight_api_prompt(prompt, object_info=object_info)
    if not preflight["prompt_ready"]:
        raise RuntimeError(
            f"InfiniteTalk prompt preflight failed: {preflight['missing_node_types']} "
            f"{preflight['unresolved_inputs'][:8]}"
        )

    run_dir = args.report_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    prompt_path = run_dir / "prompt.json"
    workflow_path = run_dir / "workflow.json"
    prompt_path.write_text(json.dumps(prompt, ensure_ascii=False, indent=2), encoding="utf-8")
    workflow_path.write_text(json.dumps(workflow, ensure_ascii=False, indent=2), encoding="utf-8")

    submit = _submit_prompt(
        base_url=args.base_url,
        prompt=prompt,
        workflow=workflow,
        client_id=f"aiops-{run_id}-infinitetalk",
    )
    prompt_id = str(submit.get("prompt_id") or "")
    if not prompt_id:
        raise RuntimeError(f"InfiniteTalk submit failed: {json.dumps(submit, ensure_ascii=False)[:2000]}")

    history = _poll_history(base_url=args.base_url, prompt_id=prompt_id, timeout_seconds=args.timeout_seconds)
    outputs = _history_outputs(history, prompt_id)
    files = _resolve_output_files(outputs)
    raw_video = _first_existing(files, {".mp4", ".mov", ".webm", ".mkv"})
    if raw_video is None:
        raise RuntimeError(f"InfiniteTalk produced no video. prompt_id={prompt_id}")

    raw_named = SHANGK_OUTPUT / "视频生成" / f"{run_id}_raw.mp4"
    shutil.copy2(raw_video, raw_named)
    delivery_video = SHANGK_OUTPUT / "视频生成" / f"{run_id}_delivery_1080x1920.mp4"
    _make_delivery_video(raw_named, delivery_video)
    contact_sheet = run_dir / "contact.jpg"
    delivery_contact_sheet = run_dir / "delivery_contact.jpg"
    _contact_sheet(raw_named, contact_sheet)
    _contact_sheet(delivery_video, delivery_contact_sheet)

    report = {
        "status": "success",
        "run_id": run_id,
        "prompt_id": prompt_id,
        "base_url": args.base_url,
        "route": "first_frame_audio_to_video_infinite_talk",
        "first_frame_input": str(first_frame_input),
        "audio_input": str(audio_input),
        "reference_video": str(reference_video) if reference_video else None,
        "prompt": args.prompt,
        "negative_prompt": args.negative_prompt,
        "fps": args.fps,
        "steps": args.steps,
        "seed": seed,
        "shift": args.shift,
        "scale_to_length": args.scale_to_length,
        "prompt_template": str(args.prompt_template),
        "workflow_template": str(args.workflow_template),
        "materialized_prompt": str(prompt_path),
        "materialized_workflow": str(workflow_path),
        "raw_video": str(raw_named),
        "raw_probe": _ffprobe(raw_named),
        "delivery_video": str(delivery_video),
        "delivery_probe": _ffprobe(delivery_video),
        "contact_sheet": str(contact_sheet),
        "delivery_contact_sheet": str(delivery_contact_sheet),
        "history_status": _history_status(history, prompt_id),
        "output_files": [str(path) for path in files],
        "submit": submit,
    }
    report_path = run_dir / "report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"report": str(report_path), "raw_video": str(raw_named), "delivery_video": str(delivery_video)}, ensure_ascii=False, indent=2))


def _prepare_first_frame(path: Path) -> Path:
    candidates = [
        path,
        COMFY_INPUT / "商k" / "shangk_standing_mic_first_frame.png",
        COMFY_OUTPUT / "商k" / "首图生成" / "shangk_standing_mic_pose_guided_00001_.png",
    ]
    source = next((candidate for candidate in candidates if candidate.exists()), None)
    if source is None:
        raise FileNotFoundError(f"First frame not found. Checked: {[str(candidate) for candidate in candidates]}")
    target = COMFY_INPUT / "shangk_standing_mic_first_frame.png"
    if source.resolve() != target.resolve():
        shutil.copy2(source, target)
    return target


def _prepare_audio(audio: Path | None, reference_video: Path | None, reference_dir: Path) -> tuple[Path, Path | None]:
    target = COMFY_INPUT / "shangk_reference_audio.wav"
    if audio is not None:
        if not audio.exists():
            raise FileNotFoundError(f"Audio not found: {audio}")
        if audio.resolve() != target.resolve():
            shutil.copy2(audio, target)
        return target, reference_video

    selected_video = reference_video or _latest_file(reference_dir, {".mp4", ".mov", ".mkv", ".webm"})
    _extract_audio(selected_video, target)
    return target, selected_video


def _patch_prompt(
    prompt: dict[str, Any],
    *,
    first_frame_name: str,
    audio_name: str,
    prompt_text: str,
    negative_prompt: str,
    run_id: str,
    fps: float,
    steps: int,
    seed: int,
    shift: float,
    scale_to_length: int,
) -> None:
    prompt["284"]["inputs"]["image"] = first_frame_name
    prompt["125"]["inputs"]["audio"] = audio_name
    prompt["125"]["inputs"]["audioUI"] = f"/api/view?filename={audio_name}&type=input&subfolder="
    prompt["355"]["inputs"]["prompt"] = prompt_text
    prompt["317"]["inputs"]["negative_prompt"] = negative_prompt
    prompt["128"]["inputs"].update(
        {
            "steps": steps,
            "cfg": 1.0,
            "shift": shift,
            "seed": seed,
            "scheduler": "dpm++_sde",
            "denoise_strength": 1.0,
            "add_noise_to_samples": True,
        }
    )
    prompt["328"]["inputs"]["value"] = fps
    prompt["345"]["inputs"]["value"] = scale_to_length
    prompt["131"]["inputs"].update(
        {
            "filename_prefix": f"商k/视频生成/{run_id}",
            "format": "video/h264-mp4",
            "pix_fmt": "yuv420p",
            "crf": 19,
            "save_metadata": True,
            "trim_to_audio": False,
            "save_output": True,
        }
    )


def _submit_prompt(*, base_url: str, prompt: dict[str, Any], workflow: dict[str, Any], client_id: str) -> dict[str, Any]:
    payload: dict[str, Any] = {"prompt": prompt, "client_id": client_id}
    if workflow:
        payload["extra_data"] = {"extra_pnginfo": {"workflow": workflow}}
    request = Request(
        f"{base_url.rstrip('/')}/prompt",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError:
            parsed = {"text": body}
        return {"status_code": exc.code, "error": str(exc.reason), "response": parsed}


def _poll_history(*, base_url: str, prompt_id: str, timeout_seconds: int) -> dict[str, Any]:
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


def _history_outputs(history: dict[str, Any], prompt_id: str) -> dict[str, Any]:
    item = history.get(prompt_id) if isinstance(history, dict) else None
    if not isinstance(item, dict):
        return {}
    outputs = item.get("outputs")
    return outputs if isinstance(outputs, dict) else {}


def _history_status(history: dict[str, Any], prompt_id: str) -> dict[str, Any]:
    item = history.get(prompt_id) if isinstance(history, dict) else None
    if not isinstance(item, dict):
        return {}
    status = item.get("status")
    return status if isinstance(status, dict) else {}


def _resolve_output_files(outputs: dict[str, Any]) -> list[Path]:
    files: list[Path] = []
    for output in outputs.values():
        if not isinstance(output, dict):
            continue
        for key in ("images", "gifs", "videos"):
            for item in output.get(key, []) or []:
                if not isinstance(item, dict):
                    continue
                filename = str(item.get("filename") or "")
                if not filename:
                    continue
                subfolder = str(item.get("subfolder") or "")
                folder_type = str(item.get("type") or "output")
                root = COMFY_OUTPUT if folder_type == "output" else COMFY_INPUT
                files.append(root / subfolder / filename)
    return files


def _first_existing(files: list[Path], suffixes: set[str]) -> Path | None:
    for path in files:
        if path.suffix.lower() in suffixes and path.exists():
            return path
    return None


def _latest_file(directory: Path, suffixes: set[str]) -> Path:
    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")
    candidates = [path for path in directory.iterdir() if path.is_file() and path.suffix.lower() in suffixes]
    if not candidates:
        raise FileNotFoundError(f"No files with suffixes {sorted(suffixes)} under {directory}")
    return max(candidates, key=lambda path: path.stat().st_mtime)


def _extract_audio(video_path: Path, output_wav: Path) -> None:
    output_wav.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(video_path),
            "-vn",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-c:a",
            "pcm_s16le",
            str(output_wav),
        ],
        check=True,
    )


def _make_delivery_video(input_video: Path, output_video: Path) -> None:
    output_video.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(input_video),
            "-vf",
            "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-shortest",
            str(output_video),
        ],
        check=True,
    )


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
            "fps=1/2,scale=270:-1,tile=8x1",
            "-frames:v",
            "1",
            str(output_path),
        ],
        check=True,
    )


def _ffprobe(path: Path) -> dict[str, Any]:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_format", "-show_streams", "-print_format", "json", str(path)],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return json.loads(result.stdout)


def _get_json(url: str) -> Any:
    request = Request(url, headers={"Accept": "application/json"}, method="GET")
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
