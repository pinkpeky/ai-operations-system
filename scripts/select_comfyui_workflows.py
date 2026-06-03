"""Rank ComfyUI workflow knowledge documents for an operation brief.

This CLI is the lightweight deterministic bridge used by operators and tests.
The production video Agent has richer stage-aware selection in
``app.commercial_operations.video_agent``; this script keeps a simple
query-to-candidate view for quick inspection.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


DEFAULT_KNOWLEDGE = Path("deployment/comfyui/commercial_ktv_workflow/cu130_runtime_workflow_rag_documents.jsonl")

CAPABILITY_KEYWORDS = {
    "video_analysis": [
        "video analysis",
        "reference video",
        "frame extraction",
        "shot analysis",
        "视频解析",
        "参考视频",
        "抽帧",
        "分镜",
        "字幕",
        "解析",
    ],
    "asr": ["asr", "speech to text", "transcript", "voice recognition", "语音转文字", "字幕", "口播提取"],
    "tts": ["tts", "voiceover", "voice clone", "配音", "旁白", "音色", "声音"],
    "music": ["music", "bgm", "song", "音乐", "歌词", "伴奏"],
    "music_generation": ["music generation", "bgm", "song", "音乐生成", "歌词", "伴奏"],
    "digital_human": [
        "digital human",
        "virtual host",
        "ai host",
        "talking host",
        "lip sync",
        "spokesperson",
        "数字人",
        "口播",
        "口型",
        "对口型",
        "虚拟人",
        "主持人",
        "美女",
        "带货",
    ],
    "digital_human_lip_sync": [
        "digital human",
        "virtual host",
        "lip sync",
        "infinitetalk",
        "口播",
        "口型",
        "对口型",
        "数字人",
    ],
    "image_generation": [
        "image generation",
        "qwen image edit",
        "image edit",
        "virtual beauty",
        "ai female host",
        "keyframe",
        "scene image",
        "文生图",
        "图像生成",
        "图像编辑",
        "虚拟美女",
        "首帧",
        "参考图",
        "场景图",
    ],
    "image_to_video": [
        "image to video",
        "i2v",
        "single image video",
        "first frame",
        "图生视频",
        "单图",
        "场景图",
        "首帧",
    ],
    "motion_transfer": [
        "motion transfer",
        "action transfer",
        "character replacement",
        "reference motion",
        "动作迁移",
        "人物替换",
        "动作模仿",
        "参考动作",
        "跳舞",
    ],
    "segmentation": ["segmentation", "mask", "matte", "background removal", "遮罩", "分割", "抠图", "去背景", "主体"],
    "subject_segmentation": ["subject segmentation", "mask", "matte", "遮罩", "分割", "主体"],
    "depth_control": ["depth", "spatial", "深度", "空间", "景深"],
    "post_processing": [
        "post processing",
        "assembly",
        "merge",
        "subtitle",
        "upscale",
        "transcode",
        "合并",
        "分屏",
        "字幕",
        "转码",
        "放大",
        "补帧",
    ],
}

PROJECT_KEYWORDS = {
    "ktv": ["ktv", "night venue", "private room", "商务ktv", "夜场", "包厢", "商务招待"],
    "local_life": ["local life", "store visit", "到店", "门店", "探店", "团购"],
    "ecommerce": ["ecommerce", "product", "conversion", "电商", "带货", "商品", "转化", "下单"],
    "brand": ["brand", "promo", "品牌", "宣传片", "形象", "招商"],
    "education": ["education", "course", "tutorial", "课程", "教育", "讲解", "知识"],
}


def _load_documents(path: Path) -> list[dict[str, Any]]:
    documents: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            clean = line.strip()
            if clean:
                documents.append(json.loads(clean))
    return documents


def _tokens(text: str) -> set[str]:
    normalized = re.sub(r"[\s,，。；;：:、\\|/()[\]{}<>\"']+", " ", text.lower())
    return {part for part in normalized.split(" ") if part}


def _detect_capabilities(query: str) -> set[str]:
    query_lower = query.lower()
    detected = {
        capability
        for capability, keywords in CAPABILITY_KEYWORDS.items()
        if any(keyword.lower() in query_lower for keyword in keywords)
    }
    if "digital_human_lip_sync" in detected:
        detected.add("digital_human")
    return detected


def _detect_project_types(query: str) -> set[str]:
    query_lower = query.lower()
    return {
        project_type
        for project_type, keywords in PROJECT_KEYWORDS.items()
        if any(keyword.lower() in query_lower for keyword in keywords)
    }


def rank_workflows(query: str, documents: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    requested_capabilities = _detect_capabilities(query)
    requested_project_types = _detect_project_types(query)
    query_tokens = _tokens(query)
    ranked: list[dict[str, Any]] = []

    for document in documents:
        metadata = document.get("metadata", {})
        capabilities = set(metadata.get("capabilities", []))
        project_types = set(metadata.get("project_types", []))
        text = " ".join(
            [
                str(document.get("text") or ""),
                str(metadata.get("workflow_name") or ""),
                str(metadata.get("category") or ""),
                " ".join(str(item) for item in metadata.get("model_refs_found", []) or []),
            ]
        )
        text_tokens = _tokens(text)
        score = 0.0
        reasons: list[str] = []

        capability_hits = sorted(requested_capabilities & capabilities)
        if capability_hits:
            score += 8.0 * len(capability_hits)
            reasons.append(f"capability match: {', '.join(capability_hits)}")
        if requested_capabilities and requested_capabilities <= capabilities:
            score += 10.0
            reasons.append("all requested capabilities matched")

        project_hits = sorted(requested_project_types & project_types)
        if project_hits:
            score += 3.0 * len(project_hits)
            reasons.append(f"project type match: {', '.join(project_hits)}")

        lexical_hits = sorted(query_tokens & text_tokens)
        if lexical_hits:
            score += min(len(lexical_hits), 8)
            reasons.append(f"keyword overlap: {', '.join(lexical_hits[:8])}")

        missing_models = metadata.get("model_refs_missing", []) or []
        if metadata.get("workflow_path"):
            score += 0.5
        if not missing_models:
            score += 1.5
            reasons.append("model references matched by runtime audit")
        else:
            score -= min(len(missing_models), 6)
            reasons.append(f"missing model references: {len(missing_models)}")
        if metadata.get("requires_prompt_validation"):
            reasons.append("requires target-material prompt validation before submission")

        if score <= 0:
            continue
        ranked.append(
            {
                "score": round(score, 2),
                "workflow_id": metadata.get("workflow_id") or document.get("source_id"),
                "workflow_name": metadata.get("workflow_name") or document.get("source_name"),
                "category": metadata.get("category"),
                "capabilities": sorted(capabilities),
                "content_modes": metadata.get("content_modes", []),
                "project_types": sorted(project_types),
                "input_contract": metadata.get("input_contract"),
                "output_contract": metadata.get("output_contract"),
                "workflow_path": metadata.get("workflow_path"),
                "model_refs_missing": missing_models,
                "reasons": reasons,
            }
        )

    ranked.sort(key=lambda item: item["score"], reverse=True)
    return ranked[:limit]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("query", help="Operation brief or workflow selection query.")
    parser.add_argument("--knowledge", type=Path, default=DEFAULT_KNOWLEDGE)
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args()

    documents = _load_documents(args.knowledge)
    result = {
        "query": args.query,
        "knowledge_path": str(args.knowledge),
        "candidate_count": len(documents),
        "detected_capabilities": sorted(_detect_capabilities(args.query)),
        "selected": rank_workflows(args.query, documents, args.limit),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
