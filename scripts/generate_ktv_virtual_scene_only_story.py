# -*- coding: utf-8 -*-
"""Generate a Douyin-style virtual-character KTV promo from scene photos only.

This path intentionally does not use the provided portrait/person images.
It builds fictional virtual hosts/singers on top of the supplied KTV scene
photos, animates selected hero frames with Wan2.2 5B TI2V/I2V, and composes a
vertical short video with subtitles and voiceover.
"""

from __future__ import annotations

import asyncio
import json
import math
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
import edge_tts
import numpy as np


ROOT = Path("D:/流程测试")
SCENE_DIR = ROOT / "场景素材"
ASCII_ROOT = Path("D:/aiops_production_runs")
COMFY_ROOT = Path("E:/ComfyUI_cu130/ComfyUI")
COMFY_INPUT = COMFY_ROOT / "input"
COMFY_OUTPUT = COMFY_ROOT / "output"
COMFY_API = "http://127.0.0.1:8188"
CLIENT_ID = f"aiops-virtual-scene-{uuid4()}"

WIDTH = 720
HEIGHT = 1280
FPS = 30

VOICE_TEXT = (
    "这次不做真人探店，人物全部虚拟。"
    "我们只保留店内真实场景，让一个虚拟主理人带你进入今晚的故事。"
    "灯光先亮起来，包房有层次，沙发、屏幕、音响和桌面都准备好。"
    "朋友入座，点歌开始，镜头像手机随手记录，但每一帧都在讲空间的价值。"
    "商务KTV真正打动人的，不只是唱歌，而是把氛围、体面和服务提前安排稳。"
    "曼哈顿商务KTV，你带重要的人来，剩下的交给我们。"
)

SUBTITLE_LINES = [
    (0.0, 3.2, "这次不做真人探店，人物全部虚拟。"),
    (3.2, 8.0, "只保留店内真实场景，让虚拟主理人带你进入今晚的故事。"),
    (8.0, 14.2, "灯光先亮起来，包房有层次，屏幕、音响和桌面都准备好。"),
    (14.2, 21.5, "朋友入座，点歌开始，镜头像手机随手记录。"),
    (21.5, 29.0, "商务KTV真正打动人的，不只是唱歌，是氛围、体面和服务。"),
    (29.0, 36.5, "曼哈顿商务KTV，你带重要的人来，剩下的交给我们。"),
]

NEGATIVE_PROMPT = (
    "real person reference, celebrity, face from photo, ugly, low quality, blurry, jitter, "
    "flicker, extra limbs, bad hands, missing legs, cropped head, duplicate person, watermark, "
    "logo, subtitles, text overlay, deformed body, distorted face, plastic skin"
)


@dataclass(frozen=True)
class SceneAsset:
    source_name: str
    path: Path


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


def imread(path: Path) -> np.ndarray:
    data = np.fromfile(str(path), dtype=np.uint8)
    image = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if image is None:
        raise RuntimeError(f"Cannot read image: {path}")
    return image


def imwrite(path: Path, image: np.ndarray, quality: int = 94) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    params = [cv2.IMWRITE_JPEG_QUALITY, quality] if path.suffix.lower() in {".jpg", ".jpeg"} else []
    ok, buffer = cv2.imencode(path.suffix, image, params)
    if not ok:
        raise RuntimeError(f"Cannot write image: {path}")
    buffer.tofile(str(path))


def make_run_dirs() -> tuple[str, Path, Path]:
    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    run_dir = ASCII_ROOT / f"ktv_virtual_scene_style_{stamp}"
    mirror_dir = ROOT / "_aiops_virtual_scene_style" / f"ktv_virtual_scene_style_{stamp}"
    run_dir.mkdir(parents=True, exist_ok=True)
    mirror_dir.mkdir(parents=True, exist_ok=True)
    return stamp, run_dir, mirror_dir


def scene_sort_key(path: Path) -> tuple[int, str]:
    stem = path.stem
    return (int(stem) if stem.isdigit() else 9999, path.name)


