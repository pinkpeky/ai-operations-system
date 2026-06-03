"""Generate a higher-quality business KTV promo video from local materials.

Run with E:/ComfyUI/venv/Scripts/python.exe so the local ComfyUI Python
packages (edge_tts, Pillow, cv2 dependencies) are available.
"""

from __future__ import annotations

import asyncio
import json
import math
import shutil
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

import edge_tts


ROOT = Path(r"D:\流程测试")
ASCII_ROOT = Path(r"D:\aiops_production_runs")
COMFY_ROOT = Path(r"E:\ComfyUI_cu130\ComfyUI")
COMFY_INPUT = COMFY_ROOT / "input"
COMFY_OUTPUT = COMFY_ROOT / "output"
COMFY_API = "http://127.0.0.1:8188"
CLIENT_ID = f"aiops-hq-ktv-{uuid4()}"

VOICE_TEXT = (
    "很多人以为，商务KTV拼的是灯光和装修。"
    "其实真正决定客户愿不愿意再来，是从进门那一刻开始的稳定感。"
    "每天营业前，我会先看包厢气味，灯光角度，音响状态，再确认接待动线。"
    "客户带重要的人来，不需要担心冷场，也不用解释太多。"
    "房间，服务，分寸，我们提前准备好。"
    "这里不是单纯唱歌，是商务接待里恰到好处的体面。"
    "今晚，把人带来，剩下的交给我们。"
)

SUBTITLE_LINES = [
    (0.0, 4.5, "很多人以为，商务KTV拼的是灯光和装修。"),
    (4.5, 10.8, "真正决定客户愿不愿再来，是进门那一刻的稳定感。"),
    (10.8, 18.5, "营业前，我会先看气味、灯光、音响，再确认接待动线。"),
    (18.5, 25.0, "客户带重要的人来，不需要担心冷场，也不用解释太多。"),
    (25.0, 32.2, "房间，服务，分寸，我们提前准备好。"),
    (32.2, 39.2, "这里不是单纯唱歌，是商务接待里恰到好处的体面。"),
    (39.2, 48.0, "今晚，把人带来，剩下的交给我们。"),
]


@dataclass(frozen=True)
class SceneSpec:
    name: str
    source: Path
    prompt: str
    duration: float
    seed: int


NEGATIVE_PROMPT = (
    "cartoon, anime, CGI, fantasy, over-smoothed skin, distorted room, extra doors, "
    "changed layout, deformed furniture, warped ceiling, text, watermark, logo, low quality, "
    "blurry, flicker, jitter, oversaturated, plastic look, extra fingers, deformed face"
)


def run(cmd: list[str], *, cwd: Path | None = None, timeout: int | None = None) -> None:
    print("[cmd]", " ".join(cmd), flush=True)
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
    run_dir = ASCII_ROOT / f"ktv_hq_{stamp}"
    mirror_dir = ROOT / "_aiops_production_hq" / f"ktv_hq_{stamp}"
    run_dir.mkdir(parents=True, exist_ok=True)
    mirror_dir.mkdir(parents=True, exist_ok=True)
    return stamp, run_dir, mirror_dir


async def generate_voice(run_dir: Path) -> tuple[Path, Path]:
    text_path = run_dir / "hq_voiceover.txt"
    mp3_path = run_dir / "hq_voiceover_edge.mp3"
    wav_path = run_dir / "hq_voiceover_normalized.wav"
    text_path.write_text(VOICE_TEXT, encoding="utf-8")
    communicate = edge_tts.Communicate(
        VOICE_TEXT,
        voice="zh-CN-XiaoxiaoNeural",
        rate="-11%",
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
            "aresample=44100,highpass=f=80,lowpass=f=14000,acompressor=threshold=-18dB:ratio=2.2:attack=12:release=180,loudnorm=I=-16:TP=-1.5:LRA=9",
            "-ar",
            "44100",
            "-ac",
            "2",
            str(wav_path),
        ],
        timeout=180,
    )
    return text_path, wav_path


