"""Generate a reviewed ShangK first frame with Qwen Image Edit."""

from __future__ import annotations

import argparse
import json
import os
import shutil
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
SHANGK_INPUT = COMFY_INPUT / "\u5546k"
SHANGK_OUTPUT = COMFY_OUTPUT / "\u5546k"
RAG_DOCS = PROJECT_ROOT / "deployment" / "comfyui" / "commercial_ktv_workflow" / "cu130_runtime_workflow_rag_documents.jsonl"
REPORT_ROOT = PROJECT_ROOT / "deployment" / "comfyui" / "commercial_ktv_workflow" / "shangk_first_frame"
QWEN_SINGLE_IMAGE_WORKFLOW_SOURCE_ID = "comfyui_cu130_runtime_553e8db0c7a1"
OUTPUT_PREFIX_BASE = "\u5546k/\u9996\u56fe\u751f\u6210"

DEFAULT_PROMPT = (
    "Use the input ShangK private-room photo as the exact background and camera perspective. "
    "Create one new fictional adult AI female singer in the room, beautiful, elegant, normal and realistic, "
    "full body visible, standing on the open floor near the sofa and table, facing the camera with strong lens presence, "
    "holding a wireless microphone near her mouth as if singing. She wears a refined black sequined mini dress and high heels. "
    "Preserve the real room layout, sofa, table, screen, blue neon lights, glossy floor reflections, and all lighting mood. "
    "Integrate her naturally with correct shadows and reflections. Premium Douyin KTV commercial first frame, vertical 9:16, "
    "not a pasted real-person cutout."
)
DEFAULT_NEGATIVE = (
    "seated, sitting, leaning on sofa, table blocking body, cropped feet, missing microphone, hidden hands, bad hands, "
    "extra fingers, missing fingers, extra limbs, broken arms, broken legs, deformed face, asymmetrical eyes, old face, male, "
    "childlike, duplicate person, crowd, pasted portrait, real-person cutout, watermark, subtitles, QR code, Douyin UI, "
    "changed room layout, messy background, low quality, blur, plastic skin"
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8188")
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--scene", type=Path, default=None)
    parser.add_argument("--scene-dir", type=Path, default=SHANGK_INPUT / "\u573a\u666f")
    parser.add_argument("--prompt", default=DEFAULT_PROMPT)
    parser.add_argument("--negative-prompt", default=DEFAULT_NEGATIVE)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--steps", type=int, default=4)
    parser.add_argument("--timeout-seconds", type=int, default=1200)
    args = parser.parse_args()

    run_id = args.run_id or f"shangk_qwen_first_frame_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.environ["COMFYUI_RUNTIME_BASE_URL"] = args.base_url
    REPORT_ROOT.mkdir(parents=True, exist_ok=True)
    (SHANGK_OUTPUT / "\u9996\u56fe\u751f\u6210").mkdir(parents=True, exist_ok=True)
    SHANGK_INPUT.mkdir(parents=True, exist_ok=True)

    scene_path = args.scene or _latest_file(args.scene_dir, {".png", ".jpg", ".jpeg", ".webp"})
    scene_name = _input_relative_name(scene_path)
    output_prefix = f"{OUTPUT_PREFIX_BASE}/{run_id}"
    workflow = _workflow_from_source_id(QWEN_SINGLE_IMAGE_WORKFLOW_SOURCE_ID)
    object_info = _get_json(f"{args.base_url.rstrip('/')}/object_info")

    materializer = ComfyUIWorkflowMaterializer()
    result = materializer.materialize_api_prompt(
        source_workflow_path=workflow["workflow_path"],
        parameter_plan={"positive_prompt": args.prompt, "negative_prompt": args.negative_prompt},
        stage_key="shangk_qwen_first_frame",
        run_id=run_id,
        input_assets={"scene_image_name": scene_name},
        node_overrides={
            "3": {"steps": args.steps, "cfg": 1, "sampler_name": "euler", "scheduler": "simple", "denoise": 1},
            "60": {"filename_prefix": output_prefix},
            "76": {"prompt": args.prompt},
            "77": {"prompt": args.negative_prompt},
            "78": {"image": scene_name},
        },
        output_prefix=output_prefix,
        object_info=object_info,
    )
    prompt = _load_json(Path(result.api_prompt_path))
    if args.seed is not None and "3" in prompt and isinstance(prompt["3"].get("inputs"), dict):
        prompt["3"]["inputs"]["seed"] = args.seed
        Path(result.api_prompt_path).write_text(json.dumps(prompt, ensure_ascii=False, indent=2), encoding="utf-8")
    preflight = materializer.preflight_api_prompt(prompt, object_info=object_info)
    if not preflight["prompt_ready"]:
        raise RuntimeError(f"Qwen first-frame preflight failed: {preflight['missing_node_types']} {preflight['unresolved_inputs'][:8]}")

    workflow_payload = _load_json(Path(result.materialization.materialized_workflow_path))
    submit = _submit_prompt(
        base_url=args.base_url,
        prompt=prompt,
        workflow=workflow_payload,
        client_id=f"aiops-{run_id}-qwen-first-frame",
    )
    prompt_id = str(submit.get("prompt_id") or "")
    if not prompt_id:
        raise RuntimeError(f"Qwen first-frame submit failed: {json.dumps(submit, ensure_ascii=False)[:2000]}")

    history = _poll_history(base_url=args.base_url, prompt_id=prompt_id, timeout_seconds=args.timeout_seconds)
    outputs = _history_outputs(history, prompt_id)
    files = _resolve_output_files(outputs)
    image = _first_existing(files, {".png", ".jpg", ".jpeg", ".webp"})
    if image is None:
        raise RuntimeError(f"Qwen first-frame produced no image. prompt_id={prompt_id}")

    root_first_frame = COMFY_INPUT / "shangk_standing_mic_first_frame.png"
    shangk_first_frame = SHANGK_INPUT / "shangk_standing_mic_first_frame.png"
    approved_first_frame = SHANGK_INPUT / "shangk_approved_first_frame.png"
    shutil.copy2(image, root_first_frame)
    shutil.copy2(image, shangk_first_frame)
    shutil.copy2(image, approved_first_frame)

    run_dir = REPORT_ROOT / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "status": "success",
        "run_id": run_id,
        "prompt_id": prompt_id,
        "workflow": workflow,
        "scene_path": str(scene_path),
        "scene_name": scene_name,
        "prompt": args.prompt,
        "negative_prompt": args.negative_prompt,
        "steps": args.steps,
        "seed": args.seed,
        "materialized_workflow_path": result.materialization.materialized_workflow_path,
        "api_prompt_path": result.api_prompt_path,
        "output_image": str(image),
        "registered_root_first_frame": str(root_first_frame),
        "registered_shangk_first_frame": str(shangk_first_frame),
        "registered_approved_first_frame": str(approved_first_frame),
        "history_status": _history_status(history, prompt_id),
        "output_files": [str(path) for path in files],
        "submit": submit,
    }
    report_path = run_dir / "report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"report": str(report_path), "output_image": str(image), "registered_first_frame": str(root_first_frame)}, ensure_ascii=False, indent=2))