def copy_scene_photos(run_dir: Path) -> list[SceneAsset]:
    raw_dir = run_dir / "raw_scene_photos"
    raw_dir.mkdir(parents=True, exist_ok=True)
    assets: list[SceneAsset] = []
    for index, source in enumerate(sorted(SCENE_DIR.glob("*.*"), key=scene_sort_key), start=1):
        if source.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
            continue
        target = raw_dir / f"scene_photo_{index:02d}.jpg"
        image = imread(source)
        imwrite(target, image, quality=96)
        assets.append(SceneAsset(source.name, target))
    if len(assets) < 4:
        raise RuntimeError("At least four scene photos are recommended for this virtual style.")
    return assets


def cover_resize(image: np.ndarray, width: int = WIDTH, height: int = HEIGHT) -> np.ndarray:
    src_h, src_w = image.shape[:2]
    scale = max(width / src_w, height / src_h)
    resized = cv2.resize(image, (math.ceil(src_w * scale), math.ceil(src_h * scale)), interpolation=cv2.INTER_AREA)
    h, w = resized.shape[:2]
    x = max(0, (w - width) // 2)
    y = max(0, (h - height) // 2)
    return resized[y : y + height, x : x + width].copy()


def add_soft_vignette(image: np.ndarray) -> np.ndarray:
    h, w = image.shape[:2]
    y = np.linspace(-1.0, 1.0, h, dtype=np.float32)[:, None]
    x = np.linspace(-1.0, 1.0, w, dtype=np.float32)[None, :]
    mask = np.clip(1.0 - (x * x + y * y) * 0.32, 0.55, 1.0)
    out = image.astype(np.float32) * mask[:, :, None]
    return np.clip(out, 0, 255).astype(np.uint8)


def alpha_composite(base: np.ndarray, overlay: np.ndarray, x: int, y: int) -> None:
    h, w = overlay.shape[:2]
    x1, y1 = max(0, x), max(0, y)
    x2, y2 = min(base.shape[1], x + w), min(base.shape[0], y + h)
    if x1 >= x2 or y1 >= y2:
        return
    ox1, oy1 = x1 - x, y1 - y
    roi = base[y1:y2, x1:x2]
    patch = overlay[oy1 : oy1 + (y2 - y1), ox1 : ox1 + (x2 - x1)]
    alpha = patch[:, :, 3:4].astype(np.float32) / 255.0
    roi[:] = (patch[:, :, :3].astype(np.float32) * alpha + roi.astype(np.float32) * (1 - alpha)).astype(np.uint8)


def draw_virtual_actor(
    *,
    scale: float,
    phase: float,
    pose: str,
    outfit: str,
    skin: tuple[int, int, int] = (176, 132, 105),
) -> np.ndarray:
    """Draw a fictional full-body virtual host/singer as BGRA."""

    canvas_h = int(900 * scale)
    canvas_w = int(360 * scale)
    supersample = 2
    img = np.zeros((canvas_h * supersample, canvas_w * supersample, 4), dtype=np.uint8)
    s = scale * supersample
    cx = canvas_w * supersample // 2
    bob = int(math.sin(phase) * 7 * s)

    def p(x: float, y: float) -> tuple[int, int]:
        return int(cx + x * s), int((y + bob) * s)

    def poly(points: list[tuple[float, float]], color: tuple[int, int, int, int]) -> None:
        cv2.fillPoly(img, [np.array([p(x, y) for x, y in points], np.int32)], color, cv2.LINE_AA)

    def line(a: tuple[float, float], b: tuple[float, float], color: tuple[int, int, int, int], thickness: float) -> None:
        cv2.line(img, p(*a), p(*b), color, max(1, int(thickness * s)), cv2.LINE_AA)

    def ellipse(center: tuple[float, float], axes: tuple[float, float], color: tuple[int, int, int, int], angle: float = 0) -> None:
        cv2.ellipse(img, p(*center), (int(axes[0] * s), int(axes[1] * s)), angle, 0, 360, color, -1, cv2.LINE_AA)

    skin_bgra = (*skin, 255)
    hair = (19, 18, 23, 255)
    black = (20, 20, 27, 255)
    white = (232, 229, 218, 255)
    magenta = (224, 52, 190, 255)
    cyan = (245, 175, 30, 255)

    # Legs and shoes.
    poly([(-55, 545), (-22, 545), (-26, 762), (-60, 762)], skin_bgra)
    poly([(24, 545), (57, 545), (68, 762), (33, 762)], skin_bgra)
    ellipse((-42, 780), (44, 13), black, -8)
    ellipse((53, 780), (44, 13), black, 8)

    # Outfit.
    if outfit == "singer":
        poly([(-86, 232), (88, 232), (118, 548), (48, 580), (-44, 580), (-118, 548)], (28, 26, 34, 255))
        poly([(-48, 246), (46, 246), (28, 418), (-18, 418)], (42, 38, 48, 255))
        for dx in [-68, -36, 0, 34, 64]:
            line((dx, 260), (dx * 0.45, 560), (95, 64, 115, 210), 1.2)
    else:
        poly([(-74, 252), (78, 252), (92, 420), (-88, 420)], black)
        poly([(-46, 258), (42, 258), (28, 420), (-28, 420)], white)
        poly([(-92, 420), (96, 420), (122, 560), (-116, 560)], black)
        line((-34, 290), (-34, 402), magenta, 2.0)
        line((32, 290), (32, 402), cyan, 2.0)

    # Arms with mic / gesture.
    left_wave = math.sin(phase) * 13
    right_wave = math.cos(phase * 0.9) * 8
    if pose == "sing":
        line((-78, 280), (-108, 360 + left_wave), skin_bgra, 19)
        line((-108, 360 + left_wave), (-68, 442), skin_bgra, 17)
        line((78, 280), (106, 358 + right_wave), skin_bgra, 19)
        line((106, 358 + right_wave), (78, 430), skin_bgra, 17)
        line((78, 430), (54, 310), (36, 34, 40, 255), 7)
        ellipse((54, 300), (17, 22), (38, 38, 45, 255), -12)
    else:
        line((-78, 282), (-106, 388 + left_wave), skin_bgra, 19)
        line((-106, 388 + left_wave), (-73, 486), skin_bgra, 17)
        line((78, 282), (126, 348 + right_wave), skin_bgra, 19)
        line((126, 348 + right_wave), (146, 300 + right_wave), skin_bgra, 15)
        ellipse((149, 292 + right_wave), (17, 17), skin_bgra)

    # Neck, head, hair.
    ellipse((0, 225), (28, 36), skin_bgra)
    ellipse((0, 138), (74, 92), hair)
    ellipse((0, 145), (58, 72), skin_bgra)
    poly([(-70, 134), (-28, 76), (52, 78), (82, 178), (62, 266), (38, 248), (52, 166)], hair)
    poly([(-68, 154), (-92, 278), (-48, 270), (-38, 176)], hair)

    # Face details.
    ellipse((-22, 142), (7, 4), (20, 18, 24, 255))
    ellipse((23, 142), (7, 4), (20, 18, 24, 255))
    line((-35, 128), (-11, 126), (36, 28, 30, 255), 1.4)
    line((11, 126), (35, 128), (36, 28, 30, 255), 1.4)
    mouth_open = 1.0 if pose == "sing" else 0.45
    ellipse((0, 180), (16, 5 + 8 * mouth_open), (112, 46, 66, 255))
    ellipse((-55, 164), (10, 16), (72, 210, 244, 255))
    ellipse((55, 164), (10, 16), (72, 210, 244, 255))

    # Synthetic rim light makes the character read like AI animation.
    alpha = img[:, :, 3]
    kernel = np.ones((7, 7), np.uint8)
    outline = cv2.dilate(alpha, kernel, iterations=1) - alpha
    rim = np.zeros_like(img)
    rim[:, :, 0] = 255
    rim[:, :, 1] = 80
    rim[:, :, 2] = 210
    rim[:, :, 3] = np.clip(outline * 0.55, 0, 140).astype(np.uint8)
    out = np.zeros_like(img)
    alpha_composite(out[:, :, :3], rim, 0, 0) if False else None
    combined = rim.copy()
    alpha_composite(combined[:, :, :3], img, 0, 0) if False else None

    # Manual composite rim + actor in BGRA.
    final = rim.astype(np.float32)
    a = img[:, :, 3:4].astype(np.float32) / 255.0
    final[:, :, :3] = img[:, :, :3].astype(np.float32) * a + final[:, :, :3] * (1 - a)
    final[:, :, 3:4] = np.maximum(final[:, :, 3:4], img[:, :, 3:4])
    final = np.clip(final, 0, 255).astype(np.uint8)
    return cv2.resize(final, (canvas_w, canvas_h), interpolation=cv2.INTER_AREA)


def draw_virtual_guests(base: np.ndarray, phase: float) -> None:
    positions = [(215, 820, 0.82), (500, 835, 0.78), (610, 785, 0.65)]
    for i, (x, y, scale) in enumerate(positions):
        sway = math.sin(phase + i) * 8
        actor = draw_virtual_actor(scale=scale, phase=phase + i, pose="sing" if i == 1 else "host", outfit="singer")
        alpha_composite(base, actor, int(x - actor.shape[1] / 2 + sway), int(y - actor.shape[0] * 0.72))


def render_seed_image(scene: Path, output: Path, *, variant: str, title: str = "") -> Path:
    frame = cover_resize(imread(scene))
    frame = add_soft_vignette(frame)
    wash = np.full_like(frame, (14, 2, 16), dtype=np.uint8)
    frame = cv2.addWeighted(frame, 0.9, wash, 0.1, 0)

    if variant == "host":
        actor = draw_virtual_actor(scale=1.0, phase=0.3, pose="host", outfit="host")
        alpha_composite(frame, actor, 360 - actor.shape[1] // 2, 1110 - actor.shape[0])
    elif variant == "singer":
        actor = draw_virtual_actor(scale=1.05, phase=1.1, pose="sing", outfit="singer")
        alpha_composite(frame, actor, 360 - actor.shape[1] // 2, 1130 - actor.shape[0])
    elif variant == "guests":
        draw_virtual_guests(frame, 0.8)
    else:
        actor = draw_virtual_actor(scale=0.82, phase=0.7, pose="host", outfit="host")
        alpha_composite(frame, actor, 515 - actor.shape[1] // 2, 1120 - actor.shape[0])

    imwrite(output, frame, quality=96)
    return output


def make_procedural_clip(scene: Path, output: Path, *, variant: str, duration: float) -> Path:
    frames_dir = output.parent / f"{output.stem}_frames"
    if frames_dir.exists():
        shutil.rmtree(frames_dir)
    frames_dir.mkdir(parents=True)
    bg0 = cover_resize(imread(scene))
    total = int(round(duration * FPS))
    for index in range(total):
        phase = index / max(1, total - 1) * math.tau
        zoom = 1.0 + 0.018 * index / max(1, total - 1)
        h, w = bg0.shape[:2]
        z_w, z_h = int(w / zoom), int(h / zoom)
        x0 = (w - z_w) // 2 + int(math.sin(phase * 0.5) * 10)
        y0 = (h - z_h) // 2 + int(math.cos(phase * 0.45) * 8)
        x0 = max(0, min(w - z_w, x0))
        y0 = max(0, min(h - z_h, y0))
        frame = cv2.resize(bg0[y0 : y0 + z_h, x0 : x0 + z_w], (WIDTH, HEIGHT), interpolation=cv2.INTER_CUBIC)
        frame = add_soft_vignette(frame)

        if variant == "guests":
            draw_virtual_guests(frame, phase)
        elif variant == "singer":
            actor = draw_virtual_actor(scale=1.02, phase=phase, pose="sing", outfit="singer")
            alpha_composite(frame, actor, 360 - actor.shape[1] // 2, 1130 - actor.shape[0])
        elif variant == "side":
            actor = draw_virtual_actor(scale=0.78, phase=phase, pose="host", outfit="host")
            alpha_composite(frame, actor, 520 - actor.shape[1] // 2, 1110 - actor.shape[0])
        else:
            actor = draw_virtual_actor(scale=0.96, phase=phase, pose="host", outfit="host")
            alpha_composite(frame, actor, 360 - actor.shape[1] // 2, 1115 - actor.shape[0])

        imwrite(frames_dir / f"frame_{index:04d}.jpg", frame, quality=94)

    run(
        [
            "ffmpeg",
            "-y",
            "-framerate",
            str(FPS),
            "-i",
            frames_dir / "frame_%04d.jpg",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-preset",
            "medium",
            "-crf",
            "17",
            "-r",
            str(FPS),
            output,
        ],
        timeout=240,
    )
    return output


def make_looped_video(source: Path, output: Path, duration: float) -> Path:
    vf = f"fps={FPS},scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,crop={WIDTH}:{HEIGHT},setsar=1,format=yuv420p"
    cmd = ["ffmpeg", "-y"]
    if ffprobe_duration(source) < duration - 0.1:
        cmd += ["-stream_loop", "-1"]
    cmd += [
        "-i",
        source,
        "-t",
        f"{duration:.3f}",
        "-vf",
        vf,
        "-an",
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "17",
        "-r",
        str(FPS),
        output,
    ]
    run(cmd, timeout=240)
    return output


def resize_for_comfy(source: Path, output: Path) -> None:
    frame = cv2.resize(cover_resize(imread(source), 480, 832), (480, 832), interpolation=cv2.INTER_AREA)
    imwrite(output, frame, quality=96)


def wan_5b_i2v_prompt(image_name: str, prefix: str, positive: str, seed: int) -> dict[str, Any]:
    return {
        "1": {"class_type": "LoadImage", "inputs": {"image": image_name}},
        "2": {
            "class_type": "WanVideoVAELoader",
            "inputs": {"model_name": "wan2.2_vae.safetensors", "precision": "bf16", "use_cpu_cache": False, "verbose": False},
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
                "noise_aug_strength": 0.02,
                "latent_strength": 0.92,
            },
        },
        "4": {"class_type": "WanVideoEmptyEmbeds", "inputs": {"width": 480, "height": 832, "num_frames": 33, "extra_latents": ["3", 0]}},
        "5": {
            "class_type": "WanVideoTextEncodeCached",
            "inputs": {
                "model_name": "umt5-xxl-enc-bf16.safetensors",
                "precision": "bf16",
                "positive_prompt": positive,
                "negative_prompt": NEGATIVE_PROMPT,
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
                "model": "Wan2.2\\wan2.2_ti2v_5B_fp16.safetensors",
                "base_precision": "fp16_fast",
                "quantization": "disabled",
                "load_device": "offload_device",
                "attention_mode": "sdpa",
                "block_swap_args": ["6", 0],
                "rms_norm_function": "default",
            },
        },
        "8": {"class_type": "WanVideoEasyCache", "inputs": {"easycache_thresh": 0.015, "start_step": 8, "end_step": -1, "cache_device": "offload_device"}},
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
                "frame_rate": 16,
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


def wait_for_history(prompt_id: str, timeout: int = 2400) -> dict[str, Any]:
    start = time.time()
    while time.time() - start < timeout:
        try:
            result = http_json("GET", f"/history/{prompt_id}", timeout=180)
        except Exception as exc:
            print(f"[comfy] poll retry after {type(exc).__name__}: {exc}", flush=True)
            time.sleep(10)
            continue
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


def newest_output(prefix: str, after: float) -> Path:
    candidates = [path for path in COMFY_OUTPUT.glob(f"{prefix}*.mp4") if path.stat().st_mtime >= after]
    if not candidates:
        raise RuntimeError(f"No ComfyUI mp4 output found for prefix {prefix}")
    return sorted(candidates, key=lambda p: p.stat().st_mtime, reverse=True)[0]


def generate_ai_clip(run_dir: Path, seed_image: Path, *, role: str, prefix: str, seed: int) -> Path | None:
    try:
        http_json("GET", "/system_stats", timeout=10)
    except Exception as exc:
        print(f"[comfy] unavailable, using procedural fallback: {exc}", flush=True)
        return None

    comfy_image = run_dir / "comfy_inputs" / f"{seed_image.stem}_480x832.jpg"
    comfy_image.parent.mkdir(parents=True, exist_ok=True)
    resize_for_comfy(seed_image, comfy_image)
    shutil.copy2(comfy_image, COMFY_INPUT / comfy_image.name)
    positive = (
        f"Douyin AI original animation style, fictional virtual {role} in a luxury business KTV room, "
        "full body, not based on any real person, expressive singing and speaking, subtle camera movement, "
        "neon cyan magenta lighting, polished AI-generated vertical short video, smooth motion, cinematic but social-media style"
    )
    prompt = wan_5b_i2v_prompt(comfy_image.name, prefix, positive, seed)
    (run_dir / f"{prefix}_prompt.json").write_text(json.dumps(prompt, ensure_ascii=False, indent=2), encoding="utf-8")
    start = time.time()
    prompt_id = submit_prompt(prompt)
    print(f"[comfy] {prefix} prompt_id={prompt_id}", flush=True)
    history = wait_for_history(prompt_id)
    (run_dir / f"{prefix}_history.json").write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")
    output = newest_output(prefix, after=start - 2)
    target = run_dir / f"{prefix}.mp4"
    shutil.copy2(output, target)
    return target


def xfade_sequence(inputs: list[Path], output: Path, *, overlap: float) -> Path:
    if len(inputs) == 1:
        shutil.copy2(inputs[0], output)
        return output
    durations = [ffprobe_duration(path) for path in inputs]
    cmd: list[str | Path] = ["ffmpeg", "-y"]
    for path in inputs:
        cmd += ["-i", path]
    filters: list[str] = []
    current = "0:v"
    accumulated = durations[0]
    final_label = current
    for index in range(1, len(inputs)):
        label = f"v{index}"
        offset = max(0.05, accumulated - overlap)
        filters.append(
            f"[{current}][{index}:v]xfade=transition=fade:duration={overlap:.3f}:offset={offset:.3f},format=yuv420p[{label}]"
        )
        accumulated += durations[index] - overlap
        current = label
        final_label = label
    run(
        [
            *cmd,
            "-filter_complex",
            ";".join(filters),
            "-map",
            f"[{final_label}]",
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "slow",
            "-crf",
            "17",
            output,
        ],
        timeout=900,
    )
    return output


def ass_time(seconds: float) -> str:
    cs = int(round(seconds * 100))
    h = cs // 360000
    cs %= 360000
    m = cs // 6000
    cs %= 6000
    s = cs // 100
    c = cs % 100
    return f"{h}:{m:02d}:{s:02d}.{c:02d}"


def create_subtitles(run_dir: Path, duration: float) -> Path:
    ass = run_dir / "virtual_scene_subtitles.ass"
    lines = [
        "[Script Info]",
        "ScriptType: v4.00+",
        "PlayResX: 720",
        "PlayResY: 1280",
        "WrapStyle: 2",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        "Style: Title,Microsoft YaHei,38,&H00FFFFFF,&H00FFFFFF,&H77000000,&H55000000,1,0,0,0,100,100,0,0,1,2,1,8,42,42,58,1",
        "Style: Sub,Microsoft YaHei,36,&H00FFFFFF,&H00FFFFFF,&HBB000000,&H77000000,1,0,0,0,100,100,0,0,1,3,1,2,44,44,112,1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
        f"Dialogue: 0,{ass_time(0)},{ass_time(min(duration, 7.0))},Title,,0,0,0,,AI原创动画 | 曼哈顿商务KTV",
    ]
    for start, end, text in SUBTITLE_LINES:
        lines.append(f"Dialogue: 1,{ass_time(start)},{ass_time(min(end, duration))},Sub,,0,0,0,,{text}")
    ass.write_text("\n".join(lines), encoding="utf-8")
    return ass


async def generate_voice(run_dir: Path) -> tuple[Path, Path]:
    text_path = run_dir / "virtual_scene_voiceover.txt"
    mp3_path = run_dir / "virtual_scene_voiceover_edge.mp3"
    wav_path = run_dir / "virtual_scene_voiceover.wav"
    text_path.write_text(VOICE_TEXT, encoding="utf-8")
    communicate = edge_tts.Communicate(VOICE_TEXT, voice="zh-CN-XiaoxiaoNeural", rate="-3%", pitch="-2Hz")
    await communicate.save(str(mp3_path))
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            mp3_path,
            "-af",
            "aresample=44100,volume=1.03,loudnorm=I=-17:TP=-1.5:LRA=9",
            "-ar",
            "44100",
            "-ac",
            "2",
            wav_path,
        ],
        timeout=180,
    )
    return text_path, wav_path


def make_audio_mix(run_dir: Path, voice_wav: Path, duration: float) -> Path:
    bed = run_dir / "virtual_scene_music_bed.wav"
    audio = run_dir / "virtual_scene_audio_mix.wav"
    run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            f"anoisesrc=color=pink:amplitude=0.020:d={duration:.3f}",
            "-f",
            "lavfi",
            "-i",
            f"sine=frequency=116:sample_rate=44100:duration={duration:.3f}",
            "-filter_complex",
            "[0:a]lowpass=f=2500,volume=0.20[a0];[1:a]volume=0.018[a1];[a0][a1]amix=inputs=2:duration=longest,afade=t=in:st=0:d=0.7,afade=t=out:st="
            + f"{max(0.0, duration - 1.7):.3f}:d=1.7",
            "-ar",
            "44100",
            "-ac",
            "2",
            bed,
        ],
        timeout=120,
    )
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            voice_wav,
            "-i",
            bed,
            "-filter_complex",
            f"[0:a]volume=1.0,apad[a0];[1:a]volume=0.36[a1];[a0][a1]amix=inputs=2:duration=longest,atrim=0:{duration:.3f},acompressor=threshold=-17dB:ratio=1.8:attack=15:release=160,loudnorm=I=-16:TP=-1.5:LRA=9",
            "-ar",
            "44100",
            "-ac",
            "2",
            audio,
        ],
        timeout=180,
    )
    return audio


def burn_final(run_dir: Path, visual: Path, audio: Path, ass: Path) -> Path:
    final = run_dir / "business_ktv_virtual_scene_ai_animation.mp4"
    duration = ffprobe_duration(visual)
    ass_filter = str(ass).replace("\\", "/").replace(":", "\\:")
    vf = f"subtitles='{ass_filter}',fade=t=out:st={max(0.0, duration - 1.2):.3f}:d=1.2"
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            visual,
            "-i",
            audio,
            "-vf",
            vf,
            "-map",
            "0:v",
            "-map",
            "1:a",
            "-c:v",
            "libx264",
            "-preset",
            "slow",
            "-crf",
            "17",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-t",
            f"{duration:.3f}",
            final,
        ],
        timeout=900,
    )
    return final