def make_portrait_source(run_dir: Path, voice_wav: Path, duration: float, stamp: str) -> Path:
    portrait = ROOT / "人物画像" / "微信图片_20260527010011_4_131.jpg"
    source = run_dir / f"hq_portrait_source_{stamp}.mp4"
    vf = (
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        "gblur=sigma=30,eq=brightness=-0.08:saturation=0.85[bg];"
        "[0:v]scale=760:-1:force_original_aspect_ratio=decrease,format=rgba[fg];"
        "[bg][fg]overlay=(W-w)/2:(H-h)/2-60,format=yuv420p"
    )
    run(
        [
            "ffmpeg",
            "-y",
            "-loop",
            "1",
            "-i",
            str(portrait),
            "-i",
            str(voice_wav),
            "-t",
            f"{duration:.3f}",
            "-filter_complex",
            vf,
            "-r",
            "25",
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
            "-shortest",
            str(source),
        ],
        timeout=240,
    )
    comfy_source = COMFY_INPUT / source.name
    shutil.copy2(source, comfy_source)
    return comfy_source


def submit_prompt(prompt: dict[str, Any]) -> str:
    result = http_json("POST", "/prompt", {"prompt": prompt, "client_id": CLIENT_ID}, timeout=30)
    prompt_id = str(result.get("prompt_id") or "")
    if not prompt_id:
        raise RuntimeError(f"ComfyUI did not return prompt_id: {result}")
    return prompt_id


def wait_for_history(prompt_id: str, timeout: int = 900) -> dict[str, Any]:
    start = time.time()
    while time.time() - start < timeout:
        try:
            result = http_json("GET", f"/history/{prompt_id}", timeout=30)
            if prompt_id in result:
                return result[prompt_id]
        except (urllib.error.URLError, TimeoutError):
            pass
        time.sleep(3)
    raise TimeoutError(f"Timed out waiting for ComfyUI history {prompt_id}")


