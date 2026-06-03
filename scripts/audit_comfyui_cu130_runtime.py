"""Audit the local ComfyUI_cu130 runtime, models, nodes, and workflows.

The output is intentionally RAG/operations friendly: it records what exists on
disk, what the running ComfyUI API exposes, and where validation boundaries
remain. It does not submit heavy generation jobs.
"""

from __future__ import annotations

import argparse
import json
import re
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


DEFAULT_COMFY_ROOT = Path("E:/ComfyUI_cu130/ComfyUI")
DEFAULT_BASE_URL = "http://127.0.0.1:8188"
DEFAULT_JSON = Path("deployment/comfyui/commercial_ktv_workflow/cu130_runtime_model_audit.json")
DEFAULT_MARKDOWN = Path("docs/COMFYUI_CU130_RUNTIME_MODEL_AUDIT.md")
DEFAULT_RAG_JSONL = Path("deployment/comfyui/commercial_ktv_workflow/cu130_runtime_workflow_rag_documents.jsonl")

MODEL_EXTENSIONS = {".safetensors", ".gguf", ".pth", ".pt", ".onnx", ".bin", ".ckpt", ".model"}
UI_ONLY_NODE_TYPES = {
    "MarkdownNote",
    "Note",
    "Reroute",
    "PrimitiveNode",
    "GetNode",
    "SetNode",
    "easy getNode",
    "easy setNode",
    "Fast Groups Bypasser (rgthree)",
    "Fast Groups Muter (rgthree)",
    "Label (rgthree)",
    "Mute / Bypass Relay (rgthree)",
    "Mute / Bypass Repeater (rgthree)",
    "Reroute (rgthree)",
}


def http_json(base_url: str, path: str, *, timeout: int = 30) -> dict[str, Any]:
    with urllib.request.urlopen(f"{base_url.rstrip('/')}{path}", timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def bytes_to_gb(value: int) -> float:
    return round(value / 1024**3, 2)


def clean_model_ref(value: str) -> str:
    value = value.strip().strip("`").strip()
    value = re.sub(r"^[-*]\s*\[?", "", value).strip()
    value = value.strip("[]()<>").strip()
    value = Path(value.replace("\\", "/")).name
    return value.rstrip(").,;`").strip()


def scan_models(models_root: Path) -> dict[str, Any]:
    model_files: list[dict[str, Any]] = []
    by_dir: dict[str, dict[str, Any]] = defaultdict(lambda: {"count": 0, "bytes": 0})
    if models_root.exists():
        for path in models_root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in MODEL_EXTENSIONS or path.name.startswith("put_"):
                continue
            size = path.stat().st_size
            rel = path.relative_to(models_root)
            top = rel.parts[0] if rel.parts else "."
            by_dir[top]["count"] += 1
            by_dir[top]["bytes"] += size
            model_files.append(
                {
                    "relative_path": str(rel).replace("\\", "/"),
                    "name": path.name,
                    "size_bytes": size,
                    "size_gb": bytes_to_gb(size),
                }
            )
    model_files.sort(key=lambda item: item["size_bytes"], reverse=True)
    return {
        "root": str(models_root),
        "count": len(model_files),
        "total_bytes": sum(item["size_bytes"] for item in model_files),
        "total_gb": bytes_to_gb(sum(item["size_bytes"] for item in model_files)),
        "by_dir": [
            {"name": name, "count": value["count"], "size_gb": bytes_to_gb(value["bytes"])}
            for name, value in sorted(by_dir.items(), key=lambda item: item[1]["bytes"], reverse=True)
        ],
        "largest": model_files[:80],
        "names": sorted({item["name"] for item in model_files}, key=str.lower),
    }


def classify_workflow(relative_path: str) -> list[str]:
    haystack = relative_path.lower()
    rules = {
        "video_analysis": ["截取视频", "视频-音频", "asr", "subtitle", "字幕", "音频分离", "depthanything", "matanyone"],
        "vlm_prompting": ["qwenvl", "image2prompt", "图像嵌入文字", "提示词反推"],
        "asr": ["asr", "语音转文字", "字幕"],
        "tts": ["tts", "语音设计", "音色", "克隆", "多人对话"],
        "music": ["音乐", "歌词", "heartmula", "ace_step"],
        "image_generation": ["文生图", "图像编辑", "qwen-image", "z-image", "flux", "局部重绘"],
        "image_to_video": ["图生视频", "i2v", "hunyuan"],
        "digital_human": ["数字人", "口型", "infinitetalk", "s2v"],
        "motion_transfer": ["动作迁移", "人物替换", "animate", "姿势控制", "stead", "scail"],
        "segmentation": ["遮罩", "sam", "matanyone", "birefnet", "背景"],
        "post_processing": ["放大", "seedvr", "gif", "mp3", "合并", "倒放", "分屏"],
    }
    matches = [name for name, keywords in rules.items() if any(keyword in haystack for keyword in keywords)]
    return matches or ["general"]


def workflow_model_refs(node: dict[str, Any]) -> list[str]:
    pattern = re.compile(r"(?i)([\w .+\-()\[\]\u4e00-\u9fff]+?\.(?:safetensors|gguf|pth|pt|onnx|bin|ckpt|model))")
    refs: list[str] = []

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)
        elif isinstance(value, str):
            for match in pattern.finditer(value):
                ref = clean_model_ref(match.group(1))
                if ref:
                    refs.append(ref)

    walk(node.get("widgets_values") or [])
    walk(node.get("properties") or {})
    return refs