def make_preview(run_dir: Path, final: Path) -> tuple[Path, Path]:
    preview = run_dir / "virtual_scene_preview_sheet.jpg"
    contact = run_dir / "virtual_scene_contact_sheet.jpg"
    run(
        ["ffmpeg", "-y", "-i", final, "-vf", "fps=1/4,scale=240:-1,tile=5x3", "-frames:v", "1", contact],
        timeout=120,
    )
    run(
        ["ffmpeg", "-y", "-i", final, "-vf", "fps=1/5,scale=240:-1,tile=5x2", "-frames:v", "1", preview],
        timeout=120,
    )
    return preview, contact


def write_storyboard(run_dir: Path, scene_manifest: list[dict[str, Any]], final: Path, preview: Path) -> Path:
    storyboard = run_dir / "virtual_scene_storyboard.md"
    text = f"""# 场景照片生成虚拟人物 AI 动画

## 风格定位

参考抖音 AI 原创动画方向：竖屏、真实 KTV 场景照片、完全虚拟人物、强字幕、短视频节奏。

## 本版规则

- 不使用 `人物画像`，人物完全虚拟。
- 只读取 `D:\\流程测试\\场景素材` 里的照片作为场景来源。
- 用 Wan2.2 5B TI2V/I2V 生成部分 AI 动效，其余镜头用虚拟人物程序动效补足节奏。

## 输出

- 成片：`{final}`
- 预览：`{preview}`

## 分镜

"""
    for item in scene_manifest:
        text += f"- {item['index']:02d}. {item['name']} ({item['kind']}), {item['duration']:.2f}s\n"
    storyboard.write_text(text, encoding="utf-8")
    return storyboard