def _workflow_from_source_id(source_id: str) -> dict[str, Any]:
    with RAG_DOCS.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            item = json.loads(line)
            if item.get("source_id") == source_id:
                metadata = dict(item.get("metadata") or {})
                return {
                    "workflow_id": source_id,
                    "workflow_name": metadata.get("workflow_name"),
                    "workflow_path": metadata.get("workflow_path"),
                    "category": metadata.get("category"),
                    "capabilities": metadata.get("capabilities"),
                }
    raise FileNotFoundError(f"Workflow source_id not found in RAG docs: {source_id}")


def _submit_prompt(*, base_url: str, prompt: dict[str, Any], workflow: dict[str, Any], client_id: str) -> dict[str, Any]:
    payload = {"prompt": prompt, "client_id": client_id, "extra_data": {"extra_pnginfo": {"workflow": workflow}}}
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
        time.sleep(5)
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


def _input_relative_name(path: Path) -> str:
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(COMFY_INPUT.resolve())
    except ValueError:
        target = COMFY_INPUT / resolved.name
        if resolved != target.resolve():
            shutil.copy2(resolved, target)
        relative = target.relative_to(COMFY_INPUT)
    return relative.as_posix()


def _get_json(url: str) -> Any:
    request = Request(url, headers={"Accept": "application/json"}, method="GET")
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
