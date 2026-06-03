# -*- coding: utf-8 -*-
"""Batch commercial KTV promo workflow for local ComfyUI.

The workflow expects prepared vertical seed images. Each seed image should
already contain the desired KTV room, host/model, lighting, and composition.
This script turns those seed images into Wan video clips through ComfyUI, then
assembles a vertical promo with optional voiceover and subtitles.
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

import cv2
import numpy as np

COMFY_ROOT = Path(r"E:\ComfyUI_cu130\ComfyUI")
COMFY_INPUT = COMFY_ROOT / "input"
COMFY_OUTPUT = COMFY_ROOT / "output"
COMFY_API = "http://127.0.0.1:8188"
RUN_ROOT = Path(r"D:\aiops_production_runs")
CLIENT_ID = f"aiops-commercial-ktv-{uuid4()}"

WIDTH = 720
HEIGHT = 1280
I2V_WIDTH = 480
I2V_HEIGHT = 832
I2V_FRAMES = 33
I2V_FPS = 16
FINAL_FPS = 30

DEFAULT_NEGATIVE_PROMPT = (
    "low quality, blurry, flicker, jitter, distorted face, bad hands, extra fingers, "
    "extra limbs, duplicate person, warped room, changed layout, text, logo, watermark, "
    "cartoon, anime, plastic skin, overexposed, oversaturated"
)


@dataclass(frozen=True)
class Shot:
    shot_id: str
    seed_image: Path
    prompt: str
    duration: float
    seed: int
    title: str = ""


def run(cmd: list[str | Path], *, timeout: int | None = None) -> None:
    print("[cmd]", " ".join(str(part) for part in cmd), flush=True)
    subprocess.run([str(part) for part in cmd], check=True, timeout=timeout)


def capture(cmd: list[str | Path], *, timeout: int | None = None) -> str:
    return subprocess.check_output(
        [str(part) for part in cmd],
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )


def http_json(method: str, path: str, payload: dict[str, Any] | None = None, timeout: int = 30) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(
        f"{COMFY_API}{path}",
        data=data,
        headers={"Content-Type": "application/json"},
        method=method,
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = response.read().decode("utf-8")
    return json.loads(body) if body else {}


def ffprobe_duration(path: Path) -> float:
    return float(
        capture(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                path,
            ],
            timeout=60,
        ).strip()
    )


def imread(path: Path) -> np.ndarray:
    data = np.fromfile(str(path), dtype=np.uint8)
    image = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if image is None:
        raise RuntimeError(f"Cannot read image: {path}")
    return image


def imwrite(path: Path, image: np.ndarray, quality: int = 95) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    params = [cv2.IMWRITE_JPEG_QUALITY, quality] if path.suffix.lower() in {".jpg", ".jpeg"} else []
    ok, buffer = cv2.imencode(path.suffix, image, params)
    if not ok:
        raise RuntimeError(f"Cannot write image: {path}")
    buffer.tofile(str(path))


def cover_resize(image: np.ndarray, width: int = WIDTH, height: int = HEIGHT) -> np.ndarray:
    src_h, src_w = image.shape[:2]
    scale = max(width / src_w, height / src_h)
    resized = cv2.resize(image, (int(src_w * scale + 0.5), int(src_h * scale + 0.5)), interpolation=cv2.INTER_AREA)
    h, w = resized.shape[:2]
    x = max(0, (w - width) // 2)
    y = max(0, (h - height) // 2)
    return resized[y : y + height, x : x + width].copy()


def alpha_composite(base: np.ndarray, overlay: np.ndarray, x: int, y: int) -> None:
    h, w = overlay.shape[:2]
    x1, y1 = max(0, x), max(0, y)
    x2, y2 = min(base.shape[1], x + w), min(base.shape[0], y + h)
    if x1 >= x2 or y1 >= y2:
        return
    ox1, oy1 = x1 - x, y1 - y
    patch = overlay[oy1 : oy1 + (y2 - y1), ox1 : ox1 + (x2 - x1)]
    alpha = patch[:, :, 3:4].astype(np.float32) / 255.0
    roi = base[y1:y2, x1:x2]
    roi[:] = (patch[:, :, :3].astype(np.float32) * alpha + roi.astype(np.float32) * (1.0 - alpha)).astype(np.uint8)


def draw_virtual_host(scale: float = 1.0) -> np.ndarray:
    """Draw a clean full-body virtual KTV host cutout as BGRA.

    This is a deterministic seed-image fallback for scene-only mode. A future
    SDXL/Flux inpainting layer can replace it without changing the video step.
    """

    width = int(360 * scale)
    height = int(900 * scale)
    ss = 3
    canvas = np.zeros((height * ss, width * ss, 4), dtype=np.uint8)
    s = scale * ss
    cx = width * ss // 2

    def point(x: float, y: float) -> tuple[int, int]:
        return int(cx + x * s), int(y * s)

    def poly(points: list[tuple[float, float]], color: tuple[int, int, int, int]) -> None:
        cv2.fillPoly(canvas, [np.array([point(x, y) for x, y in points], np.int32)], color, cv2.LINE_AA)

    def line(a: tuple[float, float], b: tuple[float, float], color: tuple[int, int, int, int], thickness: float) -> None:
        cv2.line(canvas, point(*a), point(*b), color, max(1, int(thickness * s)), cv2.LINE_AA)

    def ellipse(center: tuple[float, float], axes: tuple[float, float], color: tuple[int, int, int, int], angle: float = 0) -> None:
        cv2.ellipse(canvas, point(*center), (int(axes[0] * s), int(axes[1] * s)), angle, 0, 360, color, -1, cv2.LINE_AA)

    skin = (188, 142, 112, 255)
    hair = (18, 16, 22, 255)
    black = (18, 18, 24, 255)
    suit = (28, 26, 35, 255)
    blouse = (230, 224, 214, 255)
    neon_magenta = (235, 70, 210, 230)
    neon_cyan = (255, 180, 30, 220)

    # Soft outer glow/rim is drawn first.
    glow = (210, 54, 225, 70)
    line((-112, 270), (-154, 458), glow, 28)
    line((112, 270), (154, 438), glow, 28)
    poly([(-82, 238), (82, 238), (112, 560), (46, 600), (-48, 600), (-112, 560)], (70, 30, 85, 60))

    # Legs and shoes.
    poly([(-50, 548), (-18, 548), (-20, 762), (-58, 762)], skin)
    poly([(20, 548), (53, 548), (64, 762), (30, 762)], skin)
    ellipse((-42, 782), (44, 13), black, -8)
    ellipse((50, 782), (44, 13), black, 8)

    # Outfit.
    poly([(-88, 250), (88, 250), (105, 420), (-104, 420)], suit)
    poly([(-45, 258), (42, 258), (28, 418), (-30, 418)], blouse)
    poly([(-106, 416), (108, 416), (122, 570), (44, 605), (-46, 605), (-122, 570)], suit)
    line((-34, 292), (-36, 408), neon_magenta, 2.0)
    line((34, 292), (32, 408), neon_cyan, 2.0)

    # Arms and microphone.
    line((-82, 282), (-112, 382), skin, 18)
    line((-112, 382), (-78, 482), skin, 16)
    line((82, 282), (122, 358), skin, 18)
    line((122, 358), (88, 444), skin, 16)
    line((84, 444), (58, 320), (36, 34, 40, 255), 7)
    ellipse((55, 306), (17, 23), (42, 42, 48, 255), -12)

    # Head, hair, and face.
    ellipse((0, 222), (26, 34), skin)
    ellipse((0, 138), (74, 92), hair)
    ellipse((0, 147), (57, 72), skin)
    poly([(-70, 132), (-30, 76), (48, 78), (82, 178), (60, 268), (34, 248), (50, 166)], hair)
    poly([(-70, 154), (-92, 280), (-48, 270), (-40, 176)], hair)
    ellipse((-22, 143), (7, 4), (18, 18, 24, 255))
    ellipse((23, 143), (7, 4), (18, 18, 24, 255))
    line((-35, 128), (-12, 126), (38, 28, 32, 255), 1.4)
    line((12, 126), (35, 128), (38, 28, 32, 255), 1.4)
    ellipse((0, 181), (15, 5), (118, 48, 68, 255))
    ellipse((-55, 164), (10, 16), (56, 220, 245, 255))
    ellipse((55, 164), (10, 16), (56, 220, 245, 255))

    # Add a thin bright rim to help the host sit in neon scenes.
    alpha = canvas[:, :, 3]
    outline = cv2.dilate(alpha, np.ones((9, 9), np.uint8), iterations=1) - alpha
    rim = np.zeros_like(canvas)
    rim[:, :, 0] = 255
    rim[:, :, 1] = 80
    rim[:, :, 2] = 225
    rim[:, :, 3] = np.clip(outline * 0.45, 0, 130).astype(np.uint8)
    out = rim.astype(np.float32)
    a = canvas[:, :, 3:4].astype(np.float32) / 255.0
    out[:, :, :3] = canvas[:, :, :3].astype(np.float32) * a + out[:, :, :3] * (1.0 - a)
    out[:, :, 3:4] = np.maximum(out[:, :, 3:4], canvas[:, :, 3:4])
    return cv2.resize(np.clip(out, 0, 255).astype(np.uint8), (width, height), interpolation=cv2.INTER_AREA)


def orient_upright(image: np.ndarray) -> np.ndarray:
    height, width = image.shape[:2]
    if width > height:
        return cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    return image


def person_cutout_rgba(person_image: Path) -> np.ndarray:
    """Extract the largest person mask from a portrait image using local YOLO."""

    from ultralytics import YOLO

    model_path = COMFY_ROOT / "models" / "ultralytics" / "segm" / "yolov8n-seg.pt"
    if not model_path.exists():
        raise RuntimeError(f"Missing segmentation model: {model_path}")

    image = orient_upright(imread(person_image))
    temp = RUN_ROOT / "_tmp_person_cutout_source.jpg"
    imwrite(temp, image, quality=96)
    model = YOLO(str(model_path))
    result = model(str(temp), imgsz=1280, conf=0.2, verbose=False)[0]
    if result.masks is None:
        raise RuntimeError(f"No person mask detected: {person_image}")

    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    classes = result.boxes.cls.cpu().numpy().astype(int)
    masks = result.masks.data.cpu().numpy()
    best_area = 0
    for index, class_id in enumerate(classes):
        if class_id != 0:
            continue
        candidate = cv2.resize(
            (masks[index] > 0.45).astype(np.uint8) * 255,
            (image.shape[1], image.shape[0]),
            interpolation=cv2.INTER_NEAREST,
        )
        area = int((candidate > 0).sum())
        if area > best_area:
            best_area = area
            mask = candidate
    if best_area == 0:
        raise RuntimeError(f"No person mask detected: {person_image}")

    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((11, 11), np.uint8), iterations=2)
    mask = cv2.GaussianBlur(mask, (0, 0), 4)
    ys, xs = np.where(mask > 16)
    x1, x2 = max(0, int(xs.min()) - 16), min(image.shape[1] - 1, int(xs.max()) + 16)
    y1, y2 = max(0, int(ys.min()) - 16), min(image.shape[0] - 1, int(ys.max()) + 12)
    crop = image[y1 : y2 + 1, x1 : x2 + 1]
    crop_mask = mask[y1 : y2 + 1, x1 : x2 + 1]
    rgba = cv2.cvtColor(crop, cv2.COLOR_BGR2BGRA)
    rgba[:, :, 3] = crop_mask
    return rgba


def relight_person_for_ktv(rgba: np.ndarray) -> np.ndarray:
    bgr = rgba[:, :, :3].astype(np.float32)
    alpha = rgba[:, :, 3:4]
    tint = np.full_like(bgr, (40, 12, 78), dtype=np.float32)
    bgr = bgr * 0.82 + tint * 0.18
    rim = np.zeros_like(rgba)
    edge = cv2.dilate(alpha[:, :, 0], np.ones((9, 9), np.uint8), iterations=1) - alpha[:, :, 0]
    rim[:, :, 0] = 255
    rim[:, :, 1] = 80
    rim[:, :, 2] = 210
    rim[:, :, 3] = np.clip(edge * 0.35, 0, 110).astype(np.uint8)
    out = rgba.copy()
    out[:, :, :3] = np.clip(bgr, 0, 255).astype(np.uint8)
    canvas = rim.copy()
    alpha_composite(canvas[:, :, :3], out, 0, 0) if False else None
    return out


def make_scene_only_seed(scene_image: Path, output: Path, *, host_scale: float = 0.78, x_ratio: float = 0.53, foot_ratio: float = 0.93) -> None:
    scene = cover_resize(imread(scene_image), WIDTH, HEIGHT)
    # Commercial KTV look: deepen shadows, keep neon saturation, add slight vignette.
    wash = np.full_like(scene, (18, 8, 22), dtype=np.uint8)
    scene = cv2.addWeighted(scene, 0.92, wash, 0.08, 0)
    scene = cv2.convertScaleAbs(scene, alpha=1.05, beta=2)

    host = draw_virtual_host(scale=host_scale)
    x = int(WIDTH * x_ratio - host.shape[1] / 2)
    y = int(HEIGHT * foot_ratio - host.shape[0])

    # Ground contact shadow.
    shadow = np.zeros((HEIGHT, WIDTH, 4), dtype=np.uint8)
    cv2.ellipse(
        shadow,
        (int(WIDTH * x_ratio), int(HEIGHT * foot_ratio) + 10),
        (int(115 * host_scale), int(24 * host_scale)),
        0,
        0,
        360,
        (0, 0, 0, 90),
        -1,
        cv2.LINE_AA,
    )
    alpha_composite(scene, shadow, 0, 0)
    alpha_composite(scene, host, x, y)

    # Gentle color bloom near the person to blend into room lights.
    bloom = np.zeros_like(scene)
    cv2.circle(bloom, (int(WIDTH * x_ratio), int(HEIGHT * 0.55)), int(190 * host_scale), (90, 30, 130), -1, cv2.LINE_AA)
    scene = cv2.addWeighted(scene, 1.0, bloom, 0.08, 0)
    imwrite(output, scene, quality=96)


def make_scene_person_seed(
    scene_image: Path,
    person_image: Path,
    output: Path,
    *,
    person_height: int = 720,
    x_ratio: float = 0.52,
    foot_ratio: float = 0.91,
) -> None:
    scene = cover_resize(imread(scene_image), WIDTH, HEIGHT)
    wash = np.full_like(scene, (18, 8, 22), dtype=np.uint8)
    scene = cv2.addWeighted(scene, 0.90, wash, 0.10, 0)
    scene = cv2.convertScaleAbs(scene, alpha=1.04, beta=0)

    cutout = relight_person_for_ktv(person_cutout_rgba(person_image))
    scale = person_height / cutout.shape[0]
    target_w = max(1, int(cutout.shape[1] * scale))
    person = cv2.resize(cutout, (target_w, person_height), interpolation=cv2.INTER_AREA)
    x = int(WIDTH * x_ratio - person.shape[1] / 2)
    y = int(HEIGHT * foot_ratio - person.shape[0])

    shadow = np.zeros((HEIGHT, WIDTH, 4), dtype=np.uint8)
    cv2.ellipse(
        shadow,
        (int(WIDTH * x_ratio), int(HEIGHT * foot_ratio) + 10),
        (max(45, person.shape[1] // 3), 25),
        0,
        0,
        360,
        (0, 0, 0, 85),
        -1,
        cv2.LINE_AA,
    )
    alpha_composite(scene, shadow, 0, 0)
    alpha_composite(scene, person, x, y)

    bloom = np.zeros_like(scene)
    cv2.circle(bloom, (int(WIDTH * x_ratio), int(HEIGHT * 0.52)), 190, (80, 20, 120), -1, cv2.LINE_AA)
    scene = cv2.addWeighted(scene, 1.0, bloom, 0.06, 0)
    imwrite(output, scene, quality=96)


def load_manifest(path: Path) -> list[Shot]:
    shots: list[Shot] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"shot_id", "seed_image", "prompt"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Manifest is missing required columns: {', '.join(sorted(missing))}")
        for index, row in enumerate(reader, start=1):
            shot_id = (row.get("shot_id") or f"shot_{index:02d}").strip()
            seed_image = Path((row.get("seed_image") or "").strip())
            prompt = (row.get("prompt") or "").strip()
            if not seed_image.exists():
                raise FileNotFoundError(f"Seed image not found for {shot_id}: {seed_image}")
            duration = float(row.get("duration") or 3.8)
            seed = int(row.get("seed") or (2026052700 + index))
            shots.append(
                Shot(
                    shot_id=shot_id,
                    seed_image=seed_image,
                    prompt=prompt,
                    duration=duration,
                    seed=seed,
                    title=(row.get("title") or "").strip(),
                )
            )
    if not shots:
        raise ValueError("Manifest has no shots.")
    return shots


def ensure_comfy_ready() -> dict[str, Any]:
    stats = http_json("GET", "/system_stats", timeout=10)
    object_info = http_json("GET", "/object_info", timeout=30)
    required_nodes = {
        "LoadImage",
        "WanVideoVAELoader",
        "WanVideoEncode",
        "WanVideoEmptyEmbeds",
        "WanVideoTextEncodeCached",
        "WanVideoModelLoader",
        "WanVideoSampler",
        "WanVideoDecode",
        "VHS_VideoCombine",
    }
    available = set(object_info.keys())
    missing_nodes = sorted(required_nodes - available)
    required_files = [
        COMFY_ROOT / "models" / "diffusion_models" / "Wan2.2" / "wan2.2_ti2v_5B_fp16.safetensors",
        COMFY_ROOT / "models" / "vae" / "wan2.2_vae.safetensors",
        COMFY_ROOT / "models" / "text_encoders" / "umt5-xxl-enc-bf16.safetensors",
    ]
    missing_files = [str(path) for path in required_files if not path.exists()]
    return {
        "ok": not missing_nodes and not missing_files,
        "comfy_api": COMFY_API,
        "stats": stats,
        "missing_nodes": missing_nodes,
        "missing_files": missing_files,
    }


def make_run_dir(label: str) -> Path:
    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    run_dir = RUN_ROOT / f"commercial_ktv_{label}_{stamp}"
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "comfy_inputs").mkdir(exist_ok=True)
    (run_dir / "clips").mkdir(exist_ok=True)
    return run_dir


def prepare_seed_image(source: Path, run_dir: Path, shot_id: str) -> str:
    target = run_dir / "comfy_inputs" / f"{shot_id}_480x832.jpg"
    vf = (
        f"scale={I2V_WIDTH}:{I2V_HEIGHT}:force_original_aspect_ratio=increase,"
        f"crop={I2V_WIDTH}:{I2V_HEIGHT},setsar=1"
    )
    run(["ffmpeg", "-y", "-i", source, "-vf", vf, "-frames:v", "1", "-q:v", "2", target], timeout=120)
    comfy_target = COMFY_INPUT / target.name
    shutil.copy2(target, comfy_target)
    return comfy_target.name


def wan_i2v_prompt(*, image_name: str, positive: str, prefix: str, seed: int) -> dict[str, Any]:
    return {
        "1": {"class_type": "LoadImage", "inputs": {"image": image_name}},
        "2": {
            "class_type": "WanVideoVAELoader",
            "inputs": {
                "model_name": "wan2.2_vae.safetensors",
                "precision": "bf16",
                "use_cpu_cache": False,
                "verbose": False,
            },
        },
        "3": {
            "class_type": "WanVideoEncode",
            "inputs": {
                "vae": ["2", 0],
                "image": ["1", 0],
                "enable_vae_tiling": False,
                "tile_x": 272,
                "tile_y": 272,
                "tile_stride_x": 144,
                "tile_stride_y": 128,
                "noise_aug_strength": 0.018,
                "latent_strength": 0.94,
            },
        },
        "4": {
            "class_type": "WanVideoEmptyEmbeds",
            "inputs": {"width": I2V_WIDTH, "height": I2V_HEIGHT, "num_frames": I2V_FRAMES, "extra_latents": ["3", 0]},
        },
        "5": {
            "class_type": "WanVideoTextEncodeCached",
            "inputs": {
                "model_name": "umt5-xxl-enc-bf16.safetensors",
                "precision": "bf16",
                "positive_prompt": positive,
                "negative_prompt": DEFAULT_NEGATIVE_PROMPT,
                "quantization": "disabled",
                "use_disk_cache": True,
                "device": "gpu",
            },
        },
        "6": {
            "class_type": "WanVideoBlockSwap",
            "inputs": {
                "blocks_to_swap": 18,
                "offload_img_emb": False,
                "offload_txt_emb": False,
                "use_non_blocking": True,
                "vace_blocks_to_swap": 0,
                "prefetch_blocks": 1,
                "block_swap_debug": False,
            },
        },
        "7": {
            "class_type": "WanVideoModelLoader",
            "inputs": {
                "model": r"Wan2.2\wan2.2_ti2v_5B_fp16.safetensors",
                "base_precision": "fp16_fast",
                "quantization": "disabled",
                "load_device": "offload_device",
                "attention_mode": "sdpa",
                "block_swap_args": ["6", 0],
                "rms_norm_function": "default",
            },
        },
        "8": {
            "class_type": "WanVideoEasyCache",
            "inputs": {"easycache_thresh": 0.015, "start_step": 8, "end_step": -1, "cache_device": "offload_device"},
        },
        "9": {"class_type": "WanVideoSLG", "inputs": {"blocks": "7,8,9", "start_percent": 0.1, "end_percent": 0.7}},
        "10": {
            "class_type": "WanVideoSampler",
            "inputs": {
                "model": ["7", 0],
                "image_embeds": ["4", 0],
                "text_embeds": ["5", 0],
                "steps": 24,
                "cfg": 4.5,
                "shift": 8.0,
                "seed": seed,
                "force_offload": True,
                "scheduler": "flowmatch_pusa",
                "riflex_freq_index": 0,
                "cache_args": ["8", 0],
                "slg_args": ["9", 0],
                "denoise_strength": 1.0,
                "batched_cfg": False,
                "rope_function": "comfy",
                "start_step": 0,
                "end_step": -1,
                "add_noise_to_samples": False,
            },
        },
        "11": {
            "class_type": "WanVideoDecode",
            "inputs": {
                "vae": ["2", 0],
                "samples": ["10", 0],
                "enable_vae_tiling": True,
                "tile_x": 272,
                "tile_y": 272,
                "tile_stride_x": 144,
                "tile_stride_y": 128,
                "normalization": "default",
            },
        },
        "12": {
            "class_type": "VHS_VideoCombine",
            "inputs": {
                "images": ["11", 0],
                "frame_rate": I2V_FPS,
                "loop_count": 0,
                "filename_prefix": prefix,
                "format": "video/h264-mp4",
                "pix_fmt": "yuv420p",
                "crf": 19,
                "save_metadata": True,
                "trim_to_audio": False,
                "pingpong": False,
                "save_output": True,
            },
        },
    }


def submit_prompt(prompt: dict[str, Any]) -> str:
    try:
        result = http_json("POST", "/prompt", {"prompt": prompt, "client_id": CLIENT_ID}, timeout=60)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"ComfyUI prompt rejected: HTTP {exc.code} {body}") from exc
    prompt_id = str(result.get("prompt_id") or "")
    if not prompt_id:
        raise RuntimeError(f"ComfyUI did not return prompt_id: {result}")
    return prompt_id


def wait_for_prompt_history(prompt_id: str, timeout: int) -> dict[str, Any]:
    start = time.time()
    while time.time() - start < timeout:
        result = http_json("GET", f"/history/{prompt_id}", timeout=60)
        if prompt_id in result:
            item = result[prompt_id]
            status = item.get("status") or {}
            if status.get("status_str") == "error":
                raise RuntimeError(json.dumps(status, ensure_ascii=False, indent=2))
            return item
        time.sleep(5)
    raise TimeoutError(f"Timed out waiting for ComfyUI history {prompt_id}")


def wait_for_history(prompt_id: str, timeout: int) -> dict[str, Any]:
    start = time.time()
    while time.time() - start < timeout:
        result = http_json("GET", f"/history/{prompt_id}", timeout=60)
        if prompt_id in result:
            item = result[prompt_id]
            status = item.get("status") or {}
            if status.get("status_str") == "error":
                raise RuntimeError(json.dumps(status, ensure_ascii=False, indent=2))
            return item
        queue = http_json("GET", "/queue", timeout=30)
        print(
            "[comfy] waiting",
            prompt_id,
            "running=",
            len(queue.get("queue_running", [])),
            "pending=",
            len(queue.get("queue_pending", [])),
            flush=True,
        )
        time.sleep(10)
    raise TimeoutError(f"Timed out waiting for ComfyUI history {prompt_id}")


def flux_kontext_scene_ai_seed_prompt(*, image_name: str, positive: str, prefix: str, seed: int) -> dict[str, Any]:
    return {
        "1": {"class_type": "LoadImage", "inputs": {"image": image_name}},
        "2": {
            "class_type": "FluxKontextProImageNode",
            "inputs": {
                "prompt": positive,
                "aspect_ratio": "9:16",
                "guidance": 3.5,
                "steps": 40,
                "seed": seed,
                "prompt_upsampling": False,
                "input_image": ["1", 0],
            },
        },
        "3": {"class_type": "SaveImage", "inputs": {"images": ["2", 0], "filename_prefix": prefix}},
    }


def sdxl_inpaint_virtual_host_prompt(
    *,
    image_name: str,
    mask_name: str,
    model_path: str,
    positive: str,
    negative: str,
    prefix: str,
    seed: int,
    steps: int = 32,
    cfg: float = 7.0,
    denoise: float = 1.0,
) -> dict[str, Any]:
    return {
        "1": {"class_type": "LoadImage", "inputs": {"image": image_name}},
        "2": {"class_type": "LoadImageMask", "inputs": {"image": mask_name, "channel": "red"}},
        "3": {"class_type": "DiffusersLoader", "inputs": {"model_path": model_path}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"text": positive, "clip": ["3", 1]}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"text": negative, "clip": ["3", 1]}},
        "6": {
            "class_type": "InpaintModelConditioning",
            "inputs": {
                "positive": ["4", 0],
                "negative": ["5", 0],
                "vae": ["3", 2],
                "pixels": ["1", 0],
                "mask": ["2", 0],
                "noise_mask": True,
            },
        },
        "7": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["3", 0],
                "positive": ["6", 0],
                "negative": ["6", 1],
                "latent_image": ["6", 2],
                "seed": seed,
                "steps": steps,
                "cfg": cfg,
                "sampler_name": "dpmpp_2m",
                "scheduler": "karras",
                "denoise": denoise,
            },
        },
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["3", 2]}},
        "9": {"class_type": "SaveImage", "inputs": {"images": ["8", 0], "filename_prefix": prefix}},
    }


def default_virtual_host_positive_prompt() -> str:
    return (
        "photorealistic fictional AI female KTV host standing naturally inside the exact same luxury private KTV room, "
        "full body, elegant black fitted dress, holding a microphone, business reception style, confident gentle smile, "
        "matching blue and magenta club lighting, realistic shadows on the floor, correct perspective and scale, "
        "commercial photography, high detail face, natural hands, preserve the original room layout"
    )


def export_workflow_jsons(
    output_dir: Path,
    *,
    image_name: str,
    mask_name: str,
    sdxl_model_path: str,
    wan_image_name: str | None = None,
) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    wan_prompt = wan_i2v_prompt(
        image_name=wan_image_name or image_name,
        positive=(
            "A fictional AI female KTV host in the same luxury private room gently moves, slight breathing, "
            "subtle hand gesture with microphone, stable face, stable outfit, cinematic commercial lighting."
        ),
        prefix="aiops_virtual_host_wan_i2v",
        seed=2026052741,
    )
    sdxl_prompt = sdxl_inpaint_virtual_host_prompt(
        image_name=image_name,
        mask_name=mask_name,
        model_path=sdxl_model_path,
        positive=default_virtual_host_positive_prompt(),
        negative=DEFAULT_NEGATIVE_PROMPT,
        prefix="aiops_virtual_host_sdxl_inpaint",
        seed=2026052742,
    )
    files = {
        "wan_i2v": output_dir / "comfyui_wan_i2v_virtual_host_api_workflow.json",
        "sdxl_inpaint": output_dir / "comfyui_sdxl_inpaint_virtual_host_api_workflow.json",
    }
    files["wan_i2v"].write_text(json.dumps(wan_prompt, ensure_ascii=False, indent=2), encoding="utf-8")
    files["sdxl_inpaint"].write_text(json.dumps(sdxl_prompt, ensure_ascii=False, indent=2), encoding="utf-8")
    return {key: str(value) for key, value in files.items()}


def saved_images_from_history(history: dict[str, Any]) -> list[Path]:
    paths: list[Path] = []
    outputs = history.get("outputs") or {}
    for value in outputs.values():
        images = value.get("images") if isinstance(value, dict) else None
        if not isinstance(images, list):
            continue
        for image in images:
            if not isinstance(image, dict):
                continue
            filename = image.get("filename")
            subfolder = image.get("subfolder") or ""
            if filename:
                paths.append(COMFY_OUTPUT / str(subfolder) / str(filename))
    return paths


def newest_output(prefix: str, after: float) -> Path:
    candidates = [path for path in COMFY_OUTPUT.glob(f"{prefix}*.mp4") if path.stat().st_mtime >= after - 2]
    if not candidates:
        raise RuntimeError(f"No ComfyUI MP4 output found for prefix {prefix}")
    return sorted(candidates, key=lambda p: p.stat().st_mtime, reverse=True)[0]


def render_shots(shots: list[Shot], run_dir: Path, timeout: int) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for index, shot in enumerate(shots, start=1):
        print(f"[shot] {index}/{len(shots)} {shot.shot_id}", flush=True)
        image_name = prepare_seed_image(shot.seed_image, run_dir, shot.shot_id)
        prefix = f"commercial_ktv_{run_dir.name}_{index:02d}_{shot.shot_id}"
        prompt = wan_i2v_prompt(image_name=image_name, positive=shot.prompt, prefix=prefix, seed=shot.seed)
        (run_dir / f"{shot.shot_id}_prompt.json").write_text(
            json.dumps(prompt, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        start = time.time()
        prompt_id = submit_prompt(prompt)
        print(f"[comfy] prompt_id={prompt_id}", flush=True)
        history = wait_for_history(prompt_id, timeout=timeout)
        (run_dir / f"{shot.shot_id}_history.json").write_text(
            json.dumps(history, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        output = newest_output(prefix, after=start)
        local = run_dir / "clips" / f"{index:02d}_{shot.shot_id}.mp4"
        shutil.copy2(output, local)
        results.append(
            {
                "shot_id": shot.shot_id,
                "title": shot.title,
                "seed_image": str(shot.seed_image),
                "prompt": shot.prompt,
                "seed": shot.seed,
                "target_duration": shot.duration,
                "prompt_id": prompt_id,
                "comfy_output": str(output),
                "clip": str(local),
            }
        )
    return results


def normalize_clip(source: Path, target: Path, duration: float) -> None:
    cmd: list[str | Path] = ["ffmpeg", "-y"]
    if ffprobe_duration(source) < duration - 0.1:
        cmd += ["-stream_loop", "-1"]
    cmd += [
        "-i",
        source,
        "-t",
        f"{duration:.3f}",
        "-vf",
        f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,crop={WIDTH}:{HEIGHT},fps={FINAL_FPS},setsar=1,format=yuv420p",
        "-an",
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "18",
        "-r",
        str(FINAL_FPS),
        target,
    ]
    run(cmd, timeout=240)


def ass_time(seconds: float) -> str:
    centis = int(round(seconds * 100))
    hours = centis // 360000
    centis %= 360000
    minutes = centis // 6000
    centis %= 6000
    secs = centis // 100
    centis %= 100
    return f"{hours}:{minutes:02d}:{secs:02d}.{centis:02d}"


def write_subtitles(run_dir: Path, rendered: list[dict[str, Any]]) -> Path:
    ass = run_dir / "subtitles.ass"
    lines = [
        "[Script Info]",
        "ScriptType: v4.00+",
        "PlayResX: 720",
        "PlayResY: 1280",
        "WrapStyle: 2",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        "Style: Title,Microsoft YaHei,40,&H00FFFFFF,&H00FFFFFF,&H99000000,&H77000000,1,0,0,0,100,100,0,0,1,3,1,8,40,40,58,1",
        "Style: Sub,Microsoft YaHei,35,&H00FFFFFF,&H00FFFFFF,&HBB000000,&H88000000,1,0,0,0,100,100,0,0,1,3,1,2,44,44,110,1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    cursor = 0.0
    for item in rendered:
        duration = float(item["target_duration"])
        title = str(item.get("title") or "").strip()
        if title:
            lines.append(f"Dialogue: 0,{ass_time(cursor)},{ass_time(cursor + duration)},Sub,,0,0,0,,{title}")
        cursor += duration
    ass.write_text("\n".join(lines), encoding="utf-8-sig")
    return ass


def concat_videos(inputs: list[Path], output: Path) -> None:
    list_file = output.with_suffix(".concat.txt")
    list_file.write_text(
        "\n".join(f"file '{str(path).replace(chr(39), chr(39) + chr(92) + chr(39) + chr(39))}'" for path in inputs),
        encoding="utf-8",
    )
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_file, "-c", "copy", output], timeout=600)


def assemble_video(run_dir: Path, rendered: list[dict[str, Any]], voiceover: Path | None = None) -> Path:
    normalized: list[Path] = []
    for index, item in enumerate(rendered, start=1):
        source = Path(item["clip"])
        target = run_dir / "clips" / f"{index:02d}_{item['shot_id']}_normalized.mp4"
        normalize_clip(source, target, float(item["target_duration"]))
        normalized.append(target)
    visual = run_dir / "commercial_ktv_visual.mp4"
    concat_videos(normalized, visual)
    ass = write_subtitles(run_dir, rendered)
    final = run_dir / "commercial_ktv_final.mp4"
    ass_filter = str(ass).replace("\\", "/").replace(":", "\\:")
    if voiceover:
        run(
            [
                "ffmpeg",
                "-y",
                "-i",
                visual,
                "-i",
                voiceover,
                "-vf",
                f"subtitles='{ass_filter}'",
                "-map",
                "0:v",
                "-map",
                "1:a",
                "-shortest",
                "-c:v",
                "libx264",
                "-preset",
                "slow",
                "-crf",
                "18",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                final,
            ],
            timeout=900,
        )
    else:
        run(
            [
                "ffmpeg",
                "-y",
                "-i",
                visual,
                "-vf",
                f"subtitles='{ass_filter}'",
                "-c:v",
                "libx264",
                "-preset",
                "slow",
                "-crf",
                "18",
                "-an",
                final,
            ],
            timeout=900,
        )
    return final


def render_contact_sheet(final: Path, output: Path) -> None:
    run(["ffmpeg", "-y", "-i", final, "-vf", "fps=1/4,scale=240:-1,tile=5x3", "-frames:v", "1", output], timeout=120)


def command_doctor(args: argparse.Namespace) -> None:
    report = ensure_comfy_ready()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not report["ok"]:
        raise SystemExit(2)


def command_render(args: argparse.Namespace) -> None:
    report = ensure_comfy_ready()
    if not report["ok"]:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        raise SystemExit(2)
    shots = load_manifest(Path(args.manifest))
    run_dir = make_run_dir(args.label)
    rendered = render_shots(shots, run_dir, timeout=args.timeout)
    final = assemble_video(run_dir, rendered, voiceover=Path(args.voiceover) if args.voiceover else None)
    contact = run_dir / "contact_sheet.jpg"
    render_contact_sheet(final, contact)
    manifest = {
        "run_dir": str(run_dir),
        "final": str(final),
        "contact_sheet": str(contact),
        "shots": rendered,
    }
    (run_dir / "run_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


def command_scene_seed(args: argparse.Namespace) -> None:
    output = Path(args.output) if args.output else make_run_dir(args.label) / "scene_only_virtual_host_seed.jpg"
    make_scene_only_seed(
        Path(args.scene_image),
        output,
        host_scale=args.host_scale,
        x_ratio=args.x_ratio,
        foot_ratio=args.foot_ratio,
    )
    print(json.dumps({"scene_image": args.scene_image, "seed_image": str(output)}, ensure_ascii=False, indent=2))


def command_scene_person_seed(args: argparse.Namespace) -> None:
    output = Path(args.output) if args.output else make_run_dir(args.label) / "scene_person_digital_human_seed.jpg"
    make_scene_person_seed(
        Path(args.scene_image),
        Path(args.person_image),
        output,
        person_height=args.person_height,
        x_ratio=args.x_ratio,
        foot_ratio=args.foot_ratio,
    )
    print(
        json.dumps(
            {"scene_image": args.scene_image, "person_image": args.person_image, "seed_image": str(output)},
            ensure_ascii=False,
            indent=2,
        )
    )


def command_scene_ai_seed(args: argparse.Namespace) -> None:
    scene_image = Path(args.scene_image)
    if not scene_image.exists():
        raise FileNotFoundError(scene_image)
    run_dir = make_run_dir(args.label)
    comfy_name = f"{run_dir.name}_scene_source{scene_image.suffix.lower() or '.jpg'}"
    shutil.copy2(scene_image, COMFY_INPUT / comfy_name)
    positive = (
        "Edit the input luxury KTV private room photo. Preserve the exact room layout, sofa, table, screen, "
        "neon blue and magenta lighting. Add one beautiful fictional AI female host standing naturally near "
        "the sofa and table, full body, elegant black dress, holding a microphone, realistic commercial "
        "photography, integrated shadows and matching lighting, no real person reference, no text, no watermark."
    )
    prompt = flux_kontext_scene_ai_seed_prompt(
        image_name=comfy_name,
        positive=args.prompt or positive,
        prefix=f"{run_dir.name}_scene_ai_virtual_beauty",
        seed=args.seed,
    )
    (run_dir / "scene_ai_seed_prompt.json").write_text(json.dumps(prompt, ensure_ascii=False, indent=2), encoding="utf-8")
    prompt_id = submit_prompt(prompt)
    history = wait_for_prompt_history(prompt_id, timeout=args.timeout)
    (run_dir / "scene_ai_seed_history.json").write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")
    images = saved_images_from_history(history)
    if not images:
        raise RuntimeError(f"Scene AI seed prompt {prompt_id} completed without a saved image.")
    output = Path(args.output) if args.output else run_dir / "scene_ai_virtual_beauty_seed.png"
    shutil.copy2(images[0], output)
    print(
        json.dumps(
            {"scene_image": str(scene_image), "prompt_id": prompt_id, "seed_image": str(output), "run_dir": str(run_dir)},
            ensure_ascii=False,
            indent=2,
        )
    )


def command_export_workflows(args: argparse.Namespace) -> None:
    files = export_workflow_jsons(
        Path(args.output_dir),
        image_name=args.image_name,
        mask_name=args.mask_name,
        sdxl_model_path=args.sdxl_model_path,
        wan_image_name=args.wan_image_name,
    )
    print(json.dumps(files, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Commercial KTV ComfyUI batch video workflow.")
    sub = parser.add_subparsers(dest="command", required=True)
    doctor = sub.add_parser("doctor", help="Check ComfyUI nodes and model files.")
    doctor.set_defaults(func=command_doctor)
    render = sub.add_parser("render", help="Render manifest seed images to a final promo video.")
    render.add_argument("--manifest", required=True, help="CSV with shot_id, seed_image, prompt, duration, seed, title.")
    render.add_argument("--voiceover", help="Optional WAV/MP3 voiceover to mux into the final video.")
    render.add_argument("--label", default="batch", help="Run folder label.")
    render.add_argument("--timeout", type=int, default=2400, help="Seconds to wait for each ComfyUI shot.")
    render.set_defaults(func=command_render)
    seed = sub.add_parser("scene-seed", help="Create a same-scene virtual-host seed image from one KTV scene photo.")
    seed.add_argument("--scene-image", required=True, help="Input KTV scene image.")
    seed.add_argument("--output", help="Output seed image path. Defaults to a new run folder.")
    seed.add_argument("--label", default="scene_seed", help="Run folder label when output is omitted.")
    seed.add_argument("--host-scale", type=float, default=0.78, help="Virtual host scale relative to the 720x1280 canvas.")
    seed.add_argument("--x-ratio", type=float, default=0.53, help="Host center X position as a ratio of canvas width.")
    seed.add_argument("--foot-ratio", type=float, default=0.93, help="Host foot Y position as a ratio of canvas height.")
    seed.set_defaults(func=command_scene_seed)
    person_seed = sub.add_parser("scene-person-seed", help="Create a KTV seed image by compositing a real person into one scene photo.")
    person_seed.add_argument("--scene-image", required=True, help="Input KTV scene image.")
    person_seed.add_argument("--person-image", required=True, help="Input authorized person image.")
    person_seed.add_argument("--output", help="Output seed image path. Defaults to a new run folder.")
    person_seed.add_argument("--label", default="scene_person_seed", help="Run folder label when output is omitted.")
    person_seed.add_argument("--person-height", type=int, default=720, help="Composited person height on the 720x1280 canvas.")
    person_seed.add_argument("--x-ratio", type=float, default=0.52, help="Person center X position as a ratio of canvas width.")
    person_seed.add_argument("--foot-ratio", type=float, default=0.91, help="Person bottom Y position as a ratio of canvas height.")
    person_seed.set_defaults(func=command_scene_person_seed)
    ai_seed = sub.add_parser("scene-ai-seed", help="Use an AI image-edit node to add a fictional virtual beauty into one KTV scene photo.")
    ai_seed.add_argument("--scene-image", required=True, help="Input KTV scene image.")
    ai_seed.add_argument("--output", help="Output generated seed image path.")
    ai_seed.add_argument("--label", default="scene_ai_seed", help="Run folder label.")
    ai_seed.add_argument("--prompt", help="Override the default virtual-host image edit prompt.")
    ai_seed.add_argument("--seed", type=int, default=2026052733, help="Image generation seed.")
    ai_seed.add_argument("--timeout", type=int, default=900, help="Seconds to wait for the image edit.")
    ai_seed.set_defaults(func=command_scene_ai_seed)
    export = sub.add_parser("export-workflows", help="Export real ComfyUI API workflow JSON files.")
    export.add_argument(
        "--output-dir",
        default=r"D:\ai-operations-system\deployment\comfyui\commercial_ktv_workflow",
        help="Directory for exported workflow JSON files.",
    )
    export.add_argument("--image-name", default="scene_sdxl_ai_beauty_480x832.jpg", help="ComfyUI input image filename.")
    export.add_argument("--wan-image-name", help="Optional ComfyUI input image filename for the Wan I2V workflow.")
    export.add_argument("--mask-name", default="scene_virtual_host_mask.png", help="ComfyUI input mask filename.")
    export.add_argument("--sdxl-model-path", default="sdxl_inpaint_1_0", help="ComfyUI DiffusersLoader model path.")
    export.set_defaults(func=command_export_workflows)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