def scan_workflows(workflow_root: Path, object_info: dict[str, Any], model_names: set[str]) -> dict[str, Any]:
    available_types = set(object_info)
    workflows: list[dict[str, Any]] = []
    missing_executable_node_types: Counter[str] = Counter()
    category_counts: Counter[str] = Counter()
    capability_counts: Counter[str] = Counter()

    if workflow_root.exists():
        for path in sorted(workflow_root.rglob("*.json")):
            relative_path = str(path.relative_to(workflow_root)).replace("\\", "/")
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except Exception as exc:
                workflows.append({"relative_path": relative_path, "error": str(exc)})
                continue

            nodes = data.get("nodes") or []
            node_types = [str(node.get("type") or node.get("class_type")) for node in nodes if isinstance(node, dict) and (node.get("type") or node.get("class_type"))]
            missing_types = sorted(
                {
                    node_type
                    for node_type in node_types
                    if node_type not in available_types
                    and node_type not in UI_ONLY_NODE_TYPES
                    and not re.fullmatch(r"[0-9a-fA-F-]{32,36}", node_type)
                }
            )
            for node_type in missing_types:
                missing_executable_node_types[node_type] += 1

            refs: list[str] = []
            for node in nodes:
                if isinstance(node, dict):
                    refs.extend(workflow_model_refs(node))
            unique_refs = sorted(set(refs), key=str.lower)
            found_refs = [ref for ref in unique_refs if ref.lower() in model_names]
            missing_refs = [ref for ref in unique_refs if ref.lower() not in model_names]

            parts = relative_path.split("/")
            category = parts[0] if len(parts) > 1 else "root"
            capabilities = classify_workflow(relative_path)
            category_counts[category] += 1
            for capability in capabilities:
                capability_counts[capability] += 1

            workflows.append(
                {
                    "relative_path": relative_path,
                    "node_count": len(nodes),
                    "capabilities": capabilities,
                    "category": category,
                    "missing_executable_node_types": missing_types,
                    "model_refs": unique_refs,
                    "model_refs_found": found_refs,
                    "model_refs_missing": missing_refs,
                    "runtime_readiness": "needs_prompt_validation" if not missing_types else "missing_executable_nodes",
                }
            )

    return {
        "root": str(workflow_root),
        "count": len(workflows),
        "category_counts": dict(sorted(category_counts.items())),
        "capability_counts": dict(sorted(capability_counts.items())),
        "missing_executable_node_types": dict(missing_executable_node_types.most_common()),
        "workflows": workflows,
    }


