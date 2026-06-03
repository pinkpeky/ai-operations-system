"""Generate a full-body-owner KTV story promo from D:/流程测试.

This pipeline is for the current material set:
- half-body portrait images under D:/流程测试/人物画像
- supplemented KTV scene images/videos under D:/流程测试/场景素材
- reference-vlog style under D:/流程测试/参考视频

It creates a full-body proxy reference from the half-body portrait, drives a
short Wan2.2 5B I2V host shot, then composes that with real scene material
into a smooth vertical story video.
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
PORTRAIT_DIR = ROOT / "人物画像"
SCENE_DIR = ROOT / "场景素材"
REFERENCE_DIR = ROOT / "参考视频"
ASCII_ROOT = Path("D:/aiops_production_runs")
COMFY_ROOT = Path("E:/ComfyUI_cu130/ComfyUI")
COMFY_INPUT = COMFY_ROOT / "input"
COMFY_OUTPUT = COMFY_ROOT / "output"
COMFY_API = "http://127.0.0.1:8188"
YOLO_SEG_MODEL = COMFY_ROOT / "models" / "ultralytics" / "segm" / "yolov8n-seg.pt"
CLIENT_ID = f"aiops-fullbody-ktv-{uuid4()}"

WIDTH = 720
HEIGHT = 1280
FPS = 30

VOICE_TEXT = (
    "很多人第一次看商务KTV，只会看灯光和装修。"
    "但真正决定客户愿不愿意再来，是进门这一刻的秩序感。"
    "今天我带你走一遍。先看大厅，灯光够亮，动线够清楚，接待不用慌。"
    "再往里走，是包房区。每一间房的屏幕、音响、沙发和桌面，都要提前检查。"
    "商务接待最怕临场解释太多。好的空间，是客人一坐下，就知道今晚安排得很稳。"
    "这里不是单纯唱歌，是把氛围、体面和服务一起准备好。"
    "你带重要的人来，剩下的交给我们。"
)

SUBTITLE_LINES = [
    (0.0, 3.5, "很多人第一次看商务KTV，只会看灯光和装修。"),
    (3.5, 8.4, "真正决定客户愿不愿意再来，是进门这一刻的秩序感。"),
    (8.4, 14.8, "今天我带你走一遍：大厅、灯光、动线，接待不能慌。"),
    (14.8, 22.0, "再往里走，是包房区。屏幕、音响、沙发和桌面，都要提前检查。"),
    (22.0, 29.2, "商务接待最怕临场解释太多。好的空间，一坐下就知道安排得很稳。"),
    (29.2, 35.5, "这里不是单纯唱歌，是把氛围、体面和服务一起准备好。"),
    (35.5, 47.0, "你带重要的人来，剩下的交给我们。"),
]

NEGATIVE_PROMPT = (
    "raw montage, talking head only, close-up-only avatar, identity drift, face swap, "
    "different clothes, deformed face, bad hands, extra fingers, extra limbs, duplicate person, "
    "low quality, blurry, flicker, jitter, subtitles, watermark, logo, overexposed, "
    "oversaturated, cartoon, anime, plastic skin, warped background, three legs"
)


@dataclass(frozen=True)
class RenderAsset:
    name: str
    path: Path
    kind: str


def run(cmd: list[str], *, cwd: Path | None = None, timeout: int | None = None) -> None:
    print("[cmd]", " ".join(str(part) for part in cmd), flush=True)
    subprocess.run(cmd, cwd=str(cwd) if cwd else None, check=True, timeout=timeout)


def capture(cmd: list[str], *, timeout: int | None = None) -> str:
    return subprocess.check_output(cmd, text=True, encoding="utf-8", errors="replace", timeout=timeout)


def http_json(method: str, path: str, payload: dict[str, Any] | None = None, timeout: int = 30) -> dict[str, Any]:
    data = None
    headers = {"Content-Type": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(f"{COMFY_API}{path}", data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as response:
        body = response.read().decode("utf-8")
    return json.loads(body) if body else {}


def ffprobe_duration(path: Path) -> float:
    output = capture(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        timeout=60,
    ).strip()
    return float(output)


def make_run_dirs() -> tuple[str, Path, Path]:
    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    run_dir = ASCII_ROOT / f"ktv_fullbody_story_{stamp}"
    mirror_dir = ROOT / "_aiops_fullbody_story" / f"ktv_fullbody_story_{stamp}"
    run_dir.mkdir(parents=True, exist_ok=True)
    mirror_dir.mkdir(parents=True, exist_ok=True)
    return stamp, run_dir, mirror_dir


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


def orient_portrait(image: np.ndarray) -> np.ndarray:
    height, width = image.shape[:2]
    if width > height:
        return cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    return image


def copy_source_assets(run_dir: Path) -> dict[str, list[RenderAsset]]:
    raw_dir = run_dir / "raw_assets"
    portrait_out = raw_dir / "portraits"
    scene_out = raw_dir / "scenes"
    portrait_out.mkdir(parents=True, exist_ok=True)
    scene_out.mkdir(parents=True, exist_ok=True)

    portraits: list[RenderAsset] = []
    for index, source in enumerate(sorted(PORTRAIT_DIR.glob("*.*")), start=1):
        if source.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
            continue
        target = portrait_out / f"portrait_{index:02d}.jpg"
        image = orient_portrait(imread(source))
        imwrite(target, image)
        portraits.append(RenderAsset(source.stem, target, "portrait"))

    scene_images: list[RenderAsset] = []
    scene_videos: list[RenderAsset] = []
    for source in sorted(SCENE_DIR.glob("*.*"), key=lambda p: p.name):
        suffix = source.suffix.lower()
        if suffix in {".jpg", ".jpeg", ".png", ".webp"}:
            target = scene_out / f"scene_img_{len(scene_images) + 1:02d}.jpg"
            shutil.copy2(source, target)
            scene_images.append(RenderAsset(source.stem, target, "scene_image"))
        elif suffix in {".mp4", ".mov", ".m4v"}:
            target = scene_out / f"scene_vid_{len(scene_videos) + 1:02d}.mp4"
            shutil.copy2(source, target)
            scene_videos.append(RenderAsset(source.stem, target, "scene_video"))

    return {"portraits": portraits, "scene_images": scene_images, "scene_videos": scene_videos}


def detect_face_crop(image: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cascade = cv2.CascadeClassifier(str(Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"))
    faces = cascade.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=5, minSize=(220, 220))
    height, width = image.shape[:2]
    if len(faces):
        x, y, w, h = sorted(faces, key=lambda item: item[2] * item[3], reverse=True)[0]
        side = int(max(w, h) * 1.9)
        cx = x + w // 2
        cy = y + h // 2
    else:
        side = int(min(width, height) * 0.42)
        cx = width // 2
        cy = int(height * 0.27)
    x1 = max(0, cx - side // 2)
    y1 = max(0, cy - side // 2)
    x2 = min(width, x1 + side)
    y2 = min(height, y1 + side)
    if x2 - x1 < side:
        x1 = max(0, x2 - side)
    if y2 - y1 < side:
        y1 = max(0, y2 - side)
    crop = image[y1:y2, x1:x2]
    return cv2.resize(crop, (512, 512), interpolation=cv2.INTER_AREA)


def build_fullbody_proxy(front: np.ndarray, scene_background: np.ndarray, output: Path) -> None:
    canvas_h, canvas_w = 1280, 720
    bg = cv2.resize(scene_background, (canvas_w, canvas_h), interpolation=cv2.INTER_AREA)
    bg = cv2.GaussianBlur(bg, (0, 0), 18)
    overlay = np.full_like(bg, (235, 225, 212), dtype=np.uint8)
    bg = cv2.addWeighted(bg, 0.38, overlay, 0.62, 0)

    src_h, src_w = front.shape[:2]
    # Keep head and torso from the real portrait; synthesize only the missing lower body.
    crop = front[int(src_h * 0.02) : int(src_h * 0.70), int(src_w * 0.13) : int(src_w * 0.88)]
    target_w = 430
    target_h = int(crop.shape[0] * target_w / crop.shape[1])
    upper = cv2.resize(crop, (target_w, target_h), interpolation=cv2.INTER_AREA)
    x = (canvas_w - target_w) // 2
    y = 60
    bg[y : y + target_h, x : x + target_w] = upper

    waist_y = y + int(target_h * 0.74)
    center_x = canvas_w // 2
    dress_color = tuple(int(v) for v in np.mean(upper[int(target_h * 0.58) :, int(target_w * 0.25) : int(target_w * 0.75)], axis=(0, 1)))
    shadow = (170, 158, 145)
    # Long white dress proxy.
    dress = np.array(
        [
            [center_x - 105, waist_y - 12],
            [center_x + 105, waist_y - 8],
            [center_x + 178, 1110],
            [center_x + 54, 1145],
            [center_x - 70, 1142],
            [center_x - 178, 1110],
        ],
        dtype=np.int32,
    )
    cv2.fillPoly(bg, [dress], dress_color)
    cv2.polylines(bg, [dress], True, shadow, 2, cv2.LINE_AA)
    cv2.line(bg, (center_x - 20, waist_y + 8), (center_x - 68, 1128), shadow, 2, cv2.LINE_AA)
    cv2.line(bg, (center_x + 36, waist_y + 18), (center_x + 66, 1128), (210, 201, 190), 2, cv2.LINE_AA)
    # Minimal feet/shoe hints, intentionally subdued.
    cv2.ellipse(bg, (center_x - 58, 1160), (38, 12), -8, 0, 360, (70, 60, 52), -1, cv2.LINE_AA)
    cv2.ellipse(bg, (center_x + 58, 1160), (38, 12), 8, 0, 360, (70, 60, 52), -1, cv2.LINE_AA)
    # Soft floor shadow.
    cv2.ellipse(bg, (center_x, 1176), (190, 24), 0, 0, 360, (96, 86, 80), -1, cv2.LINE_AA)
    bg = cv2.addWeighted(bg, 0.96, np.full_like(bg, 245), 0.04, 0)
    imwrite(output, bg, quality=96)


def cover_to_canvas(image: np.ndarray, width: int, height: int) -> np.ndarray:
    src_h, src_w = image.shape[:2]
    scale = max(width / src_w, height / src_h)
    resized = cv2.resize(image, (math.ceil(src_w * scale), math.ceil(src_h * scale)), interpolation=cv2.INTER_AREA)
    resized_h, resized_w = resized.shape[:2]
    x = max(0, (resized_w - width) // 2)
    y = max(0, (resized_h - height) // 2)
    canvas = resized[y : y + height, x : x + width].copy()
    if canvas.shape[:2] != (height, width):
        canvas = cv2.copyMakeBorder(
            canvas,
            0,
            height - canvas.shape[0],
            0,
            width - canvas.shape[1],
            cv2.BORDER_REPLICATE,
        )
    return canvas


def segment_person_cutout(source: Path, output: Path) -> np.ndarray:
    if not YOLO_SEG_MODEL.exists():
        raise RuntimeError(f"Missing YOLO segmentation model: {YOLO_SEG_MODEL}")
    from ultralytics import YOLO

    image = imread(source)
    model = YOLO(str(YOLO_SEG_MODEL))
    result = model(str(source), imgsz=1280, conf=0.2, verbose=False)[0]
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    if result.masks is not None:
        classes = result.boxes.cls.cpu().numpy().astype(int)
        masks = result.masks.data.cpu().numpy()
        best_mask: np.ndarray | None = None
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
                best_mask = candidate
        if best_mask is not None:
            mask = best_mask
    if mask.sum() == 0:
        raise RuntimeError(f"No person mask detected in portrait: {source}")

    kernel = np.ones((9, 9), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    mask = cv2.GaussianBlur(mask, (0, 0), 4)
    ys, xs = np.where(mask > 18)
    x1 = max(int(xs.min()) - 12, 0)
    x2 = min(int(xs.max()) + 12, image.shape[1] - 1)
    y1 = max(int(ys.min()) - 12, 0)
    y2 = min(int(ys.max()) + 10, image.shape[0] - 1)
    crop = image[y1 : y2 + 1, x1 : x2 + 1]
    crop_mask = mask[y1 : y2 + 1, x1 : x2 + 1]
    rgba = cv2.cvtColor(crop, cv2.COLOR_BGR2BGRA)
    rgba[:, :, 3] = crop_mask
    imwrite(output, rgba)
    return rgba


def build_i2v_fullbody_reference(front_path: Path, scene_background: np.ndarray, output: Path, cutout_output: Path) -> None:
    rgba = segment_person_cutout(front_path, cutout_output)
    canvas = cover_to_canvas(scene_background, WIDTH, HEIGHT)
    canvas = cv2.addWeighted(canvas, 0.86, np.full_like(canvas, (10, 4, 15)), 0.14, 0)

    center = 366
    top_y = 228
    foot_y = 1162
    upper_w = 310
    upper_h = int(rgba.shape[0] * upper_w / rgba.shape[1])
    upper = cv2.resize(rgba, (upper_w, upper_h), interpolation=cv2.INTER_AREA)

    alpha = upper[:, :, 3].astype(np.float32)
    fade = 82
    for y in range(max(0, upper_h - fade), upper_h):
        alpha[y] *= (upper_h - y) / fade
    upper[:, :, 3] = np.clip(alpha, 0, 255).astype(np.uint8)

    x = center - upper_w // 2
    y = top_y
    waist_y = y + int(upper_h * 0.71)

    cv2.ellipse(canvas, (center, foot_y + 18), (120, 20), 0, 0, 360, (4, 4, 8), -1, cv2.LINE_AA)
    skirt = np.array(
        [
            [center - 82, waist_y - 10],
            [center + 82, waist_y - 10],
            [center + 126, foot_y - 44],
            [center + 54, foot_y - 4],
            [center - 52, foot_y - 4],
            [center - 124, foot_y - 44],
        ],
        np.int32,
    )
    cv2.fillPoly(canvas, [skirt], (214, 208, 196))
    cv2.fillPoly(
        canvas,
        [np.array([[center - 82, waist_y - 10], [center - 118, foot_y - 47], [center - 54, foot_y - 4], [center - 18, waist_y + 8]], np.int32)],
        (176, 169, 158),
    )
    cv2.fillPoly(
        canvas,
        [np.array([[center + 82, waist_y - 10], [center + 118, foot_y - 47], [center + 54, foot_y - 4], [center + 18, waist_y + 8]], np.int32)],
        (182, 175, 164),
    )
    for dx, color, thickness in [
        (-68, (125, 120, 114), 1),
        (-44, (236, 232, 222), 2),
        (-20, (164, 158, 148), 1),
        (8, (238, 234, 224), 2),
        (34, (143, 137, 130), 1),
        (62, (235, 231, 222), 1),
    ]:
        cv2.line(canvas, (center + dx, waist_y + 8), (center + int(dx * 0.45), foot_y - 28), color, thickness, cv2.LINE_AA)
    cv2.polylines(canvas, [skirt], True, (150, 143, 132), 1, cv2.LINE_AA)
    cv2.ellipse(canvas, (center - 38, foot_y), (32, 10), -6, 0, 360, (28, 26, 28), -1, cv2.LINE_AA)
    cv2.ellipse(canvas, (center + 38, foot_y), (32, 10), 6, 0, 360, (28, 26, 28), -1, cv2.LINE_AA)

    person_alpha = upper[:, :, 3:4].astype(np.float32) / 255
    roi = canvas[y : y + upper_h, x : x + upper_w]
    roi[:] = (upper[:, :, :3].astype(np.float32) * person_alpha + roi.astype(np.float32) * (1 - person_alpha)).astype(np.uint8)

    rim = np.zeros_like(canvas)
    cv2.polylines(rim, [skirt], False, (255, 80, 210), 3, cv2.LINE_AA)
    canvas = cv2.addWeighted(canvas, 1.0, rim, 0.08, 0)
    canvas = cv2.convertScaleAbs(canvas, alpha=1.03, beta=3)
    imwrite(output, canvas, quality=96)


def draw_pose_frame(width: int, height: int, frame: int, total: int) -> np.ndarray:
    image = np.zeros((height, width, 3), dtype=np.uint8)
    phase = math.sin(frame / max(1, total - 1) * math.pi * 2)
    cx = width // 2 + int(12 * phase)
    top = 120
    neck = (cx, top + 82)
    head = (cx, top + 42)
    hip = (cx, top + 318)
    l_sh = (cx - 58, top + 105)
    r_sh = (cx + 58, top + 105)
    l_el = (cx - 78, top + 200 + int(8 * phase))
    r_el = (cx + 82, top + 202 - int(7 * phase))
    l_wr = (cx - 54, top + 292 + int(6 * phase))
    r_wr = (cx + 104, top + 292 - int(6 * phase))
    l_hip = (cx - 48, top + 330)
    r_hip = (cx + 48, top + 330)
    l_knee = (cx - 76 + int(18 * phase), top + 512)
    r_knee = (cx + 78 - int(18 * phase), top + 512)
    l_ankle = (cx - 96 + int(20 * phase), top + 672)
    r_ankle = (cx + 92 - int(20 * phase), top + 672)

    def line(a: tuple[int, int], b: tuple[int, int], color: tuple[int, int, int], thickness: int = 8) -> None:
        cv2.line(image, a, b, color, thickness, cv2.LINE_AA)

    def dot(p: tuple[int, int], color: tuple[int, int, int]) -> None:
        cv2.circle(image, p, 7, color, -1, cv2.LINE_AA)

    cv2.circle(image, head, 32, (255, 0, 255), 4, cv2.LINE_AA)
    line(neck, hip, (0, 210, 255), 7)
    line(l_sh, r_sh, (0, 0, 255), 7)
    line(l_sh, l_el, (0, 128, 255), 7)
    line(l_el, l_wr, (0, 255, 255), 7)
    line(r_sh, r_el, (0, 255, 0), 7)
    line(r_el, r_wr, (80, 255, 80), 7)
    line(l_hip, r_hip, (255, 128, 0), 7)
    line(l_hip, l_knee, (0, 255, 0), 8)
    line(l_knee, l_ankle, (0, 180, 255), 8)
    line(r_hip, r_knee, (255, 0, 0), 8)
    line(r_knee, r_ankle, (255, 0, 160), 8)
    for point, color in [
        (neck, (255, 255, 255)),
        (l_sh, (0, 0, 255)),
        (r_sh, (0, 255, 0)),
        (l_el, (0, 128, 255)),
        (r_el, (0, 255, 0)),
        (l_wr, (0, 255, 255)),
        (r_wr, (80, 255, 80)),
        (l_hip, (255, 128, 0)),
        (r_hip, (255, 128, 0)),
        (l_knee, (0, 255, 0)),
        (r_knee, (255, 0, 0)),
        (l_ankle, (0, 180, 255)),
        (r_ankle, (255, 0, 160)),
    ]:
        dot(point, color)
    return image


def create_pose_driver(run_dir: Path, output: Path, *, frames: int = 33, fps: int = 8) -> None:
    frames_dir = run_dir / "pose_frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    for index in range(frames):
        frame = draw_pose_frame(480, 832, index, frames)
        imwrite(frames_dir / f"pose_{index:04d}.jpg", frame, quality=95)
    run(
        [
            "ffmpeg",
            "-y",
            "-framerate",
            str(fps),
            "-i",
            str(frames_dir / "pose_%04d.jpg"),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-r",
            str(fps),
            str(output),
        ],
        timeout=120,
    )


def prepare_generation_assets(run_dir: Path, assets: dict[str, list[RenderAsset]]) -> dict[str, Path]:
    if not assets["portraits"]:
        raise RuntimeError("No portrait images found.")
    if not assets["scene_images"] or not assets["scene_videos"]:
        raise RuntimeError("Scene images/videos are required.")

    prepared = run_dir / "prepared"
    prepared.mkdir(parents=True, exist_ok=True)
    front = imread(assets["portraits"][-1].path)
    side = imread(assets["portraits"][0].path)
    scene_bg = imread(assets["scene_images"][0].path)

    front_path = prepared / "portrait_front_upright.jpg"
    side_path = prepared / "portrait_side_upright.jpg"
    face_path = prepared / "portrait_face_512.jpg"
    proxy_path = prepared / "fullbody_reference_proxy.jpg"
    i2v_reference = prepared / "fullbody_i2v_reference.jpg"
    i2v_reference_480 = prepared / "fullbody_i2v_reference_480x832.jpg"
    cutout_path = prepared / "portrait_person_cutout.png"
    pose_video = prepared / "fullbody_pose_driver.mp4"

    imwrite(front_path, front, quality=96)
    imwrite(side_path, side, quality=96)
    imwrite(face_path, detect_face_crop(front), quality=96)
    build_fullbody_proxy(front, scene_bg, proxy_path)
    i2v_bg = imread(assets["scene_images"][min(8, len(assets["scene_images"]) - 1)].path)
    build_i2v_fullbody_reference(front_path, i2v_bg, i2v_reference, cutout_path)
    i2v_480 = cv2.resize(imread(i2v_reference), (480, 832), interpolation=cv2.INTER_AREA)
    imwrite(i2v_reference_480, i2v_480, quality=96)
    create_pose_driver(run_dir, pose_video, frames=33, fps=8)

    for path in [front_path, side_path, face_path, proxy_path, i2v_reference, i2v_reference_480, pose_video, assets["scene_videos"][0].path]:
        shutil.copy2(path, COMFY_INPUT / path.name)
    bg_video = COMFY_INPUT / assets["scene_videos"][0].path.name

    return {
        "front": front_path,
        "side": side_path,
        "face": face_path,
        "fullbody_proxy": proxy_path,
        "fullbody_i2v_reference": i2v_reference,
        "fullbody_i2v_reference_480": i2v_reference_480,
        "person_cutout": cutout_path,
        "pose_video": pose_video,
        "comfy_proxy": COMFY_INPUT / proxy_path.name,
        "comfy_i2v_reference": COMFY_INPUT / i2v_reference_480.name,
        "comfy_face": COMFY_INPUT / face_path.name,
        "comfy_pose": COMFY_INPUT / pose_video.name,
        "comfy_bg_video": bg_video,
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


def wait_for_history(prompt_id: str, timeout: int = 5400) -> dict[str, Any]:
    start = time.time()
    while time.time() - start < timeout:
        result = http_json("GET", f"/history/{prompt_id}", timeout=30)
        if prompt_id in result:
            item = result[prompt_id]
            status = item.get("status") or {}
            if status.get("status_str") == "error":
                raise RuntimeError(json.dumps(status, ensure_ascii=False, indent=2))
            return item
        queue = http_json("GET", "/queue", timeout=15)
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
    candidates = [
        path
        for path in COMFY_OUTPUT.glob(f"{prefix}*.mp4")
        if path.stat().st_mtime >= after
    ]
    if not candidates:
        raise RuntimeError(f"No ComfyUI mp4 output found for prefix {prefix}")
    return sorted(candidates, key=lambda p: p.stat().st_mtime, reverse=True)[0]


def wananimate_fullbody_prompt(*, proxy_name: str, face_name: str, pose_name: str, bg_video_name: str, prefix: str) -> dict[str, Any]:
    positive = (
        "realistic vertical phone-shot business KTV vlog, full body Chinese female owner based on the reference image, "
        "same face, same black straight hair, same cream white draped blouse and dress style, natural relaxed expression, "
        "standing and gently walking in a premium KTV lobby, warm cyan magenta indoor lighting, smooth handheld camera, "
        "daily operator story style, coherent body proportions, high detail, natural skin, premium but real"
    )
    return {
        "1": {
            "class_type": "VHS_LoadVideo",
            "inputs": {
                "video": pose_name,
                "force_rate": 8,
                "custom_width": 480,
                "custom_height": 832,
                "frame_load_cap": 33,
                "skip_first_frames": 0,
                "select_every_nth": 1,
                "format": "Wan",
            },
        },
        "2": {
            "class_type": "VHS_LoadVideo",
            "inputs": {
                "video": bg_video_name,
                "force_rate": 8,
                "custom_width": 480,
                "custom_height": 832,
                "frame_load_cap": 33,
                "skip_first_frames": 0,
                "select_every_nth": 1,
                "format": "Wan",
            },
        },
        "3": {"class_type": "LoadImage", "inputs": {"image": proxy_name}},
        "4": {"class_type": "LoadImage", "inputs": {"image": face_name}},
        "5": {"class_type": "CLIPVisionLoader", "inputs": {"clip_name": "clip_vision_h.safetensors"}},
        "6": {
            "class_type": "WanVideoClipVisionEncode",
            "inputs": {
                "clip_vision": ["5", 0],
                "image_1": ["3", 0],
                "strength_1": 1.0,
                "strength_2": 1.0,
                "crop": "center",
                "combine_embeds": "average",
                "force_offload": True,
                "tiles": 0,
                "ratio": 0.5,
            },
        },
        "7": {
            "class_type": "WanVideoVAELoader",
            "inputs": {
                "model_name": "Wan2_1_VAE_bf16.safetensors",
                "precision": "bf16",
                "use_cpu_cache": False,
                "verbose": False,
            },
        },
        "8": {
            "class_type": "WanVideoAnimateEmbeds",
            "inputs": {
                "vae": ["7", 0],
                "width": 480,
                "height": 832,
                "num_frames": 33,
                "force_offload": True,
                "frame_window_size": 33,
                "colormatch": "disabled",
                "pose_strength": 1.0,
                "face_strength": 1.15,
                "clip_embeds": ["6", 0],
                "ref_images": ["3", 0],
                "pose_images": ["1", 0],
                "face_images": ["4", 0],
                "bg_images": ["2", 0],
                "tiled_vae": False,
            },
        },
        "9": {
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
        "10": {
            "class_type": "WanVideoLoraSelectMulti",
            "inputs": {
                "lora_0": "WanVideo\\WanAnimate_relight_lora_fp16.safetensors",
                "strength_0": 1.0,
                "lora_1": "WanVideo\\Lightx2v\\lightx2v_I2V_14B_480p_cfg_step_distill_rank64_bf16.safetensors",
                "strength_1": 1.15,
                "lora_2": "none",
                "strength_2": 1.0,
                "lora_3": "none",
                "strength_3": 1.0,
                "lora_4": "none",
                "strength_4": 1.0,
            },
        },
        "11": {
            "class_type": "WanVideoBlockSwap",
            "inputs": {
                "blocks_to_swap": 30,
                "offload_img_emb": False,
                "offload_txt_emb": False,
                "use_non_blocking": True,
                "vace_blocks_to_swap": 0,
                "prefetch_blocks": 1,
                "block_swap_debug": False,
            },
        },
        "12": {
            "class_type": "WanVideoModelLoader",
            "inputs": {
                "model": "WanVideo\\2_2\\Wan2_2-Animate-14B_fp8_e4m3fn_scaled_KJ.safetensors",
                "base_precision": "fp16_fast",
                "quantization": "disabled",
                "load_device": "offload_device",
                "attention_mode": "sdpa",
                "lora": ["10", 0],
                "block_swap_args": ["11", 0],
                "rms_norm_function": "default",
            },
        },
        "13": {
            "class_type": "WanVideoEasyCache",
            "inputs": {"easycache_thresh": 0.015, "start_step": 2, "end_step": -1, "cache_device": "offload_device"},
        },
        "14": {"class_type": "WanVideoSLG", "inputs": {"blocks": "7,8,9", "start_percent": 0.1, "end_percent": 0.7}},
        "15": {
            "class_type": "WanVideoSampler",
            "inputs": {
                "model": ["12", 0],
                "image_embeds": ["8", 0],
                "text_embeds": ["9", 0],
                "steps": 4,
                "cfg": 1.0,
                "shift": 5.0,
                "seed": 2026052701,
                "force_offload": True,
                "scheduler": "flowmatch_distill",
                "riflex_freq_index": 0,
                "cache_args": ["13", 0],
                "slg_args": ["14", 0],
                "denoise_strength": 1.0,
                "batched_cfg": False,
                "rope_function": "comfy",
                "start_step": 0,
                "end_step": -1,
                "add_noise_to_samples": False,
            },
        },
        "16": {
            "class_type": "WanVideoDecode",
            "inputs": {
                "vae": ["7", 0],
                "samples": ["15", 0],
                "enable_vae_tiling": True,
                "tile_x": 272,
                "tile_y": 272,
                "tile_stride_x": 144,
                "tile_stride_y": 128,
                "normalization": "default",
            },
        },
        "17": {
            "class_type": "VHS_VideoCombine",
            "inputs": {
                "images": ["16", 0],
                "frame_rate": 8,
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


def generate_fullbody_host_clip(run_dir: Path, prepared: dict[str, Path]) -> Path:
    prefix = "aiops_fullbody_host_story"
    start = time.time()
    prompt = wananimate_fullbody_prompt(
        proxy_name=prepared["comfy_proxy"].name,
        face_name=prepared["comfy_face"].name,
        pose_name=prepared["comfy_pose"].name,
        bg_video_name=prepared["comfy_bg_video"].name,
        prefix=prefix,
    )
    (run_dir / "wananimate_fullbody_prompt.json").write_text(json.dumps(prompt, ensure_ascii=False, indent=2), encoding="utf-8")
    prompt_id = submit_prompt(prompt)
    print(f"[comfy] fullbody host prompt_id={prompt_id}", flush=True)
    history = wait_for_history(prompt_id, timeout=5400)
    (run_dir / "wananimate_fullbody_history.json").write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")
    output = newest_output(prefix, after=start)
    target = run_dir / "fullbody_host_wananimate.mp4"
    shutil.copy2(output, target)
    return target


def wan_5b_i2v_fullbody_prompt(*, reference_name: str, prefix: str) -> dict[str, Any]:
    positive = (
        "realistic full body Chinese female KTV owner, same face and hair as reference image, "
        "same cream white draped blouse and long cream dress, standing naturally in a premium KTV interior, "
        "subtle breathing motion, slight relaxed hand movement, smooth phone camera micro motion, "
        "warm cyan magenta lighting, coherent body, natural skin, real commercial vlog video"
    )
    negative = (
        "cartoon, anime, illustration, low quality, blurry, flicker, jitter, unstable face, different person, "
        "face swap, deformed body, bad hands, extra limbs, missing legs, cropped head, talking head only, "
        "duplicate person, text, subtitles, watermark, logo, plastic skin"
    )
    return {
        "1": {"class_type": "LoadImage", "inputs": {"image": reference_name}},
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
                "noise_aug_strength": 0.012,
                "latent_strength": 1.0,
            },
        },
        "4": {"class_type": "WanVideoEmptyEmbeds", "inputs": {"width": 480, "height": 832, "num_frames": 33, "extra_latents": ["3", 0]}},
        "5": {
            "class_type": "WanVideoTextEncodeCached",
            "inputs": {
                "model_name": "umt5-xxl-enc-bf16.safetensors",
                "precision": "bf16",
                "positive_prompt": positive,
                "negative_prompt": negative,
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
                "seed": 2026052705,
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


def generate_fullbody_host_clip_5b_i2v(run_dir: Path, prepared: dict[str, Path]) -> Path:
    prefix = "aiops_fullbody_5b_i2v"
    start = time.time()
    prompt = wan_5b_i2v_fullbody_prompt(reference_name=prepared["comfy_i2v_reference"].name, prefix=prefix)
    (run_dir / "wan_5b_i2v_fullbody_prompt.json").write_text(json.dumps(prompt, ensure_ascii=False, indent=2), encoding="utf-8")
    prompt_id = submit_prompt(prompt)
    print(f"[comfy] 5b i2v fullbody prompt_id={prompt_id}", flush=True)
    history = wait_for_history(prompt_id, timeout=2400)
    (run_dir / "wan_5b_i2v_fullbody_history.json").write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")
    output = newest_output(prefix, after=start)
    target = run_dir / "fullbody_host_5b_i2v.mp4"
    shutil.copy2(output, target)
    return target


async def generate_voice(run_dir: Path) -> tuple[Path, Path]:
    text_path = run_dir / "voiceover_script.txt"
    mp3_path = run_dir / "voiceover_edge.mp3"
    wav_path = run_dir / "voiceover_normalized.wav"
    text_path.write_text(VOICE_TEXT, encoding="utf-8")
    communicate = edge_tts.Communicate(
        VOICE_TEXT,
        voice="zh-CN-XiaoyiNeural",
        rate="-13%",
        pitch="-2Hz",
        volume="+0%",
    )
    await communicate.save(str(mp3_path))
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(mp3_path),
            "-af",
            "aresample=44100,highpass=f=75,lowpass=f=13500,acompressor=threshold=-18dB:ratio=2.0:attack=14:release=180,loudnorm=I=-16:TP=-1.5:LRA=9",
            "-ar",
            "44100",
            "-ac",
            "2",
            str(wav_path),
        ],
        timeout=180,
    )
    return text_path, wav_path


def make_video_scene(source: Path, output: Path, *, duration: float | None = None, start: float = 0.0) -> Path:
    cmd = ["ffmpeg", "-y"]
    if duration is not None and duration > ffprobe_duration(source) + 0.1:
        cmd += ["-stream_loop", "-1"]
    if start > 0:
        cmd += ["-ss", f"{start:.3f}"]
    cmd += ["-i", str(source)]
    if duration is not None:
        cmd += ["-t", f"{duration:.3f}"]
    vf = (
        f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,"
        f"crop={WIDTH}:{HEIGHT},fps={FPS},setsar=1,"
        "colorbalance=rs=0.025:gs=0.004:bs=-0.018:rm=0.012:bm=-0.014,"
        "eq=brightness=0.006:contrast=1.035:saturation=1.045,"
        "unsharp=5:5:0.24:3:3:0.05,format=yuv420p"
    )
    run(
        [
            *cmd,
            "-vf",
            vf,
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "slow",
            "-crf",
            "17",
            str(output),
        ],
        timeout=240,
    )
    return output


def make_still_scene(source: Path, output: Path, *, duration: float, zoom: float = 0.0015) -> Path:
    vf = (
        f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,"
        f"crop={WIDTH}:{HEIGHT},"
        f"zoompan=z='1+{zoom}*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:fps={FPS}:s={WIDTH}x{HEIGHT},"
        "colorbalance=rs=0.025:gs=0.004:bs=-0.018:rm=0.012:bm=-0.014,"
        "eq=brightness=0.006:contrast=1.035:saturation=1.045,"
        "unsharp=5:5:0.22:3:3:0.05,format=yuv420p"
    )
    run(
        [
            "ffmpeg",
            "-y",
            "-loop",
            "1",
            "-framerate",
            str(FPS),
            "-i",
            str(source),
            "-t",
            f"{duration:.3f}",
            "-vf",
            vf,
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "slow",
            "-crf",
            "17",
            str(output),
        ],
        timeout=180,
    )
    return output


def build_visual_sequence(run_dir: Path, assets: dict[str, list[RenderAsset]], host_clip: Path) -> tuple[Path, list[dict[str, Any]]]:
    scenes_dir = run_dir / "scenes"
    scenes_dir.mkdir(parents=True, exist_ok=True)
    scene_videos = assets["scene_videos"]
    scene_images = assets["scene_images"]

    def pick(items: list[RenderAsset], index: int) -> Path:
        if not items:
            raise RuntimeError("Scene assets are required.")
        return items[min(index, len(items) - 1)].path

    specs: list[tuple[str, Path, str, float | None]] = [
        ("01_fullbody_owner_open", host_clip, "host_generated", 4.6),
        ("02_lobby_order", pick(scene_videos, 1), "real_scene_video", 4.7),
        ("03_room_first_view", pick(scene_videos, 3), "real_scene_video", 4.3),
        ("04_corridor_flow", pick(scene_videos, 2), "real_scene_video", 3.8),
        ("05_private_room_table", pick(scene_images, 0), "real_scene_photo", 3.6),
        ("06_screen_sound_check", pick(scene_images, 1), "real_scene_photo", 3.6),
        ("07_sofa_layout", pick(scene_videos, 4), "real_scene_video", 4.0),
        ("08_clean_table_detail", pick(scene_images, 3), "real_scene_photo", 3.5),
        ("09_service_equipment", pick(scene_images, 8), "real_scene_photo", 3.5),
        ("10_walk_to_room", pick(scene_videos, 0), "real_scene_video", 4.2),
        ("11_big_room_space", pick(scene_images, 9), "real_scene_photo", 3.4),
        ("12_neon_hall_scale", pick(scene_videos, 1), "real_scene_video", 4.4),
        ("13_vip_room_finish", pick(scene_images, 7), "real_scene_photo", 3.8),
        ("14_fullbody_owner_close", host_clip, "host_generated_reprise", 4.4),
    ]
    clips: list[Path] = []
    manifest: list[dict[str, Any]] = []
    for index, (name, source, kind, duration) in enumerate(specs, start=1):
        output = scenes_dir / f"{index:02d}_{name}.mp4"
        if kind.startswith("host"):
            make_video_scene(source, output, duration=duration)
        elif source.suffix.lower() in {".mp4", ".mov", ".m4v"}:
            make_video_scene(source, output, duration=duration)
        else:
            make_still_scene(source, output, duration=duration or 3.4, zoom=0.0012 + index * 0.00008)
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
    visual = run_dir / "visual_story_xfade.mp4"
    xfade_sequence(clips, visual, overlap=0.45)
    return visual, manifest


def xfade_sequence(inputs: list[Path], output: Path, *, overlap: float) -> Path:
    if len(inputs) == 1:
        shutil.copy2(inputs[0], output)
        return output
    durations = [ffprobe_duration(path) for path in inputs]
    cmd = ["ffmpeg", "-y"]
    for path in inputs:
        cmd += ["-i", str(path)]
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
            str(output),
        ],
        timeout=480,
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
    ass = run_dir / "story_subtitles.ass"
    lines = [
        "[Script Info]",
        "ScriptType: v4.00+",
        "PlayResX: 720",
        "PlayResY: 1280",
        "WrapStyle: 2",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        "Style: Title,Microsoft YaHei,38,&H00FFFFFF,&H00FFFFFF,&H66000000,&H55000000,1,0,0,0,100,100,0,0,1,2,1,8,48,48,62,1",
        "Style: Sub,Microsoft YaHei,34,&H00FFFFFF,&H00FFFFFF,&HAA000000,&H77000000,0,0,0,0,100,100,0,0,1,2,1,2,56,56,118,1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
        f"Dialogue: 0,{ass_time(0)},{ass_time(min(duration, 7.0))},Title,,0,0,0,,曼哈顿商务KTV | 真实探店",
    ]
    for start, end, text in SUBTITLE_LINES:
        lines.append(f"Dialogue: 1,{ass_time(start)},{ass_time(min(end, duration))},Sub,,0,0,0,,{text}")
    ass.write_text("\n".join(lines), encoding="utf-8")
    return ass


def make_audio_mix(run_dir: Path, voice_wav: Path, duration: float) -> Path:
    bed = run_dir / "ambient_music_bed.wav"
    audio = run_dir / "story_audio_mix.wav"
    run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            f"anoisesrc=color=pink:amplitude=0.025:d={duration:.3f}",
            "-f",
            "lavfi",
            "-i",
            f"sine=frequency=98:sample_rate=44100:duration={duration:.3f}",
            "-filter_complex",
            "[0:a]lowpass=f=2400,volume=0.26[a0];[1:a]volume=0.025[a1];[a0][a1]amix=inputs=2:duration=longest,afade=t=in:st=0:d=1.0,afade=t=out:st="
            + f"{max(0.0, duration - 2.0):.3f}:d=2.0",
            "-ar",
            "44100",
            "-ac",
            "2",
            str(bed),
        ],
        timeout=120,
    )
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(voice_wav),
            "-i",
            str(bed),
            "-filter_complex",
            f"[0:a]volume=1.0,apad[a0];[1:a]volume=0.34[a1];[a0][a1]amix=inputs=2:duration=longest,atrim=0:{duration:.3f},acompressor=threshold=-17dB:ratio=1.8:attack=15:release=160,loudnorm=I=-16:TP=-1.5:LRA=9",
            "-ar",
            "44100",
            "-ac",
            "2",
            str(audio),
        ],
        timeout=180,
    )
    return audio


def burn_subtitles_and_audio(run_dir: Path, visual: Path, audio: Path, ass: Path) -> Path:
    final = run_dir / "business_ktv_fullbody_story_final.mp4"
    ass_filter = str(ass).replace("\\", "/").replace(":", "\\:")
    duration = ffprobe_duration(visual)
    vf = f"subtitles='{ass_filter}',fade=t=out:st={max(0.0, duration - 1.3):.3f}:d=1.3"
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(visual),
            "-i",
            str(audio),
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
            str(final),
        ],
        timeout=480,
    )
    return final


def make_preview(run_dir: Path, final: Path) -> Path:
    preview = run_dir / "fullbody_story_preview_sheet.jpg"
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(final),
            "-vf",
            "fps=1/4,scale=240:-1,tile=5x2",
            "-frames:v",
            "1",
            str(preview),
        ],
        timeout=120,
    )
    return preview


def make_contact_sheet(run_dir: Path, final: Path) -> Path:
    contact = run_dir / "final_contact_sheet.jpg"
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(final),
            "-vf",
            "fps=1/4,scale=240:-1,tile=5x3",
            "-frames:v",
            "1",
            str(contact),
        ],
        timeout=120,
    )
    return contact


def write_storyboard(run_dir: Path, manifest: list[dict[str, Any]], final: Path, preview: Path) -> Path:
    storyboard = run_dir / "fullbody_storyboard.md"
    text = f"""# 商务KTV全身数字人故事片