def mirror_outputs(mirror_dir: Path, files: list[Path]) -> list[Path]:
    mirror_dir.mkdir(parents=True, exist_ok=True)
    mirrored: list[Path] = []
    for path in files:
        target = mirror_dir / path.name
        shutil.copy2(path, target)
        mirrored.append(target)
    return mirrored


async def main() -> None:
    stamp, run_dir, mirror_dir = make_run_dirs()
    print(f"[run] {stamp} {run_dir}", flush=True)
    scene_assets = copy_scene_photos(run_dir)
    seed_dir = run_dir / "seed_images"
    seed_dir.mkdir(parents=True, exist_ok=True)
    scene_paths = [asset.path for asset in scene_assets]

    host_seed = render_seed_image(scene_paths[8 if len(scene_paths) > 8 else -1], seed_dir / "seed_virtual_host.jpg", variant="host")
    singer_seed = render_seed_image(scene_paths[6 if len(scene_paths) > 6 else 0], seed_dir / "seed_virtual_singer.jpg", variant="singer")
    guests_seed = render_seed_image(scene_paths[0], seed_dir / "seed_virtual_guests.jpg", variant="guests")

    ai_host = generate_ai_clip(run_dir, host_seed, role="female KTV host", prefix="aiops_virtual_host_i2v", seed=2026052707)
    ai_singer = generate_ai_clip(run_dir, singer_seed, role="female virtual singer", prefix="aiops_virtual_singer_i2v", seed=2026052708)

    scenes_dir = run_dir / "scenes"
    scenes_dir.mkdir(parents=True, exist_ok=True)
    specs: list[tuple[str, Path, str, float, str]] = [
        ("01_virtual_host_open", ai_host or host_seed, "ai_i2v" if ai_host else "procedural_seed", 4.4, "host"),
        ("02_virtual_room_story", scene_paths[0], "procedural", 4.2, "guests"),
        ("03_virtual_singer", ai_singer or singer_seed, "ai_i2v" if ai_singer else "procedural_seed", 4.4, "singer"),
        ("04_private_room_guests", scene_paths[2 if len(scene_paths) > 2 else 0], "procedural", 4.0, "guests"),
        ("05_equipment_check", scene_paths[8 if len(scene_paths) > 8 else -1], "procedural", 3.8, "side"),
        ("06_big_room_sing", scene_paths[-1], "procedural", 4.2, "singer"),
        ("07_scene_scale", scene_paths[6 if len(scene_paths) > 6 else 0], "procedural", 4.0, "host"),
        ("08_virtual_host_close", ai_host or host_seed, "ai_i2v_reprise" if ai_host else "procedural_seed", 4.3, "host"),
    ]

    clips: list[Path] = []
    manifest: list[dict[str, Any]] = []
    for index, (name, source, kind, duration, variant) in enumerate(specs, start=1):
        output = scenes_dir / f"{index:02d}_{name}.mp4"
        if source.suffix.lower() in {".mp4", ".mov", ".m4v"}:
            make_looped_video(source, output, duration)
        else:
            make_procedural_clip(source, output, variant=variant, duration=duration)
        clips.append(output)
        manifest.append(
            {
                "index": index,
                "name": name,
                "kind": kind,
                "source": str(source),
                "output": str(output),
                "duration": ffprobe_duration(output),
            }
        )

    visual = run_dir / "virtual_scene_visual_xfade.mp4"
    xfade_sequence(clips, visual, overlap=0.42)
    visual_duration = ffprobe_duration(visual)
    text_path, voice_wav = await generate_voice(run_dir)
    ass = create_subtitles(run_dir, visual_duration)
    audio = make_audio_mix(run_dir, voice_wav, visual_duration)
    final = burn_final(run_dir, visual, audio, ass)
    preview, contact = make_preview(run_dir, final)
    storyboard = write_storyboard(run_dir, manifest, final, preview)
    manifest_path = run_dir / "virtual_scene_manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "stamp": stamp,
                "run_dir": str(run_dir),
                "mirror_dir": str(mirror_dir),
                "source_scene_dir": str(SCENE_DIR),
                "portrait_usage": "not used",
                "voiceover_script": str(text_path),
                "visual": str(visual),
                "audio": str(audio),
                "subtitles": str(ass),
                "final": str(final),
                "preview": str(preview),
                "contact_sheet": str(contact),
                "storyboard": str(storyboard),
                "seed_images": [str(host_seed), str(singer_seed), str(guests_seed)],
                "ai_clips": [str(path) for path in [ai_host, ai_singer] if path],
                "scene_manifest": manifest,
                "limitations": [
                    "人物为完全虚拟，不基于用户人物照片。",
                    "当前版本用场景照片和虚拟角色合成，再用 Wan2.2 5B 做部分动效。",
                    "如需更接近参考号的商业级人物一致性，建议后续接入虚拟人物 LoRA 或固定角色模型。",
                ],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    mirrored = mirror_outputs(mirror_dir, [final, preview, contact, storyboard, manifest_path, ass, host_seed, singer_seed, guests_seed])
    print(
        json.dumps(
            {
                "final": str(final),
                "preview": str(preview),
                "contact": str(contact),
                "mirror": [str(path) for path in mirrored],
                "duration": visual_duration,
            },
            ensure_ascii=False,
            indent=2,
        ),
        flush=True,
    )


if __name__ == "__main__":
    asyncio.run(main())