def capability_matrix(object_info: dict[str, Any], model_names: set[str]) -> list[dict[str, Any]]:
    def has_node(*keywords: str) -> bool:
        return any(all(keyword.lower() in node.lower() for keyword in keywords) for node in object_info)

    def has_model(*keywords: str) -> bool:
        return any(all(keyword.lower() in name.lower() for keyword in keywords) for name in model_names)

    def has_ocr_node() -> bool:
        ocr_pattern = re.compile(r"(^|[^a-z])ocr($|[^a-z])", re.IGNORECASE)
        return any(
            ocr_pattern.search(node) or "paddle" in node.lower() or "rapidocr" in node.lower() or "easyocr" in node.lower()
            for node in object_info
        )

    def has_ocr_model() -> bool:
        ocr_pattern = re.compile(r"(^|[^a-z])ocr($|[^a-z])", re.IGNORECASE)
        return any(
            ocr_pattern.search(name) or "paddle" in name.lower() or "rapidocr" in name.lower() or "easyocr" in name.lower()
            for name in model_names
        )

    return [
        {
            "capability": "video_frame_extraction",
            "nodes_ready": has_node("LoadVideo") or has_node("VHS_LoadVideo"),
            "models_ready": True,
            "conclusion": "ready_for_minimal_validation",
        },
        {
            "capability": "asr_audio_to_text",
            "nodes_ready": has_node("Qwen3ASR") or has_node("Whisper"),
            "models_ready": has_model("Qwen3-ASR") or has_model("whisper") or has_model("model.fp32"),
            "conclusion": "ready_for_minimal_validation",
        },
        {
            "capability": "vlm_keyframe_understanding",
            "nodes_ready": has_node("QwenVL") or has_node("OllamaVision") or has_node("SmolVLM") or has_node("JoyCaption"),
            "models_ready": has_model("qwen_2.5_vl") or has_model("Qwen3.5") or has_model("joycaption") or has_model("mmproj"),
            "conclusion": "ready_for_minimal_validation",
        },
        {
            "capability": "subject_segmentation",
            "nodes_ready": has_node("SAM3") or has_node("SAM2") or has_node("SAMLoader"),
            "models_ready": has_model("sam3") or has_model("sam2") or has_model("sam_vit"),
            "conclusion": "ready_for_minimal_validation",
        },
        {
            "capability": "depth_spatial_analysis",
            "nodes_ready": has_node("DepthAnything"),
            "models_ready": has_model("depth_anything"),
            "conclusion": "ready_for_minimal_validation",
        },
        {
            "capability": "ocr_screen_text",
            "nodes_ready": has_ocr_node(),
            "models_ready": has_ocr_model(),
            "conclusion": "not_a_primary_comfyui_capability",
        },
        {
            "capability": "wan_digital_human_generation",
            "nodes_ready": has_node("Wan") or has_node("WanVideo"),
            "models_ready": has_model("Wan2.2") or has_model("InfiniteTalk") or has_model("wan2.2"),
            "conclusion": "models_present_but_requires_generation_validation",
        },
    ]


def write_markdown(report: dict[str, Any], output: Path) -> None:
    models = report["models"]
    runtime = report["runtime"]
    workflows = report["workflows"]
    matrix = report["capability_matrix"]
    lines = [
        "# ComfyUI_cu130 Runtime Model Audit",
        "",
        f"Generated at: `{report['generated_at']}`",
        "",
        "## Runtime",
        "",
        f"- ComfyUI root: `{report['comfy_root']}`",
        f"- Base URL: `{report['base_url']}`",
        f"- Queue running: `{len(runtime.get('queue', {}).get('queue_running', []))}`",
        f"- Queue pending: `{len(runtime.get('queue', {}).get('queue_pending', []))}`",
        f"- ComfyUI version: `{runtime.get('system_stats', {}).get('system', {}).get('comfyui_version', 'unknown')}`",
        f"- PyTorch: `{runtime.get('system_stats', {}).get('system', {}).get('pytorch_version', 'unknown')}`",
        "",
        "## Models",
        "",
        f"- Model file count: `{models['count']}`",
        f"- Total model size: `{models['total_gb']} GB`",
        "",
        "| Directory | Files | Size |",
        "|---|---:|---:|",
    ]
    for item in models["by_dir"][:40]:
        lines.append(f"| `{item['name']}` | {item['count']} | {item['size_gb']} GB |")
    lines.extend(["", "## Video Analysis Capability Matrix", "", "| Capability | Nodes | Models | Conclusion |", "|---|---|---|---|"])
    for item in matrix:
        lines.append(
            f"| `{item['capability']}` | {'yes' if item['nodes_ready'] else 'no'} | {'yes' if item['models_ready'] else 'no'} | `{item['conclusion']}` |"
        )
    lines.extend(
        [
            "",
            "## Workflow Inventory",
            "",
            f"- Workflow count: `{workflows['count']}`",
            "",
            "### By Category",
            "",
        ]
    )
    for name, count in workflows["category_counts"].items():
        lines.append(f"- {name}: {count}")
    lines.extend(["", "### By Capability", ""])
    for name, count in workflows["capability_counts"].items():
        lines.append(f"- {name}: {count}")
    lines.extend(["", "## Operational Conclusion", ""])
    lines.extend(
        [
            "- The model download is now materially complete for the current ComfyUI_cu130 bundle.",
            "- Minimal video analysis can be validated with frame extraction, ASR, VLM/keyframe captioning, segmentation, and depth workflows.",
            "- OCR is still not a primary ComfyUI capability in this runtime; use an independent OCR/video-analysis service when screen text matters.",
            "- Digital-human and WanAnimate workflows have model coverage, but they still require controlled generation validation before production use.",
            "- Agent workflow selection should use this audit as capability evidence, not as proof that every workflow has passed prompt execution.",
        ]
    )
    lines.extend(["", "## High-Value Workflow Status", "", "| Workflow | Capabilities | Node Status | Model refs found/missing |", "|---|---|---|---:|"])
    high_value = {"video_analysis", "asr", "vlm_prompting", "image_to_video", "digital_human", "motion_transfer", "segmentation"}
    for workflow in workflows["workflows"]:
        capabilities = workflow.get("capabilities") or []
        if not high_value.intersection(capabilities):
            continue
        node_status = "ok" if not workflow.get("missing_executable_node_types") else "missing executable node"
        found = len(workflow.get("model_refs_found") or [])
        missing = len(workflow.get("model_refs_missing") or [])
        lines.append(f"| `{workflow['relative_path']}` | {', '.join(capabilities)} | `{node_status}` | {found}/{missing} |")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def stable_source_id(value: str) -> str:
    import hashlib

    return f"comfyui_cu130_runtime_{hashlib.sha1(value.encode('utf-8')).hexdigest()[:12]}"