def wait_for_output(prefix: str, timeout: int = 900) -> Path:
    start = time.time()
    while time.time() - start < timeout:
        matches = sorted(COMFY_OUTPUT.glob(f"{prefix}*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True)
        if matches:
            return matches[0]
        time.sleep(3)
    raise TimeoutError(f"Timed out waiting for output prefix {prefix}")


def musetalk_prompt(video_name: str) -> dict[str, Any]:
    return {
        "1": {"inputs": {"video": video_name}, "class_type": "MuseTalkLoadVideo"},
        "2": {
            "inputs": {
                "use_saved_coord": False,
                "batch_size": 4,
                "bbox_shift": 0,
                "fps": 25,
                "batch_size_fa": 1,
                "video": ["1", 0],
                "audio": ["1", 1],
            },
            "class_type": "MuseTalk",
        },
        "3": {"inputs": {"video": ["2", 0]}, "class_type": "PreViewVideo"},
    }


def wan_prompt(*, image_name: str, positive: str, prefix: str, seed: int, width: int, height: int, length: int) -> dict[str, Any]:
    return {
        "1": {"inputs": {"image": image_name}, "class_type": "LoadImage"},
        "2": {"inputs": {"clip_name": "umt5_xxl_fp8_e4m3fn_scaled.safetensors", "type": "wan"}, "class_type": "CLIPLoader"},
        "3": {"inputs": {"clip": ["2", 0], "text": positive}, "class_type": "CLIPTextEncode"},
        "4": {"inputs": {"clip": ["2", 0], "text": NEGATIVE_PROMPT}, "class_type": "CLIPTextEncode"},
        "5": {"inputs": {"vae_name": "wan_2.1_vae.safetensors"}, "class_type": "VAELoader"},
        "6": {
            "inputs": {"weight_dtype": "default", "unet_name": r"Wan2.2\wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors"},
            "class_type": "UNETLoader",
        },
        "7": {
            "inputs": {"weight_dtype": "default", "unet_name": r"Wan2.2\wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors"},
            "class_type": "UNETLoader",
        },
        "8": {
            "inputs": {
                "strength_model": 1.0,
                "model": ["6", 0],
                "lora_name": r"Wan2.2\wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors",
            },
            "class_type": "LoraLoaderModelOnly",
        },
        "9": {
            "inputs": {
                "strength_model": 1.0,
                "model": ["7", 0],
                "lora_name": r"Wan2.2\wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors",
            },
            "class_type": "LoraLoaderModelOnly",
        },
        "10": {"inputs": {"model": ["8", 0], "shift": 5.0}, "class_type": "ModelSamplingSD3"},
        "11": {"inputs": {"model": ["9", 0], "shift": 5.0}, "class_type": "ModelSamplingSD3"},
        "12": {"inputs": {"clip_name": "clip_vision_h.safetensors"}, "class_type": "CLIPVisionLoader"},
        "13": {"inputs": {"clip_vision": ["12", 0], "crop": "center", "image": ["1", 0]}, "class_type": "CLIPVisionEncode"},
        "14": {
            "inputs": {
                "width": width,
                "height": height,
                "length": length,
                "batch_size": 1,
                "vae": ["5", 0],
                "positive": ["3", 0],
                "negative": ["4", 0],
                "start_image": ["1", 0],
                "clip_vision_output": ["13", 0],
            },
            "class_type": "WanImageToVideo",
        },
        "15": {
            "inputs": {
                "add_noise": "enable",
                "noise_seed": seed,
                "steps": 4,
                "cfg": 1.0,
                "sampler_name": "euler",
                "scheduler": "simple",
                "start_at_step": 0,
                "end_at_step": 2,
                "return_with_leftover_noise": "enable",
                "model": ["10", 0],
                "positive": ["14", 0],
                "negative": ["14", 1],
                "latent_image": ["14", 2],
            },
            "class_type": "KSamplerAdvanced",
        },
        "16": {
            "inputs": {
                "add_noise": "disable",
                "noise_seed": seed,
                "steps": 4,
                "cfg": 1.0,
                "sampler_name": "euler",
                "scheduler": "simple",
                "start_at_step": 2,
                "end_at_step": 4,
                "return_with_leftover_noise": "disable",
                "model": ["11", 0],
                "positive": ["14", 0],
                "negative": ["14", 1],
                "latent_image": ["15", 0],
            },
            "class_type": "KSamplerAdvanced",
        },
        "17": {"inputs": {"samples": ["16", 0], "vae": ["5", 0]}, "class_type": "VAEDecode"},
        "18": {
            "inputs": {
                "images": ["17", 0],
                "frame_rate": 16.0,
                "loop_count": 0,
                "filename_prefix": prefix,
                "format": "video/h264-mp4",
                "pingpong": False,
                "save_output": True,
            },
            "class_type": "VHS_VideoCombine",
        },
    }


def prepare_scene_specs(stamp: str) -> list[SceneSpec]:
    ref_dir = ROOT / "_aiops_backend_run_v4" / "i2v_refs"
    return [
        SceneSpec(
            "opening_neon_room",
            ref_dir / "ref_01_neon_room.png",
            "realistic premium business KTV room, preserve the exact neon ceiling and sofa layout, slow cinematic dolly forward, subtle moving club lights, glossy floor reflections, expensive hospitality atmosphere, high-end commercial video, no text, no watermark",
            4.0,
            int(f"27{stamp[-6:]}01"),
        ),
        SceneSpec(
            "owner_private_suite",
            ref_dir / "ref_04_host_from_video.png",
            "real business KTV female owner in a private room, preserve the venue background from the input frame, natural handheld camera push-in, confident operator energy, premium service documentary style, realistic skin and fabric, no text, no watermark",
            5.0,
            int(f"27{stamp[-6:]}02"),
        ),
        SceneSpec(
            "star_ceiling_room",
            ref_dir / "ref_02_star_ceiling_room.png",
            "realistic private business KTV suite, preserve star ceiling, sofa arrangement, black glossy floor and light strips, slow elegant pan from doorway to table, premium reception space, natural reflections, no text, no watermark",
            4.5,
            int(f"27{stamp[-6:]}03"),
        ),
        SceneSpec(
            "service_room_detail",
            ROOT / "素材" / "微信图片_20260527010233.jpg",
            "premium KTV room service detail, preserve the input room layout and lighting, camera glides across sofa, table, microphone and lighting details, clean commercial lens, realistic shadows, refined business reception atmosphere, no text, no watermark",
            4.5,
            int(f"27{stamp[-6:]}04"),
        ),
        SceneSpec(
            "corridor_arrival",
            ROOT / "素材" / "微信图片_20260527010216.jpg",
            "realistic arrival moment in a premium business KTV, preserve the input decoration and lighting, slow forward movement like a client entering the venue, warm service mood, polished commercial photography, no text, no watermark",
            4.5,
            int(f"27{stamp[-6:]}05"),
        ),
        SceneSpec(
            "closing_room_atmosphere",
            ref_dir / "ref_03_room_from_video.png",
            "realistic business KTV private room closing shot, preserve the input room atmosphere, slow pull back showing sofa, table, ceiling light and clean service environment, elegant premium commercial video, no text, no watermark",
            4.0,
            int(f"27{stamp[-6:]}06"),
        ),
    ]


def copy_refs_to_comfy(specs: list[SceneSpec], stamp: str) -> list[tuple[SceneSpec, str]]:
    copied: list[tuple[SceneSpec, str]] = []
    for index, spec in enumerate(specs, start=1):
        suffix = spec.source.suffix.lower() or ".png"
        target_name = f"hq_{stamp}_ref_{index:02d}{suffix}"
        shutil.copy2(spec.source, COMFY_INPUT / target_name)
        copied.append((spec, target_name))
    return copied


def generate_digital_human(comfy_source: Path, run_dir: Path) -> Path:
    print("[stage] submitting MuseTalk digital-human full voiceover", flush=True)
    prompt_id = submit_prompt(musetalk_prompt(comfy_source.name))
    print(f"[comfy] MuseTalk prompt_id={prompt_id}", flush=True)
    wait_for_history(prompt_id, timeout=1200)
    expected = COMFY_OUTPUT / f"{comfy_source.stem}_{comfy_source.stem}.mp4"
    if not expected.exists():
        expected = wait_for_output(f"{comfy_source.stem}_{comfy_source.stem}", timeout=120)
    local_copy = run_dir / "hq_digital_human_full.mp4"
    shutil.copy2(expected, local_copy)
    print(f"[stage] digital human ready: {local_copy}", flush=True)
    return local_copy


def generate_i2v_scenes(stamp: str, run_dir: Path, copied_refs: list[tuple[SceneSpec, str]]) -> list[dict[str, Any]]:
    scenes: list[dict[str, Any]] = []
    width, height, length = 480, 848, 65
    for index, (spec, image_name) in enumerate(copied_refs, start=1):
        prefix = f"aiops_hq_{stamp}_scene_{index:02d}_{spec.name}"
        print(f"[stage] submitting Wan2.2 scene {index}: {spec.name}", flush=True)
        prompt = wan_prompt(
            image_name=image_name,
            positive=spec.prompt,
            prefix=prefix,
            seed=spec.seed,
            width=width,
            height=height,
            length=length,
        )
        prompt_id = submit_prompt(prompt)
        print(f"[comfy] scene {index} prompt_id={prompt_id}", flush=True)
        wait_for_history(prompt_id, timeout=1200)
        output = wait_for_output(prefix, timeout=120)
        local = run_dir / f"scene_{index:02d}_{spec.name}.mp4"
        shutil.copy2(output, local)
        scenes.append(
            {
                "index": index,
                "name": spec.name,
                "prompt": spec.prompt,
                "seed": spec.seed,
                "source_reference": str(spec.source),
                "comfy_input": image_name,
                "comfy_output": str(output),
                "local_output": str(local),
                "target_duration": spec.duration,
            }
        )
        print(f"[stage] scene {index} ready: {local}", flush=True)
    return scenes


def ass_time(seconds: float) -> str:
    centis = int(round(seconds * 100))
    h = centis // 360000
    centis %= 360000
    m = centis // 6000
    centis %= 6000
    s = centis // 100
    c = centis % 100
    return f"{h}:{m:02d}:{s:02d}.{c:02d}"


def make_ass(run_dir: Path, duration: float) -> Path:
    ass = run_dir / "hq_subtitles.ass"
    lines = [
        "[Script Info]",
        "ScriptType: v4.00+",
        "PlayResX: 1080",
        "PlayResY: 1920",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        "Style: Title, Microsoft YaHei, 74, &H00FFFFFF, &H00FFFFFF, &H5A000000, &H65000000, -1, 0, 0, 0, 100, 100, 0, 0, 1, 4, 1, 8, 70, 70, 220, 1",
        "Style: Sub, Microsoft YaHei, 46, &H00FFFFFF, &H00FFFFFF, &H7A000000, &H85000000, -1, 0, 0, 0, 100, 100, 0, 0, 1, 3, 1, 2, 78, 78, 170, 1",
        "Style: CTA, Microsoft YaHei, 58, &H00FFFFFF, &H00FFFFFF, &H78000000, &H90000000, -1, 0, 0, 0, 100, 100, 0, 0, 1, 4, 1, 2, 70, 70, 250, 1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
        f"Dialogue: 2,{ass_time(0)},{ass_time(3.2)},Title,,0,0,0,,商务KTV老板娘\\N真实经营日常",
    ]
    for start, end, text in SUBTITLE_LINES:
        lines.append(f"Dialogue: 1,{ass_time(start)},{ass_time(min(end, duration))},Sub,,0,0,0,,{text}")
    lines.append(f"Dialogue: 2,{ass_time(max(0, duration - 4.8))},{ass_time(duration)},CTA,,0,0,0,,商务接待 · 私密包厢 · 提前预约")
    ass.write_text("\n".join(lines), encoding="utf-8-sig")
    return ass


def make_visual_segments(run_dir: Path, scenes: list[dict[str, Any]], dh_video: Path, duration: float) -> list[Path]:
    timeline = [
        ("scene", 0, 4.0),
        ("dh", 0, 5.5),
        ("scene", 1, 4.5),
        ("dh", 5.5, 5.5),
        ("scene", 2, 4.5),
        ("scene", 3, 4.5),
        ("dh", 20.0, 6.5),
        ("scene", 4, 4.5),
        ("scene", 5, 4.0),
        ("dh", max(0, duration - 5.0), 5.0),
    ]
    total = sum(item[2] for item in timeline)
    if total < duration:
        timeline.append(("scene", 5, duration - total))
    elif total > duration:
        kind, source, seg_dur = timeline[-1]
        timeline[-1] = (kind, source, max(1.0, seg_dur - (total - duration)))

    paths: list[Path] = []
    for idx, (kind, source, seg_dur) in enumerate(timeline, start=1):
        out = run_dir / f"visual_segment_{idx:02d}.mp4"
        if kind == "dh":
            start = float(source)
            run(
                [
                    "ffmpeg",
                    "-y",
                    "-ss",
                    f"{start:.3f}",
                    "-i",
                    str(dh_video),
                    "-t",
                    f"{seg_dur:.3f}",
                    "-vf",
                    "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=25,eq=contrast=1.04:saturation=1.03,unsharp=5:5:0.6:3:3:0.2,format=yuv420p",
                    "-an",
                    "-c:v",
                    "libx264",
                    "-preset",
                    "slow",
                    "-crf",
                    "17",
                    str(out),
                ],
                timeout=240,
            )
        else:
            scene_index = int(source)
            scene_path = Path(str(scenes[scene_index]["local_output"]))
            run(
                [
                    "ffmpeg",
                    "-y",
                    "-stream_loop",
                    "-1",
                    "-i",
                    str(scene_path),
                    "-t",
                    f"{seg_dur:.3f}",
                    "-vf",
                    "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=25,eq=contrast=1.05:saturation=1.08:gamma=0.98,unsharp=5:5:0.55:3:3:0.15,format=yuv420p",
                    "-an",
                    "-c:v",
                    "libx264",
                    "-preset",
                    "slow",
                    "-crf",
                    "17",
                    str(out),
                ],
                timeout=240,
            )
        paths.append(out)
    return paths


def concat_videos(run_dir: Path, segments: list[Path]) -> Path:
    concat_file = run_dir / "concat_visuals.txt"
    concat_file.write_text("\n".join(f"file '{path.as_posix()}'" for path in segments), encoding="utf-8")
    output = run_dir / "hq_visual_concat.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file), "-c", "copy", str(output)], timeout=240)
    return output


def make_bgm_mix(run_dir: Path, voice_wav: Path, duration: float) -> Path:
    bgm = run_dir / "hq_audio_mix.m4a"
    ambient = (
        f"aevalsrc='0.020*sin(2*PI*55*t)+0.012*sin(2*PI*110*t)+0.008*sin(2*PI*220*t)':"
        f"s=44100:d={duration:.3f}"
    )
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(voice_wav),
            "-f",
            "lavfi",
            "-i",
            ambient,
            "-filter_complex",
            "[1:a]volume=0.28,afade=t=in:st=0:d=2,afade=t=out:st="
            + f"{max(0, duration - 3):.3f}:d=3[bg];[0:a]volume=1.08[v];[v][bg]amix=inputs=2:duration=first:dropout_transition=2,loudnorm=I=-15:TP=-1.2:LRA=8[a]",
            "-map",
            "[a]",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            str(bgm),
        ],
        timeout=180,
    )
    return bgm