## 成片定位

老板娘第一视角真实探店：用半身人物画像生成全身数字人开场与收尾，用真实场景素材完成大厅、走廊、包房和服务动线展示。

## 核心故事

不是单纯展示灯光装修，而是讲“商务接待为什么稳”：大厅秩序、包房检查、动线清楚、氛围体面，最后落到“你带重要的人来，剩下交给我们”。

## 素材使用

- 人物画像：用于脸部、发型、耳饰、上衣、整体气质参考。
- 场景视频/图片：用于真实空间走访和包房展示。
- 参考视频：用于手机第一视角、边走边讲、数字背书式表达的节奏参考。

## 输出

- 成片：`{final}`
- 预览：`{preview}`

## 分镜

"""
    for item in manifest:
        text += f"- {item['index']:02d}. {item['name']} ({item['kind']}), {item['duration']:.2f}s\n"
    storyboard.write_text(text, encoding="utf-8")
    return storyboard


def mirror_outputs(run_dir: Path, mirror_dir: Path, files: list[Path]) -> list[Path]:
    mirrored: list[Path] = []
    for path in files:
        target = mirror_dir / path.name
        shutil.copy2(path, target)
        mirrored.append(target)
    return mirrored


async def main() -> None:
    stamp, run_dir, mirror_dir = make_run_dirs()
    print(f"[run] {stamp} {run_dir}", flush=True)
    assets = copy_source_assets(run_dir)
    prepared = prepare_generation_assets(run_dir, assets)
    print("[stage] prepared assets", flush=True)
    host_clip = generate_fullbody_host_clip_5b_i2v(run_dir, prepared)
    print(f"[stage] fullbody 5b i2v host clip={host_clip}", flush=True)
    text_path, voice_wav = await generate_voice(run_dir)
    visual, scene_manifest = build_visual_sequence(run_dir, assets, host_clip)
    visual_duration = ffprobe_duration(visual)
    ass = create_subtitles(run_dir, visual_duration)
    audio = make_audio_mix(run_dir, voice_wav, visual_duration)
    final = burn_subtitles_and_audio(run_dir, visual, audio, ass)
    preview = make_preview(run_dir, final)
    contact = make_contact_sheet(run_dir, final)
    storyboard = write_storyboard(run_dir, scene_manifest, final, preview)
    manifest = {
        "stamp": stamp,
        "run_dir": str(run_dir),
        "mirror_dir": str(mirror_dir),
        "source_root": str(ROOT),
        "voiceover_script": str(text_path),
        "prepared_assets": {key: str(value) for key, value in prepared.items()},
        "fullbody_host_clip": str(host_clip),
        "visual": str(visual),
        "audio": str(audio),
        "subtitles": str(ass),
        "final": str(final),
        "preview": str(preview),
        "contact_sheet": str(contact),
        "storyboard": str(storyboard),
        "scene_manifest": scene_manifest,
        "limitations": [
            "人物输入为半身画像，AI 会合理补全下半身和全身站姿。",
            "当前默认使用 Wan2.2 5B TI2V/I2V 稳定路线；14B I2V 在本机服务进程上更容易造成 ComfyUI 退出。",
            "当前声音为边缘神经 TTS 预览，正式交付建议替换为真人录音或授权音色。",
        ],
    }
    manifest_path = run_dir / "fullbody_story_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    mirrored = mirror_outputs(
        run_dir,
        mirror_dir,
        [
            final,
            preview,
            contact,
            storyboard,
            manifest_path,
            host_clip,
            prepared["fullbody_proxy"],
            prepared["fullbody_i2v_reference"],
            ass,
        ],
    )
    print(json.dumps({"final": str(final), "preview": str(preview), "mirror": [str(p) for p in mirrored]}, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    asyncio.run(main())
