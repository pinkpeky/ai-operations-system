"""Build RAG-ready ComfyUI workflow knowledge documents.

The source of truth for semantic descriptions is the curated Markdown guide.
The generated JSONL can be ingested into the existing RAG pipeline one item at a
time with metadata preserved.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


DEFAULT_GUIDE = Path("docs/COMFYUI_CU130_WORKFLOW_GUIDE.md")
DEFAULT_OUTPUT = Path("deployment/comfyui/commercial_ktv_workflow/cu130_workflow_rag_documents.jsonl")
DEFAULT_SUMMARY = Path("deployment/comfyui/commercial_ktv_workflow/cu130_workflow_rag_summary.md")
DEFAULT_WORKFLOW_ROOT = Path("E:/ComfyUI_cu130/ComfyUI/user/default/workflows")
COLLECTION_NAME = "comfyui_cu130_workflows"


@dataclass(frozen=True)
class WorkflowKnowledgeDocument:
    source_id: str
    source_name: str
    source_type: str
    collection_name: str
    text: str
    metadata: dict[str, object]


def _stable_id(value: str) -> str:
    digest = hashlib.sha1(value.encode("utf-8")).hexdigest()[:12]
    return f"comfyui_workflow_{digest}"


def _strip_backticks(value: str) -> str:
    value = value.strip()
    if value.startswith("`") and value.endswith("`"):
        return value[1:-1].strip()
    return value


def _split_table_row(line: str) -> list[str]:
    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    return cells


def _is_workflow_row(line: str) -> bool:
    return line.startswith("| `") and ".json`" in line


def _normalize_category(heading: str) -> tuple[str, str]:
    raw = heading.strip().lstrip("#").strip()
    match = re.match(r"(?P<number>\d+)\.\s*(?P<name>.+)", raw)
    if not match:
        return raw, raw
    return match.group("number"), match.group("name").strip()


def _infer_capabilities(name: str, description: str, value: str) -> list[str]:
    haystack = f"{name} {description} {value}".lower()
    rules: list[tuple[str, Iterable[str]]] = [
        ("video_analysis", ["截取视频", "分镜", "音频分离", "asr", "字幕", "image2prompt", "qwenvl"]),
        ("asr", ["asr", "语音转文字", "字幕", "whisper"]),
        ("tts", ["tts", "语音生成", "音色", "克隆", "旁白", "配音"]),
        ("music_generation", ["音乐", "bgm", "ace-step", "heartmula", "歌词"]),
        ("digital_human_lip_sync", ["infinitetalk", "s2v", "口型", "对口型", "音频驱动"]),
        ("image_to_video", ["图生视频", "i2v", "image to video", "hunyuan"]),
        ("motion_transfer", ["动作迁移", "人物迁移", "animate", "stead", "scail", "姿势控制"]),
        ("subject_segmentation", ["遮罩", "sam", "分割", "抠图", "移除背景", "birefnet"]),
        ("depth_control", ["depth", "深度"]),
        ("post_processing", ["合并", "分屏", "倒放", "gif", "mp3", "放大", "补帧", "转"]),
    ]
    capabilities = [capability for capability, keywords in rules if any(keyword in haystack for keyword in keywords)]
    return capabilities or ["general_comfyui_workflow"]


def _infer_project_types(capabilities: list[str], value: str) -> list[str]:
    project_types = {"general"}
    haystack = value.lower()
    if any(item in capabilities for item in ["digital_human_lip_sync", "motion_transfer", "image_to_video"]):
        project_types.update({"ktv", "local_life", "ecommerce", "brand"})
    if "music_generation" in capabilities or "ktv" in haystack or "商 k" in haystack:
        project_types.add("ktv")
    if "tts" in capabilities:
        project_types.update({"education", "local_life", "brand"})
    if "video_analysis" in capabilities:
        project_types.update({"all_video_projects", "ktv", "local_life", "ecommerce", "brand"})
    return sorted(project_types)


def _infer_content_modes(capabilities: list[str]) -> list[str]:
    mapping = {
        "video_analysis": "video_analysis",
        "asr": "audio_to_text",
        "tts": "voice_generation",
        "music_generation": "music_generation",
        "digital_human_lip_sync": "digital_human_video",
        "image_to_video": "image_to_video",
        "motion_transfer": "motion_transfer_video",
        "subject_segmentation": "material_preprocess",
        "depth_control": "control_map_generation",
        "post_processing": "post_processing",
    }
    return sorted({mapping[item] for item in capabilities if item in mapping}) or ["workflow_utility"]


def _find_workflow_path(workflow_root: Path, workflow_name: str) -> str | None:
    if not workflow_root.exists():
        return None
    candidates = list(workflow_root.rglob(workflow_name))
    if not candidates:
        return None
    return str(candidates[0])


def parse_guide(guide_path: Path, workflow_root: Path) -> list[WorkflowKnowledgeDocument]:
    lines = guide_path.read_text(encoding="utf-8").splitlines()
    current_category_number = ""
    current_category_name = ""
    documents: list[WorkflowKnowledgeDocument] = []

    for line in lines:
        if line.startswith("## "):
            current_category_number, current_category_name = _normalize_category(line)
            continue
        if not _is_workflow_row(line):
            continue
        cells = _split_table_row(line)
        if len(cells) < 5:
            continue
        workflow_name = _strip_backticks(cells[0])
        description, input_contract, output_contract, project_value = cells[1:5]
        workflow_path = _find_workflow_path(workflow_root, workflow_name)
        source_id = _stable_id(workflow_name)
        capability_text = " ".join([workflow_name, description, input_contract, output_contract, project_value])
        capabilities = _infer_capabilities(workflow_name, description, capability_text)
        project_types = _infer_project_types(capabilities, capability_text)
        content_modes = _infer_content_modes(capabilities)
        text = "\n".join(
            [
                f"工作流：{workflow_name}",
                f"分类：{current_category_name}",
                f"作用：{description}",
                f"输入：{input_contract}",
                f"输出：{output_contract}",
                f"项目价值：{project_value}",
                f"能力标签：{', '.join(capabilities)}",
                f"适合项目：{', '.join(project_types)}",
                f"适合内容模式：{', '.join(content_modes)}",
            ]
        )
        metadata: dict[str, object] = {
            "knowledge_type": "comfyui_workflow",
            "workflow_id": source_id,
            "workflow_name": workflow_name,
            "workflow_path": workflow_path,
            "category_number": current_category_number,
            "category": current_category_name,
            "capabilities": capabilities,
            "content_modes": content_modes,
            "project_types": project_types,
            "input_contract": input_contract,
            "output_contract": output_contract,
            "project_value": project_value,
            "source_guide": str(guide_path),
            "runtime_project": "comfyui_cu130",
            "requires_model_validation": True,
        }
        documents.append(
            WorkflowKnowledgeDocument(
                source_id=source_id,
                source_name=workflow_name,
                source_type="comfyui_workflow",
                collection_name=COLLECTION_NAME,
                text=text,
                metadata=metadata,
            )
        )
    return documents


def write_jsonl(documents: list[WorkflowKnowledgeDocument], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        for document in documents:
            handle.write(json.dumps(asdict(document), ensure_ascii=False, sort_keys=True))
            handle.write("\n")


def write_summary(documents: list[WorkflowKnowledgeDocument], summary_path: Path) -> None:
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    by_category: dict[str, int] = {}
    by_capability: dict[str, int] = {}
    for document in documents:
        category = str(document.metadata.get("category") or "未分类")
        by_category[category] = by_category.get(category, 0) + 1
        for capability in document.metadata.get("capabilities", []):
            key = str(capability)
            by_capability[key] = by_capability.get(key, 0) + 1

    lines = [
        "# ComfyUI_cu130 工作流 RAG 文档生成摘要",
        "",
        f"Collection: `{COLLECTION_NAME}`",
        f"Document count: `{len(documents)}`",
        "",
        "## 按分类统计",
        "",
    ]
    for category, count in sorted(by_category.items()):
        lines.append(f"- {category}: {count}")
    lines.extend(["", "## 按能力统计", ""])
    for capability, count in sorted(by_capability.items()):
        lines.append(f"- {capability}: {count}")
    lines.extend(
        [
            "",
            "## 入库建议",
            "",
            "逐行读取 `cu130_workflow_rag_documents.jsonl`，对每行调用现有 RAG ingest：",
            "",
            "```json",
            '{"text": "...", "metadata": {...}, "source_id": "...", "source_name": "...", "source_type": "comfyui_workflow", "collection_name": "comfyui_cu130_workflows"}',
            "```",
            "",
            "这些条目只负责工作流选型知识，不代表模型已经下载完成或工作流已经通过运行验证。",
        ]
    )
    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--guide", type=Path, default=DEFAULT_GUIDE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--workflow-root", type=Path, default=DEFAULT_WORKFLOW_ROOT)
    args = parser.parse_args()

    documents = parse_guide(args.guide, args.workflow_root)
    write_jsonl(documents, args.output)
    write_summary(documents, args.summary)
    print(f"wrote {len(documents)} workflow RAG documents to {args.output}")
    print(f"wrote summary to {args.summary}")


if __name__ == "__main__":
    main()
