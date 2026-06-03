"""Generate a local video-agent planning artifact for the original KTV request."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.commercial_operations.video_agent import CommercialVideoAgent  # noqa: E402


DEFAULT_SCENE_IMAGE = PROJECT_ROOT / "douyin_frames" / "frame_004.jpg"
DEFAULT_SOURCE_VIDEO = PROJECT_ROOT / "douyin_7575632283172932870.mp4"
DEFAULT_OUTPUT = (
    PROJECT_ROOT
    / "deployment"
    / "comfyui"
    / "commercial_ktv_workflow"
    / "original_douyin_requirement_video_agent_output.json"
)


def file_uri(path: Path) -> str:
    return path.resolve().as_uri()


def build_payload(scene_image: Path, source_video: Path | None) -> dict[str, Any]:
    return CommercialVideoAgent().plan(
        operation={
            "id": "local-original-douyin-requirement",
            "workspace_id": "local-runtime",
            "title": "Original Douyin KTV AI virtual-host video requirement",
            "objective": (
                "Use one KTV scene image to generate a same-scene Douyin vertical video with a fictional "
                "AI female virtual host, without using a real-person portrait cutout."
            ),
        },
        request_context={
            "channel": "short_video",
            "target_channels": ["douyin"],
            "style": "KTV commercial short video, realistic scene, fictional AI host",
            "scene_image_uri": file_uri(scene_image),
            "source_video_uri": file_uri(source_video) if source_video and source_video.exists() else None,
            "needs_ai_virtual_person": True,
            "allow_real_person_cutout": False,
            "aspect_ratio": "9:16",
            "duration_seconds": 12,
            "metadata": {
                "reference_video_intent": "structure_learning",
                "original_requirement": (
                    "A single scene image should generate a same-scene video with an AI virtual beauty/digital human."
                ),
            },
        },
        rag_context={
            "used_retrieval": False,
            "rag_result_count": 0,
            "query": "KTV Douyin scene image AI virtual female host digital human video workflow",
            "collection_name": "comfyui_cu130_workflows",
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the commercial video Agent against the original KTV requirement.")
    parser.add_argument("--scene-image", type=Path, default=DEFAULT_SCENE_IMAGE)
    parser.add_argument("--source-video", type=Path, default=DEFAULT_SOURCE_VIDEO)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    if not args.scene_image.exists():
        raise FileNotFoundError(f"Scene image not found: {args.scene_image}")
    payload = build_payload(args.scene_image, args.source_video)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    selection = payload["workflow_selection"]["selected_by_stage"]
    summary = {
        "output": str(args.output),
        "status": payload["execution_package"]["status"],
        "workflow_candidate_count": payload["workflow_selection"]["candidate_count"],
        "primary_digital_human_workflow": selection["digital_human_i2v"]["selected"][0]["workflow_name"],
        "primary_ai_host_seed_workflow": selection["ai_virtual_host_seed"]["selected"][0]["workflow_name"],
        "blocking_conditions": payload["execution_package"]["readiness"]["blocking_conditions"],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