def burn_subtitles_and_audio(run_dir: Path, visual: Path, audio: Path, ass: Path) -> Path:
    final = run_dir / "business_ktv_hq_promo_final.mp4"
    try:
        ass_filter_path = ass.relative_to(run_dir).as_posix()
    except ValueError:
        ass_filter_path = str(ass).replace("\\", "/").replace(":", "\\:")
    ass_filter = "subtitles=" + ass_filter_path
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(visual),
            "-i",
            str(audio),
            "-vf",
            ass_filter,
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-c:v",
            "libx264",
            "-preset",
            "slow",
            "-crf",
            "17",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-shortest",
            str(final),
        ],
        cwd=run_dir,
        timeout=300,
    )
    return final


def make_preview_and_report(
    *,
    run_dir: Path,
    mirror_dir: Path,
    final: Path,
    scenes: list[dict[str, Any]],
    voice_wav: Path,
    dh_video: Path,
    duration: float,
) -> dict[str, Any]:
    preview = run_dir / "business_ktv_hq_preview_sheet.jpg"
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(final),
            "-vf",
            "fps=1/5,scale=216:384:force_original_aspect_ratio=increase,crop=216:384,tile=3x3",
            "-frames:v",
            "1",
            str(preview),
        ],
        timeout=120,
    )
    mirror_final = mirror_dir / final.name
    mirror_preview = mirror_dir / preview.name
    shutil.copy2(final, mirror_final)
    shutil.copy2(preview, mirror_preview)
    manifest = {
        "title": "商务KTV老板娘真实经营日常高质量宣发视频",
        "generated_at": datetime.now().isoformat(),
        "duration_seconds": duration,
        "resolution": "1080x1920",
        "final_video": str(final),
        "mirror_final_video": str(mirror_final),
        "preview_sheet": str(preview),
        "mirror_preview_sheet": str(mirror_preview),
        "voiceover_audio": str(voice_wav),
        "digital_human_video": str(dh_video),
        "scene_count": len(scenes),
        "scenes": scenes,
        "quality_notes": [
            "Wan2.2 I2V generated material-bound venue scenes from provided KTV references.",
            "MuseTalk generated a full-length synchronized digital-human owner voiceover pass.",
            "Final edit uses 1080x1920 delivery, burned Chinese subtitles, normalized voice, and low ambient music bed.",
            "The current voice is neural TTS; a real recorded or cloned authorized voice can replace it for a more natural final master.",
        ],
    }
    manifest_path = run_dir / "business_ktv_hq_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    shutil.copy2(manifest_path, mirror_dir / manifest_path.name)
    report = run_dir / "business_ktv_hq_report.md"
    report.write_text(
        "\n".join(
            [
                "# Business KTV HQ Promo Generation Report",
                "",
                f"- Final video: `{final}`",
                f"- Mirror final video: `{mirror_final}`",
                f"- Preview sheet: `{preview}`",
                f"- Duration: {duration:.2f}s",
                "- Resolution: 1080x1920",
                "- Story: post-90s KTV female owner explains stable business reception standards.",
                "- Digital human: full voiceover MuseTalk pass from provided portrait.",
                "- Scene generation: Wan2.2 I2V material-bound KTV venue references.",
                "",
                "## Quality Boundary",
                "",
                "This is a production-style backend master generated from the available local models and user materials. "
                "For final paid delivery, replace neural TTS with recorded/authorized cloned voice and optionally rerender selected shots at a slower higher-step workflow.",
            ]
        ),
        encoding="utf-8",
    )
    shutil.copy2(report, mirror_dir / report.name)
    return manifest


