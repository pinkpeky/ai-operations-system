"""Video-specialist Agent for commercial operation workflow selection.

This module turns a video production brief into a reviewable ComfyUI execution
package. It does not submit prompts to ComfyUI; queue submission stays behind
the runtime gate and operator approval.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_WORKFLOW_KNOWLEDGE = (
    PROJECT_ROOT / "deployment" / "comfyui" / "commercial_ktv_workflow" / "cu130_runtime_workflow_rag_documents.jsonl"
)
DEFAULT_MODEL_AUDIT = (
    PROJECT_ROOT / "deployment" / "comfyui" / "commercial_ktv_workflow" / "cu130_runtime_model_audit.json"
)


@dataclass(frozen=True)
class WorkflowStageProfile:
    """A workflow selection slice for one video-production stage."""

    stage_key: str
    display_name: str
    purpose: str
    required_capabilities: tuple[str, ...]
    preferred_terms: tuple[str, ...]
    required_inputs: tuple[str, ...]
    expected_outputs: tuple[str, ...]
    optional: bool = False


class ComfyUIWorkflowKnowledge:
    """Load and rank CU130 workflow RAG documents."""

    def __init__(self, knowledge_path: Path = DEFAULT_WORKFLOW_KNOWLEDGE) -> None:
        self.knowledge_path = knowledge_path

    def load_documents(self) -> list[dict[str, Any]]:
        if not self.knowledge_path.exists():
            return []
        documents: list[dict[str, Any]] = []
        with self.knowledge_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                clean = line.strip()
                if clean:
                    documents.append(json.loads(clean))
        return documents

    def capability_counts(self, documents: list[dict[str, Any]]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for document in documents:
            metadata = self._metadata(document)
            for capability in metadata.get("capabilities", []) or []:
                key = str(capability)
                counts[key] = counts.get(key, 0) + 1
        return dict(sorted(counts.items()))

    def rank(
        self,
        *,
        documents: list[dict[str, Any]],
        query: str,
        required_capabilities: tuple[str, ...],
        preferred_terms: tuple[str, ...] = (),
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        ranked = self._rank(
            documents=documents,
            query=query,
            required_capabilities=required_capabilities,
            preferred_terms=preferred_terms,
            require_all_capabilities=True,
        )
        if not ranked:
            ranked = self._rank(
                documents=documents,
                query=query,
                required_capabilities=required_capabilities,
                preferred_terms=preferred_terms,
                require_all_capabilities=False,
            )
        ranked.sort(key=lambda item: item["score"], reverse=True)
        return [
            {
                **item,
                "rank": index,
            }
            for index, item in enumerate(ranked[:limit], start=1)
        ]

    def _rank(
        self,
        *,
        documents: list[dict[str, Any]],
        query: str,
        required_capabilities: tuple[str, ...],
        preferred_terms: tuple[str, ...],
        require_all_capabilities: bool,
    ) -> list[dict[str, Any]]:
        query_tokens = _tokens(query)
        preferred = [term.lower() for term in preferred_terms if term]
        required = set(required_capabilities)
        ranked: list[dict[str, Any]] = []

        for document in documents:
            metadata = self._metadata(document)
            capabilities = {str(item) for item in metadata.get("capabilities", []) or []}
            matched_capabilities = sorted(required & capabilities)
            if required:
                if require_all_capabilities and required - capabilities:
                    continue
                if not require_all_capabilities and not matched_capabilities:
                    continue

            workflow_name = str(metadata.get("workflow_name") or document.get("source_name") or "")
            category = str(metadata.get("category") or "")
            text = " ".join(
                [
                    workflow_name,
                    category,
                    str(document.get("text") or ""),
                    " ".join(str(item) for item in metadata.get("model_refs_found", []) or []),
                ]
            )
            text_lower = text.lower()
            text_tokens = _tokens(text)
            model_refs_missing = [str(item) for item in metadata.get("model_refs_missing", []) or []]
            missing_nodes = [str(item) for item in metadata.get("missing_executable_node_types", []) or []]

            score = 0.0
            reasons: list[str] = []
            if matched_capabilities:
                score += 100.0 if require_all_capabilities else 35.0
                score += 22.0 * len(matched_capabilities)
                reasons.append(f"capability_match={','.join(matched_capabilities)}")

            term_hits = sorted({term for term in preferred if term and term in text_lower})
            if term_hits:
                score += 9.0 * len(term_hits)
                reasons.append(f"preferred_terms={','.join(term_hits[:6])}")

            lexical_hits = sorted(query_tokens & text_tokens)
            if lexical_hits:
                score += min(len(lexical_hits), 12)
                reasons.append(f"query_overlap={','.join(lexical_hits[:8])}")

            found_count = len(metadata.get("model_refs_found", []) or [])
            score += min(found_count, 12) * 0.8
            if not model_refs_missing:
                score += 8.0
                reasons.append("model_refs_matched")
            else:
                score -= min(len(model_refs_missing), 8) * 5.0
                reasons.append(f"missing_model_refs={len(model_refs_missing)}")
            if missing_nodes:
                score -= 80.0
                reasons.append(f"missing_nodes={len(missing_nodes)}")
            if metadata.get("requires_prompt_validation"):
                reasons.append("requires_target_material_prompt_validation")

            workflow_path = str(metadata.get("workflow_path") or "")
            if workflow_path and Path(workflow_path).exists():
                score += 2.0
                reasons.append("workflow_path_exists")

            ranked.append(
                {
                    "score": round(score, 2),
                    "workflow_id": str(metadata.get("workflow_id") or document.get("source_id") or ""),
                    "workflow_name": workflow_name,
                    "category": category,
                    "capabilities": sorted(capabilities),
                    "workflow_path": workflow_path,
                    "workflow_path_exists": bool(workflow_path and Path(workflow_path).exists()),
                    "runtime_readiness": str(metadata.get("runtime_readiness") or "unknown"),
                    "requires_prompt_validation": bool(metadata.get("requires_prompt_validation")),
                    "model_refs_found_count": found_count,
                    "model_refs_missing": model_refs_missing,
                    "missing_executable_node_types": missing_nodes,
                    "reasons": reasons,
                }
            )
        return ranked

    @staticmethod
    def _metadata(document: dict[str, Any]) -> dict[str, Any]:
        metadata = document.get("metadata")
        return metadata if isinstance(metadata, dict) else {}


class CommercialVideoAgent:
    """Prepare video analysis, workflow selection, and execution package output."""

    stage_profiles = (
        WorkflowStageProfile(
            stage_key="reference_video_analysis",
            display_name="Reference video analysis",
            purpose="Extract frames, audio, speech, subtitles, and visual style from a reference video.",
            required_capabilities=("video_analysis",),
            preferred_terms=("截取视频", "视频-音频分离", "Qwen3-ASR", "图像嵌入文字描述", "ASR"),
            required_inputs=("source_video_or_reference_video",),
            expected_outputs=("frame_samples", "transcript", "shot_segments", "style_summary"),
            optional=True,
        ),
        WorkflowStageProfile(
            stage_key="ai_virtual_host_seed",
            display_name="AI virtual host seed",
            purpose="Create a fictional adult AI host identity and keyframe inside the target scene.",
            required_capabilities=("image_generation",),
            preferred_terms=("Qwen-Image-Edit", "Qwen", "SAM3", "人物", "姿势", "多视角"),
            required_inputs=("scene_image", "character_prompt"),
            expected_outputs=("ai_host_keyframe", "identity_prompt"),
        ),
        WorkflowStageProfile(
            stage_key="scene_i2v_motion",
            display_name="Scene image to video",
            purpose="Animate the approved scene-host keyframe while preserving the room and vertical framing.",
            required_capabilities=("image_to_video",),
            preferred_terms=("Wan2.2_I2V", "Wan2.1_I2V", "I2V", "图生视频", "GGUF"),
            required_inputs=("approved_keyframe", "motion_prompt"),
            expected_outputs=("short_video_clip",),
        ),
        WorkflowStageProfile(
            stage_key="digital_human_i2v",
            display_name="Digital human I2V and lip-sync",
            purpose="Drive mouth movement and modest host motion from audio/script while preserving the scene.",
            required_capabilities=("image_to_video", "digital_human"),
            preferred_terms=("InfiniteTalk", "I2V", "提示词调度", "KJ", "Wan2.1"),
            required_inputs=("approved_keyframe", "voice_audio_or_script", "motion_prompt"),
            expected_outputs=("talking_host_video_clip",),
        ),
        WorkflowStageProfile(
            stage_key="motion_transfer",
            display_name="Optional motion transfer",
            purpose="Use only when a reference action video is supplied and the target needs same-action body motion.",
            required_capabilities=("motion_transfer", "segmentation"),
            preferred_terms=("Wan2.2_Animate", "SAM3", "MatAnyone", "人物迁移", "长视频"),
            required_inputs=("ai_host_keyframe", "reference_motion_video"),
            expected_outputs=("motion_transferred_video_clip", "mask_preview"),
            optional=True,
        ),
        WorkflowStageProfile(
            stage_key="post_processing",
            display_name="Post processing",
            purpose="Assemble clips, audio, subtitles, and review previews into a delivery candidate.",
            required_capabilities=("post_processing",),
            preferred_terms=("合成", "字幕", "放大", "音频", "MP3"),
            required_inputs=("rendered_clips", "audio", "subtitles"),
            expected_outputs=("final_video_candidate", "contact_sheet", "quality_report"),
        ),
    )

    def __init__(
        self,
        *,
        workflow_knowledge: ComfyUIWorkflowKnowledge | None = None,
        model_audit_path: Path = DEFAULT_MODEL_AUDIT,
    ) -> None:
        self.workflow_knowledge = workflow_knowledge or ComfyUIWorkflowKnowledge()
        self.model_audit_path = model_audit_path

    def plan(
        self,
        *,
        operation: Any,
        request_context: dict[str, Any],
        rag_context: dict[str, Any],
        digital_human_job: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        documents = self.workflow_knowledge.load_documents()
        capability_counts = self.workflow_knowledge.capability_counts(documents)
        source_understanding = self._source_understanding(request_context)
        operation_goal = self._operation_goal(operation=operation, request_context=request_context)
        query = self._selection_query(
            operation=operation,
            request_context=request_context,
            rag_context=rag_context,
            source_understanding=source_understanding,
        )
        selected_by_stage = self._select_by_stage(
            documents=documents,
            query=query,
            source_understanding=source_understanding,
        )
        workflow_selection = {
            "selection_mode": "deterministic_cu130_runtime_rag",
            "knowledge_path": str(self.workflow_knowledge.knowledge_path),
            "collection_name": "comfyui_cu130_workflows",
            "candidate_count": len(documents),
            "capability_counts": capability_counts,
            "query": query,
            "selected_by_stage": selected_by_stage,
            "selected_workflows": self._flatten_selected(selected_by_stage),
            "rejected_workflows": self._rejected_workflows(source_understanding),
        }
        video_analysis_result = self._video_analysis_result(
            operation=operation,
            request_context=request_context,
            rag_context=rag_context,
            source_understanding=source_understanding,
            capability_counts=capability_counts,
        )
        runtime_evidence = self._runtime_evidence(
            documents=documents,
            capability_counts=capability_counts,
        )
        execution_package = self._execution_package(
            operation=operation,
            operation_goal=operation_goal,
            request_context=request_context,
            source_understanding=source_understanding,
            workflow_selection=workflow_selection,
            runtime_evidence=runtime_evidence,
            digital_human_job=digital_human_job,
        )
        return {
            "video_agent_plan": {
                "agent_name": "commercial_video_specialist_agent",
                "display_name": "Commercial Video Specialist Agent",
                "mode": "video_analysis_contract_plus_cu130_workflow_selection",
                "content_mode": "scene_to_ai_virtual_host_video",
                "operation_goal": operation_goal,
                "source_understanding": source_understanding,
                "recommended_pipeline": [
                    "reference_video_analysis_if_present",
                    "ai_virtual_host_seed_generation",
                    "scene_consistent_keyframe_review",
                    "image_to_video_or_infinitetalk_render",
                    "quality_review_and_post_processing",
                ],
                "readiness": execution_package["readiness"],
                "next_actions": self._next_actions(execution_package),
                "generated_at": datetime.now(UTC).isoformat(),
            },
            "video_analysis_result": video_analysis_result,
            "workflow_selection": workflow_selection,
            "execution_package": execution_package,
            "runtime_evidence": runtime_evidence,
        }

    def _select_by_stage(
        self,
        *,
        documents: list[dict[str, Any]],
        query: str,
        source_understanding: dict[str, Any],
    ) -> dict[str, Any]:
        selected: dict[str, Any] = {}
        for profile in self.stage_profiles:
            if profile.stage_key == "reference_video_analysis" and not source_understanding["has_reference_video"]:
                selected[profile.stage_key] = self._skipped_stage(profile, "no_reference_video_supplied")
                continue
            if profile.stage_key == "motion_transfer" and not source_understanding["needs_motion_transfer"]:
                selected[profile.stage_key] = self._skipped_stage(profile, "motion_transfer_not_required_for_scene_image_route")
                continue
            ranked = self.workflow_knowledge.rank(
                documents=documents,
                query=query,
                required_capabilities=profile.required_capabilities,
                preferred_terms=profile.preferred_terms,
                limit=5,
            )
            selected[profile.stage_key] = {
                "stage_key": profile.stage_key,
                "display_name": profile.display_name,
                "status": "candidate_selected" if ranked else "no_candidate_found",
                "purpose": profile.purpose,
                "required_capabilities": list(profile.required_capabilities),
                "required_inputs": list(profile.required_inputs),
                "expected_outputs": list(profile.expected_outputs),
                "selected": ranked,
            }
        return selected

    @staticmethod
    def _skipped_stage(profile: WorkflowStageProfile, reason: str) -> dict[str, Any]:
        return {
            "stage_key": profile.stage_key,
            "display_name": profile.display_name,
            "status": "skipped",
            "skip_reason": reason,
            "purpose": profile.purpose,
            "required_capabilities": list(profile.required_capabilities),
            "required_inputs": list(profile.required_inputs),
            "expected_outputs": list(profile.expected_outputs),
            "selected": [],
        }

    def _execution_package(
        self,
        *,
        operation: Any,
        operation_goal: str,
        request_context: dict[str, Any],
        source_understanding: dict[str, Any],
        workflow_selection: dict[str, Any],
        runtime_evidence: dict[str, Any],
        digital_human_job: dict[str, Any] | None,
    ) -> dict[str, Any]:
        hard_blocks: list[str] = []
        if workflow_selection["candidate_count"] <= 0:
            hard_blocks.append("workflow_knowledge_missing")
        if not runtime_evidence.get("runtime_audit_available"):
            hard_blocks.append("comfyui_cu130_runtime_audit_missing")
        if not source_understanding["has_scene_image"]:
            hard_blocks.append("scene_image_required_for_scene_to_ai_virtual_host_video")
        for stage_key in ("ai_virtual_host_seed", "scene_i2v_motion", "digital_human_i2v", "post_processing"):
            stage = workflow_selection["selected_by_stage"].get(stage_key, {})
            if not stage.get("selected"):
                hard_blocks.append(f"{stage_key}_workflow_candidate_missing")

        status = "blocked" if hard_blocks else "ready_for_review"
        width, height = _aspect_dimensions(str(request_context.get("aspect_ratio") or "9:16"))
        duration_seconds = float(request_context.get("duration_seconds") or 12.0)
        fps = 24
        frames = int(duration_seconds * fps)
        selected_primary = _first_selected(workflow_selection["selected_by_stage"], "digital_human_i2v")
        fallback_primary = _first_selected(workflow_selection["selected_by_stage"], "scene_i2v_motion")
        return {
            "contract_version": "1.0",
            "package_type": "video_execution_package",
            "content_mode": "scene_to_ai_virtual_host_video",
            "status": status,
            "runtime_provider": "comfyui_cu130",
            "operation_id": str(_get(operation, "id", "")),
            "workspace_id": str(_get(operation, "workspace_id", "")),
            "operation_goal": operation_goal,
            "digital_human_job_id": str(digital_human_job.get("id")) if digital_human_job else None,
            "selected_primary_workflow": selected_primary or fallback_primary,
            "workflow_stages": workflow_selection["selected_by_stage"],
            "input_assets": {
                "scene_image": source_understanding.get("scene_image_uri"),
                "source_video": source_understanding.get("source_video_uri"),
                "reference_motion_video": source_understanding.get("reference_video_uri"),
                "avatar_asset_id": source_understanding.get("avatar_asset_id"),
                "material_asset_ids": source_understanding.get("material_asset_ids"),
                "reference_asset_ids": source_understanding.get("reference_asset_ids"),
            },
            "parameter_plan": {
                "aspect_ratio": str(request_context.get("aspect_ratio") or "9:16"),
                "width": width,
                "height": height,
                "fps": fps,
                "frames": frames,
                "duration_seconds": duration_seconds,
                "character_prompt": (
                    "Fictional adult AI female commercial host, elegant KTV reception style, natural face, "
                    "normal body proportions, confident but not exaggerated, no real-person identity."
                ),
                "scene_prompt": (
                    "Preserve the supplied KTV/private-room scene image: room layout, sofa, table, screen, "
                    "neon lighting, camera perspective, and vertical short-video framing."
                ),
                "motion_prompt": (
                    "Modest commercial presenter motion: breathing, small head turn, light hand gesture, "
                    "stable full-body or half-body framing, no dance or large body movement unless reviewed."
                ),
                "negative_prompt": (
                    "distorted face, asymmetrical eyes, bad hands, extra fingers, extra limbs, broken body, "
                    "childlike appearance, real person cutout, watermark, unreadable text, changed room layout, "
                    "severe flicker, plastic skin"
                ),
            },
            "quality_gates": [
                "host_must_be_fictional_adult_ai_character",
                "no_real_person_cutout_as_default_route",
                "face_and_body_proportions_must_be_normal",
                "hands_must_be_reviewable_before_video_render",
                "scene_layout_must_remain_recognizable",
                "lip_sync_or_audio_timing_must_be_reviewed_when_voice_is_used",
                "operator_approval_required_before_queue_submit",
            ],
            "readiness": {
                "status": status,
                "blocking_conditions": list(dict.fromkeys(hard_blocks)),
                "approval_gates": ["operator_approval_required_before_comfyui_queue_submit"],
                "runtime_checks": [
                    "cu130_runtime_audit_loaded" if runtime_evidence.get("runtime_audit_available") else "runtime_audit_missing",
                    f"workflow_candidates={workflow_selection['candidate_count']}",
                    f"models={runtime_evidence.get('model_count', 0)}",
                    f"model_total_gb={runtime_evidence.get('model_total_gb', 0)}",
                ],
            },
            "fallback_plan": {
                "if_ai_host_seed_fails": "regenerate the AI virtual host keyframe with stricter face/body negative prompts",
                "if_full_body_motion_fails": "switch to half-body digital-human I2V or close-up lip-sync shot",
                "if_scene_drifts": "reduce motion strength and rerun from approved keyframe",
                "if_lip_sync_fails": "use a non-speaking presenter shot plus subtitles and voiceover in post",
            },
            "workflow_materialization_policy": {
                "source_workflow_is_read_only": True,
                "never_overwrite_source_workflow": True,
                "materialize_per_run_copy_before_prompt_submission": True,
                "default_output_root": "storage/comfyui_materialized_workflows",
                "injectable_fields": [
                    "positive_prompt",
                    "negative_prompt",
                    "prompt",
                    "text",
                    "image",
                    "video",
                    "audio",
                    "width",
                    "height",
                    "frames",
                    "fps",
                    "filename_prefix",
                ],
            },
            "forbidden_actions": [
                "no_comfyui_queue_submit_without_runtime_gate",
                "no_source_workflow_overwrite",
                "no_real_person_portrait_cutout_unless_operator_overrides",
                "no_platform_publish_from_server",
                "no_secret_exposure",
            ],
        }

    def _runtime_evidence(self, *, documents: list[dict[str, Any]], capability_counts: dict[str, int]) -> dict[str, Any]:
        evidence: dict[str, Any] = {
            "runtime_project": "comfyui_cu130",
            "runtime_audit_path": str(self.model_audit_path),
            "runtime_audit_available": self.model_audit_path.exists(),
            "workflow_knowledge_path": str(self.workflow_knowledge.knowledge_path),
            "workflow_candidate_count": len(documents),
            "workflow_capability_counts": capability_counts,
        }
        if not self.model_audit_path.exists():
            return evidence
        audit = json.loads(self.model_audit_path.read_text(encoding="utf-8"))
        runtime = audit.get("runtime", {}) if isinstance(audit.get("runtime"), dict) else {}
        system_stats = runtime.get("system_stats", {}) if isinstance(runtime.get("system_stats"), dict) else {}
        system = system_stats.get("system", {}) if isinstance(system_stats.get("system"), dict) else {}
        devices = system_stats.get("devices", []) if isinstance(system_stats.get("devices"), list) else []
        models = audit.get("models", {}) if isinstance(audit.get("models"), dict) else {}
        workflows = audit.get("workflows", {}) if isinstance(audit.get("workflows"), dict) else {}
        evidence.update(
            {
                "audit_generated_at": audit.get("generated_at"),
                "comfy_root": audit.get("comfy_root"),
                "base_url": audit.get("base_url"),
                "comfyui_version": system.get("comfyui_version"),
                "pytorch_version": system.get("pytorch_version"),
                "device_names": [str(device.get("name")) for device in devices if isinstance(device, dict)],
                "model_count": models.get("count", 0),
                "model_total_gb": models.get("total_gb", 0),
                "workflow_count": workflows.get("count", len(documents)),
                "runtime_queue": runtime.get("queue", {}),
                "video_minimum_capabilities_present": {
                    "video_analysis": capability_counts.get("video_analysis", 0) > 0,
                    "asr": capability_counts.get("asr", 0) > 0,
                    "vlm_prompting": capability_counts.get("vlm_prompting", 0) > 0,
                    "image_generation": capability_counts.get("image_generation", 0) > 0,
                    "image_to_video": capability_counts.get("image_to_video", 0) > 0,
                    "digital_human": capability_counts.get("digital_human", 0) > 0,
                    "motion_transfer": capability_counts.get("motion_transfer", 0) > 0,
                },
            }
        )
        return evidence

    def _video_analysis_result(
        self,
        *,
        operation: Any,
        request_context: dict[str, Any],
        rag_context: dict[str, Any],
        source_understanding: dict[str, Any],
        capability_counts: dict[str, int],
    ) -> dict[str, Any]:
        metadata = _metadata(request_context)
        supplied = metadata.get("video_analysis_result")
        if isinstance(supplied, dict):
            return {
                **supplied,
                "status": supplied.get("status") or "supplied",
                "source": "request_metadata",
            }
        if source_understanding["has_reference_video"]:
            status = "analysis_contract_ready"
            next_action = "Run the video analysis service: extract frames/audio, ASR, VLM captions, shot segments, and operating formula."
        elif source_understanding["has_scene_image"]:
            status = "scene_image_source_ready"
            next_action = "Use the scene image as the visual anchor; no source-video analysis is required for this scene-only route."
        else:
            status = "blocked_missing_scene_or_reference_video"
            next_action = "Attach a scene image or reference video before workflow execution planning can be finalized."
        return {
            "analysis_id": None,
            "status": status,
            "source": "commercial_video_specialist_agent",
            "operation_id": str(_get(operation, "id", "")),
            "source_asset": {
                "source_video_uri": source_understanding.get("source_video_uri"),
                "scene_image_uri": source_understanding.get("scene_image_uri"),
                "reference_video_uri": source_understanding.get("reference_video_uri"),
                "target_platforms": source_understanding.get("target_channels"),
            },
            "scene_summary": (
                "The production route uses a supplied KTV/private-room scene image as the background anchor and "
                "generates a fictional AI female host for short-video presentation."
            ),
            "available_analysis_capabilities": {
                "frame_extraction": capability_counts.get("video_analysis", 0) > 0,
                "asr": capability_counts.get("asr", 0) > 0,
                "vlm_prompting": capability_counts.get("vlm_prompting", 0) > 0,
                "segmentation": capability_counts.get("segmentation", 0) > 0,
            },
            "workflow_hints": [
                "scene_consistent_i2v",
                "ai_generated_virtual_host",
                "digital_human_lip_sync_if_audio_exists",
                "motion_transfer_only_if_reference_action_video_exists",
            ],
            "rag_payload": {
                "used_retrieval": bool(rag_context.get("used_retrieval")),
                "rag_result_count": rag_context.get("rag_result_count", 0),
                "collection_name": rag_context.get("collection_name"),
            },
            "next_action": next_action,
        }

    def _source_understanding(self, request_context: dict[str, Any]) -> dict[str, Any]:
        metadata = _metadata(request_context)
        scene_image_uri = _first_text(
            request_context.get("scene_image_uri"),
            metadata.get("scene_image_uri"),
            metadata.get("scene_image"),
        )
        source_video_uri = _first_text(request_context.get("source_video_uri"), metadata.get("source_video_uri"))
        reference_video_uri = _first_text(request_context.get("reference_video_uri"), metadata.get("reference_video_uri"))
        material_asset_ids = [str(item) for item in request_context.get("material_asset_ids", []) or []]
        reference_asset_ids = [str(item) for item in request_context.get("reference_asset_ids", []) or []]
        avatar_asset_id = _first_text(request_context.get("avatar_asset_id"), metadata.get("avatar_asset_id"))
        needs_ai_virtual_person = bool(request_context.get("needs_ai_virtual_person", True))
        allow_real_person_cutout = bool(request_context.get("allow_real_person_cutout", False))
        has_scene_image = bool(scene_image_uri or material_asset_ids)
        has_reference_video = bool(source_video_uri or reference_video_uri)
        needs_motion_transfer = bool(
            metadata.get("needs_motion_transfer")
            or (has_reference_video and str(metadata.get("reference_video_intent") or "").lower() == "motion_transfer")
        )
        return {
            "has_scene_image": has_scene_image,
            "scene_image_uri": scene_image_uri,
            "has_reference_video": has_reference_video,
            "source_video_uri": source_video_uri,
            "reference_video_uri": reference_video_uri,
            "has_person_reference": bool(avatar_asset_id),
            "avatar_asset_id": avatar_asset_id,
            "material_asset_ids": material_asset_ids,
            "reference_asset_ids": reference_asset_ids,
            "needs_ai_virtual_person": needs_ai_virtual_person,
            "allow_real_person_cutout": allow_real_person_cutout,
            "primary_character_source": (
                "ai_generated_fictional_host"
                if needs_ai_virtual_person and not allow_real_person_cutout
                else "operator_supplied_authorized_character_reference"
            ),
            "needs_lip_sync": bool(
                request_context.get("script")
                or request_context.get("voice_profile")
                or metadata.get("needs_lip_sync", True)
            ),
            "needs_motion_transfer": needs_motion_transfer,
            "target_channels": list(request_context.get("target_channels") or [request_context.get("channel") or "short_video"]),
            "original_requirement_alignment": [
                "single_scene_image_can_anchor_same_scene_video",
                "host_identity_should_be_generated_by_ai",
                "real_person_cutout_is_not_the_default_route",
                "reference_video_is_for_structure_and_motion_learning_only",
            ],
        }

    def _selection_query(
        self,
        *,
        operation: Any,
        request_context: dict[str, Any],
        rag_context: dict[str, Any],
        source_understanding: dict[str, Any],
    ) -> str:
        parts = [
            self._operation_goal(operation=operation, request_context=request_context),
            str(request_context.get("script") or ""),
            str(request_context.get("style") or ""),
            " ".join(source_understanding.get("target_channels") or []),
            " ".join(source_understanding.get("original_requirement_alignment") or []),
            str(rag_context.get("query") or ""),
            "KTV Douyin short video scene image AI virtual female host digital human i2v InfiniteTalk Qwen Image Edit",
        ]
        return " ".join(part.strip() for part in parts if part and str(part).strip())[:4000]

    @staticmethod
    def _operation_goal(*, operation: Any, request_context: dict[str, Any]) -> str:
        return _first_text(
            request_context.get("objective"),
            _get(operation, "objective", None),
            _get(operation, "title", None),
            "Generate a reviewable commercial short video with a fictional AI virtual host.",
        ) or "Generate a reviewable commercial short video with a fictional AI virtual host."

    @staticmethod
    def _flatten_selected(selected_by_stage: dict[str, Any]) -> list[dict[str, Any]]:
        flattened: list[dict[str, Any]] = []
        seen: set[str] = set()
        for stage_key, stage in selected_by_stage.items():
            for item in stage.get("selected", []) or []:
                workflow_id = str(item.get("workflow_id") or item.get("workflow_name") or "")
                if workflow_id and workflow_id not in seen:
                    seen.add(workflow_id)
                    flattened.append({**item, "stage_key": stage_key})
        return flattened

    @staticmethod
    def _rejected_workflows(source_understanding: dict[str, Any]) -> list[dict[str, Any]]:
        rejected = [
            {
                "workflow_id": "real_person_cutout_composite_route",
                "reason": "The requested default route is AI-generated fictional host, not finding a portrait and compositing it into the scene.",
            }
        ]
        if not source_understanding["needs_motion_transfer"]:
            rejected.append(
                {
                    "workflow_id": "motion_transfer_without_reference_action_video",
                    "reason": "Motion-transfer workflows are not primary when the input is only a scene image.",
                }
            )
        return rejected

    @staticmethod
    def _next_actions(execution_package: dict[str, Any]) -> list[str]:
        readiness = execution_package.get("readiness", {})
        blocking = readiness.get("blocking_conditions") or []
        if blocking:
            return [
                f"Resolve blocking condition: {item}"
                for item in blocking
            ]
        return [
            "Review the selected CU130 workflows and execution package.",
            "Generate or approve the fictional AI virtual-host seed image from the scene image.",
            "Run a guarded ComfyUI preflight with target material before queue submission.",
            "Submit rendering only after operator approval and runtime gate activation.",
        ]


def _tokens(text: str) -> set[str]:
    normalized = re.sub(r"[\s,.;:|/\\()[\]{}<>\"'，。；：、]+", " ", text.lower())
    return {part for part in normalized.split(" ") if part}


def _get(obj: Any, key: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _metadata(request_context: dict[str, Any]) -> dict[str, Any]:
    metadata = request_context.get("metadata")
    return metadata if isinstance(metadata, dict) else {}


def _first_text(*values: Any) -> str | None:
    for value in values:
        if value is None:
            continue
        clean = str(value).strip()
        if clean:
            return clean
    return None


def _aspect_dimensions(aspect_ratio: str) -> tuple[int, int]:
    clean = aspect_ratio.strip()
    if clean == "16:9":
        return 1920, 1080
    if clean == "1:1":
        return 1024, 1024
    return 1080, 1920


def _first_selected(selected_by_stage: dict[str, Any], stage_key: str) -> dict[str, Any] | None:
    stage = selected_by_stage.get(stage_key) or {}
    selected = stage.get("selected") or []
    if not selected:
        return None
    first = dict(selected[0])
    first["stage_key"] = stage_key
    return first