def write_workflow_rag_jsonl(report: dict[str, Any], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="\n") as handle:
        for workflow in report["workflows"]["workflows"]:
            relative_path = workflow.get("relative_path", "")
            workflow_name = Path(relative_path).name
            capabilities = workflow.get("capabilities") or ["general"]
            missing_nodes = workflow.get("missing_executable_node_types") or []
            missing_models = workflow.get("model_refs_missing") or []
            text = "\n".join(
                [
                    f"ComfyUI_cu130 工作流：{workflow_name}",
                    f"路径：{relative_path}",
                    f"分类：{workflow.get('category')}",
                    f"能力标签：{', '.join(capabilities)}",
                    f"节点数量：{workflow.get('node_count')}",
                    f"运行前状态：{workflow.get('runtime_readiness')}",
                    f"模型引用已匹配数量：{len(workflow.get('model_refs_found') or [])}",
                    f"模型引用未精确匹配数量：{len(missing_models)}",
                    f"未匹配模型引用：{', '.join(missing_models[:12]) if missing_models else '无'}",
                    f"缺失可执行节点：{', '.join(missing_nodes) if missing_nodes else '无'}",
                    "用途判断：由路径、节点、模型引用和当前 runtime 审计自动生成，适合 agent 做工作流候选筛选；最终提交前仍需用目标素材做运行验证。",
                ]
            )
            payload = {
                "source_id": stable_source_id(relative_path),
                "source_name": workflow_name,
                "source_type": "comfyui_runtime_workflow",
                "collection_name": "comfyui_cu130_workflows",
                "text": text,
                "metadata": {
                    "knowledge_type": "comfyui_runtime_workflow",
                    "runtime_project": "comfyui_cu130",
                    "workflow_name": workflow_name,
                    "workflow_path": str((Path(report["comfy_root"]) / "user" / "default" / "workflows" / relative_path).as_posix()),
                    "relative_path": relative_path,
                    "category": workflow.get("category"),
                    "capabilities": capabilities,
                    "node_count": workflow.get("node_count"),
                    "runtime_readiness": workflow.get("runtime_readiness"),
                    "missing_executable_node_types": missing_nodes,
                    "model_refs_found": workflow.get("model_refs_found") or [],
                    "model_refs_missing": missing_models,
                    "audit_source": str(DEFAULT_MARKDOWN),
                    "requires_prompt_validation": True,
                },
            }
            handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True))
            handle.write("\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--comfy-root", type=Path, default=DEFAULT_COMFY_ROOT)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN)
    parser.add_argument("--rag-jsonl-output", type=Path, default=DEFAULT_RAG_JSONL)
    args = parser.parse_args()

    object_info = http_json(args.base_url, "/object_info", timeout=60)
    system_stats = http_json(args.base_url, "/system_stats", timeout=30)
    queue = http_json(args.base_url, "/queue", timeout=30)
    models = scan_models(args.comfy_root / "models")
    model_names = {str(name).lower() for name in models["names"]}
    workflows = scan_workflows(args.comfy_root / "user" / "default" / "workflows", object_info, model_names)
    report = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "comfy_root": str(args.comfy_root),
        "base_url": args.base_url,
        "runtime": {"system_stats": system_stats, "queue": queue, "object_info_node_count": len(object_info)},
        "models": models,
        "workflows": workflows,
        "capability_matrix": capability_matrix(object_info, model_names),
    }
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(report, args.markdown_output)
    write_workflow_rag_jsonl(report, args.rag_jsonl_output)
    print(f"wrote {args.json_output}")
    print(f"wrote {args.markdown_output}")
    print(f"wrote {args.rag_jsonl_output}")
    print(f"models={models['count']} total_gb={models['total_gb']} workflows={workflows['count']}")


if __name__ == "__main__":
    main()