async def main() -> None:
    stamp, run_dir, mirror_dir = make_run_dirs()
    print(f"[stage] run_dir={run_dir}", flush=True)
    print(f"[stage] mirror_dir={mirror_dir}", flush=True)

    text_path, voice_wav = await generate_voice(run_dir)
    duration = ffprobe_duration(voice_wav)
    print(f"[stage] voice ready duration={duration:.2f}s text={text_path}", flush=True)

    portrait_source = make_portrait_source(run_dir, voice_wav, duration, stamp)
    dh_video = generate_digital_human(portrait_source, run_dir)

    specs = prepare_scene_specs(stamp)
    copied_refs = copy_refs_to_comfy(specs, stamp)
    scenes = generate_i2v_scenes(stamp, run_dir, copied_refs)

    segments = make_visual_segments(run_dir, scenes, dh_video, duration)
    visual = concat_videos(run_dir, segments)
    audio_mix = make_bgm_mix(run_dir, voice_wav, duration)
    ass = make_ass(run_dir, duration)
    final = burn_subtitles_and_audio(run_dir, visual, audio_mix, ass)
    manifest = make_preview_and_report(
        run_dir=run_dir,
        mirror_dir=mirror_dir,
        final=final,
        scenes=scenes,
        voice_wav=voice_wav,
        dh_video=dh_video,
        duration=duration,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    asyncio.run(main())
