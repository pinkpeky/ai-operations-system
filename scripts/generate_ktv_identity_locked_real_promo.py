"""Generate an identity-locked realistic KTV promo from the provided materials.

This version prioritizes exact person/environment preservation over model
hallucination: full-body person shots come from the provided videos, and the
render only adds stabilization-oriented framing, warm color, soft motion, text,
ambient audio, and gentle fades.
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime
from pathlib import Path


ROOT = Path(r"D:\流程测试")
SOURCE_DIR = ROOT / "素材"
ASCII_ROOT = Path(r"D:\aiops_production_runs")

OUTSIDE_VIDEO = SOURCE_DIR / "微信视频_20260527010402.mp4"
LOBBY_VIDEO = SOURCE_DIR / "微信视频_20260527010319.mp4"
ROOM_WALK_VIDEO = SOURCE_DIR / "微信视频_20260527010327.mp4"
CORRIDOR_PERSON_VIDEO = SOURCE_DIR / "微信视频_20260527010409.mp4"
ROOM_VIDEO_A = SOURCE_DIR / "微信视频_20260527010339.mp4"
ROOM_VIDEO_B = SOURCE_DIR / "微信视频_20260527010348.mp4"
ROOM_VIDEO_C = SOURCE_DIR / "微信视频_20260527010416.mp4"


VIDEO_FILTER = (
    "scale=1080:1920:force_original_aspect_ratio=increase,"
    "crop=1080:1920,fps=25,setsar=1,"
    "colorbalance=rs=0.035:gs=0.012:bs=-0.025:rm=0.018:bm=-0.018,"
    "eq=brightness=0.012:contrast=1.035:saturation=1.055,"
    "unsharp=5:5:0.32:3:3:0.08,format=yuv420p"
)


def run(cmd: list[str], *, cwd: Path | None = None, timeout: int | None = None) -> None:
    print("[cmd]", " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=str(cwd) if cwd else None, check=True, timeout=timeout)


def capture(cmd: list[str], *, timeout: int | None = None) -> str:
    return subprocess.check_output(
        cmd,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )


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
    run_dir = ASCII_ROOT / f"ktv_identity_locked_{stamp}"
    mirror_dir = ROOT / "_aiops_identity_locked" / f"ktv_identity_locked_{stamp}"
    run_dir.mkdir(parents=True, exist_ok=True)
    mirror_dir.mkdir(parents=True, exist_ok=True)
    return stamp, run_dir, mirror_dir


def make_video_clip(
    source: Path,
    output: Path,
    *,
    start: float = 0.0,
    duration: float | None = None,
    crf: int = 17,
) -> Path:
    cmd = ["ffmpeg", "-y"]
    if start > 0:
        cmd += ["-ss", f"{start:.3f}"]
    cmd += ["-i", str(source)]
    if duration is not None:
        cmd += ["-t", f"{duration:.3f}"]
    cmd += [
        "-vf",
        VIDEO_FILTER,
        "-an",
        "-c:v",
        "libx264",
        "-preset",
        "slow",
        "-crf",
        str(crf),
        str(output),
    ]
    run(cmd, timeout=240)
    return output


def make_still_clip(source: Path, run_dir: Path, output: Path, *, at: float, duration: float) -> Path:
    frame = run_dir / f"{output.stem}_source_frame.jpg"
    run(
        [
            "ffmpeg",
            "-y",
            "-ss",
            f"{at:.3f}",
            "-i",
            str(source),
            "-frames:v",
            "1",
            str(frame),
        ],
        timeout=60,
    )
    vf = (
        "scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,"
        "zoompan=z='1.004+0.002*sin(on/18)':"
        "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        "d=1:fps=25:s=1080x1920,"
        "colorbalance=rs=0.035:gs=0.012:bs=-0.025:rm=0.018:bm=-0.018,"
        "eq=brightness=0.012:contrast=1.035:saturation=1.055,"
        "unsharp=5:5:0.28:3:3:0.06,format=yuv420p"
    )
    run(
        [
            "ffmpeg",
            "-y",
            "-loop",
            "1",
            "-framerate",
            "25",
            "-i",
            str(frame),
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


def xfade_sequence(inputs: list[Path], output: Path, *, overlap: float = 0.75) -> Path:
    if len(inputs) == 1:
        run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(inputs[0]),
                "-c:v",
                "libx264",
                "-preset",
                "slow",
                "-crf",
                "17",
                "-an",
                str(output),
            ],
            timeout=180,
        )
        return output

    durations = [ffprobe_duration(path) for path in inputs]
    cmd = ["ffmpeg", "-y"]
    for path in inputs:
        cmd += ["-i", str(path)]

    filters: list[str] = []
    current_label = "0:v"
    current_duration = durations[0]
    final_label = ""
    for index in range(1, len(inputs)):
        label = f"v{index}"
        offset = max(0.1, current_duration - overlap)
        filters.append(
            f"[{current_label}][{index}:v]"
            f"xfade=transition=fade:duration={overlap:.3f}:offset={offset:.3f},"
            f"format=yuv420p[{label}]"
        )
        current_duration = current_duration + durations[index] - overlap
        current_label = label
        final_label = label

    cmd += [
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
    ]
    run(cmd, timeout=300)
    return output


def make_scene_two(run_dir: Path) -> Path:
    lobby = make_video_clip(LOBBY_VIDEO, run_dir / "scene02_01_lobby_entry.mp4", start=0.2, duration=3.8)
    room_walk = make_video_clip(ROOM_WALK_VIDEO, run_dir / "scene02_02_hall_push.mp4", start=0.0, duration=4.5)
    corridor = make_video_clip(
        CORRIDOR_PERSON_VIDEO,
        run_dir / "scene02_03_follow_person_corridor.mp4",
        start=0.2,
        duration=6.4,
    )
    return xfade_sequence([lobby, room_walk, corridor], run_dir / "scene02_enter_and_corridor.mp4", overlap=0.65)


def make_scene_three(run_dir: Path) -> Path:
    room_a = make_video_clip(ROOM_VIDEO_A, run_dir / "scene03_01_room_slow_pan.mp4", start=0.0, duration=3.8)
    room_b = make_video_clip(ROOM_VIDEO_B, run_dir / "scene03_02_room_detail.mp4", start=0.0, duration=2.6)
    room_c = make_video_clip(LOBBY_VIDEO, run_dir / "scene03_03_lobby_reveal.mp4", start=1.0, duration=4.2)
    return xfade_sequence([room_a, room_b, room_c], run_dir / "scene03_room_and_lounge.mp4", overlap=0.7)


def create_ambient_audio(run_dir: Path, duration: float) -> Path:
    audio = run_dir / "identity_locked_ambient.m4a"
    ambient = (
        "aevalsrc='0.010*sin(2*PI*72*t)+0.007*sin(2*PI*144*t)+"
        "0.004*sin(2*PI*216*t)':s=44100:"
        f"d={duration:.3f}"
    )
    run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            ambient,
            "-af",
            f"afade=t=in:st=0:d=1.5,afade=t=out:st={max(0, duration - 2.0):.3f}:d=2,"
            "acompressor=threshold=-22dB:ratio=1.6:attack=20:release=220,loudnorm=I=-25:TP=-2:LRA=10",
            "-c:a",
            "aac",
            "-b:a",
            "160k",
            str(audio),
        ],
        timeout=120,
    )
    return audio


def ass_time(seconds: float) -> str:
    centiseconds = int(round(seconds * 100))
    cs = centiseconds % 100
    total_seconds = centiseconds // 100
    s = total_seconds % 60
    total_minutes = total_seconds // 60
    m = total_minutes % 60
    h = total_minutes // 60
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def create_subtitles(run_dir: Path, duration: float) -> Path:
    ass = run_dir / "identity_story.ass"
    lines = [
        (0.0, 4.8, "真实日常 · 商务KTV"),
        (5.3, 13.2, "从门口到包间，动线自然，氛围稳定"),
        (14.2, 22.2, "暖光包间，适合小聚与商务接待"),
        (23.3, min(duration - 1.0, 30.5), "今晚，把人带来，剩下的交给我们"),
    ]
    events = "\n".join(
        f"Dialogue: 1,{ass_time(start)},{ass_time(end)},Sub,,0,0,0,,{text}"
        for start, end, text in lines
        if end > start
    )
    ass.write_text(
        "\n".join(
            [
                "[Script Info]",
                "ScriptType: v4.00+",
                "PlayResX: 1080",
                "PlayResY: 1920",
                "",
                "[V4+ Styles]",
                (
                    "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
                    "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, "
                    "ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
                    "Alignment, MarginL, MarginR, MarginV, Encoding"
                ),
                (
                    "Style: Sub, Microsoft YaHei, 46, &H00FFFFFF, &H00FFFFFF, "
                    "&H86000000, &H8A000000, -1, 0, 0, 0, 100, 100, 0, 0, "
                    "1, 3, 1, 2, 70, 70, 160, 1"
                ),
                "",
                "[Events]",
                "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
                events,
                "",
            ]
        ),
        encoding="utf-8",
    )
    return ass


def render_final(run_dir: Path, visual: Path, audio: Path, ass: Path, duration: float) -> Path:
    final = run_dir / "business_ktv_identity_locked_real_promo.mp4"
    vf = f"subtitles={ass.name},fade=t=out:st={max(0, duration - 2.0):.3f}:d=2"
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
            "160k",
            "-shortest",
            str(final),
        ],
        cwd=run_dir,
        timeout=300,
    )
    return final


def make_preview_and_manifest(run_dir: Path, mirror_dir: Path, final: Path, visual: Path) -> None:
    preview = run_dir / "identity_locked_preview_sheet.jpg"
    probe = run_dir / "identity_locked_ffprobe.json"
    report = run_dir / "identity_locked_report.md"
    manifest = run_dir / "identity_locked_manifest.json"

    probe_json = capture(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration,size,bit_rate",
            "-show_streams",
            "-of",
            "json",
            str(final),
        ],
        timeout=60,
    )
    probe.write_text(probe_json, encoding="utf-8")
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(final),
            "-vf",
            "fps=1/4,scale=216:384:force_original_aspect_ratio=increase,crop=216:384,tile=3x3",
            "-frames:v",
            "1",
            str(preview),
        ],
        timeout=120,
    )

    final_hash = capture(["powershell", "-NoProfile", "-Command", f"(Get-FileHash -LiteralPath '{final}' -Algorithm SHA256).Hash"]).strip()
    data = {
        "status": "complete",
        "theme": "商务KTV宣传视频",
        "mode": "identity_locked_realistic_storyboard",
        "final_video": str(final),
        "mirror_video": str(mirror_dir / final.name),
        "preview_sheet": str(preview),
        "ffprobe": str(probe),
        "sha256": final_hash,
        "source_policy": "人物全身和场景来自用户提供素材，避免重画脸和衣服。",
        "storyboard": [
            "门外招牌下固定镜头，轻微呼吸式微动",
            "大厅到走廊，跟随人物进入，平稳推进",
            "厅内/包间环境慢速展示，暖色真实氛围",
            "回到主角全身镜头，淡出结束",
        ],
    }
    manifest.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    report.write_text(
        "\n".join(
            [
                "# 身份锁定版真实宣传片交付说明",
                "",
                "状态：已完成",
                "",
                f"- 成片：{final}",
                f"- 同步目录：{mirror_dir / final.name}",
                f"- 预览九宫格：{preview}",
                f"- 质检信息：{probe}",
                "",
                "这版优先解决上一版的问题：不使用头像口播数字人，不让模型重新生成主角脸和衣服；主角全身、门外、走廊、厅内均来自用户提供素材。",
                "处理只包含：竖屏统一、暖色调、柔和稳定、轻微呼吸式运动、慢节奏转场、环境氛围音和少量宣传字幕。",
                "",
                "限制：素材中没有明确的“几个朋友坐沙发聊天”实拍参考，因此本版没有强行生成随机朋友，避免再次出现不连贯和无厘头人物。",
                "",
            ]
        ),
        encoding="utf-8",
    )

    for artifact in [final, preview, probe, report, manifest]:
        target = mirror_dir / artifact.name
        target.write_bytes(artifact.read_bytes())


def main() -> None:
    stamp, run_dir, mirror_dir = make_run_dirs()
    print(f"[stage] stamp={stamp}", flush=True)
    print(f"[stage] run_dir={run_dir}", flush=True)
    print(f"[stage] mirror_dir={mirror_dir}", flush=True)

    scene1 = make_still_clip(
        OUTSIDE_VIDEO,
        run_dir,
        run_dir / "scene01_outside_sign_identity_locked.mp4",
        at=2.2,
        duration=5.4,
    )
    print(f"[stage] scene1 ready: {scene1}", flush=True)

    scene2 = make_scene_two(run_dir)
    print(f"[stage] scene2 ready: {scene2}", flush=True)

    scene3 = make_scene_three(run_dir)
    print(f"[stage] scene3 ready: {scene3}", flush=True)

    scene4 = make_video_clip(ROOM_VIDEO_C, run_dir / "scene04_host_full_body_final.mp4", start=0.0, duration=6.9)
    print(f"[stage] scene4 ready: {scene4}", flush=True)

    visual = xfade_sequence([scene1, scene2, scene3, scene4], run_dir / "identity_locked_visual_story.mp4", overlap=0.8)
    duration = ffprobe_duration(visual)
    audio = create_ambient_audio(run_dir, duration)
    ass = create_subtitles(run_dir, duration)
    final = render_final(run_dir, visual, audio, ass, duration)
    make_preview_and_manifest(run_dir, mirror_dir, final, visual)
    print(json.dumps({"final": str(final), "mirror": str(mirror_dir / final.name)}, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
