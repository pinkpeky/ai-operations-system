"""Commercial video main-agent orchestration contracts."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


class CommercialVideoMainAgent:
    """Plan how a commercial operation should hand off into video sub-agents."""

    video_keywords = {
        "video",
        "short_video",
        "reel",
        "tiktok",
        "douyin",
        "digital human",
        "avatar",
        "spokesperson",
        "livestream",
        "ktv",
        "宣传",
        "短视频",
        "视频",
        "数字人",
        "口播",
    }

    def plan(
        self,
        *,
        operation: Any,
        request_context: dict[str, Any],
        rag_context: dict[str, Any],
        digital_human_job: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        objective = self._objective(operation=operation, request_context=request_context)
        target_channels = self._target_channels(operation=operation, request_context=request_context)
        route = self._route(objective=objective, target_channels=target_channels, request_context=request_context)
        digital_human_request = self._digital_human_request(
            operation=operation,
            objective=objective,
            target_channels=target_channels,
            request_context=request_context,
            rag_context=rag_context,
            route=route,
        )
        sub_agents = self._sub_agents(
            route=route,
            rag_context=rag_context,
            request_context=request_context,
            digital_human_job=digital_human_job,
        )
        return {
            "operation_id": str(getattr(operation, "id", "")),
            "workspace_id": str(getattr(operation, "workspace_id", "")),
            "controller_agent": {
                "agent_name": "commercial_video_main_agent",
                "display_name": "Commercial Video Main Agent",
                "mode": "deterministic_route_with_rag_grounding",
                "uses_existing_agents": [
                    "rag_agent",
                    "creative_director_agent",
                    "digital_human_video_agent",
                    "shot_execution_agent",
                    "voice_normalization_agent",
                    "comfyui_render_agent",
                    "quality_review_agent",
                ],
                "capabilities": [
                    "commercial_goal_routing",
                    "rag_context_grounding",
                    "digital_human_job_handoff",
                    "shot_level_render_contracts",
                    "human_review_boundary",
                ],
            },
            "route_decision": {
                "route": route,
                "confidence": 0.92 if route == "digital_human_video" else 0.62,
                "rationale": self._route_rationale(route=route, rag_context=rag_context),
                "objective": objective,
                "target_channels": target_channels,
            },
            "rag_context": rag_context,
            "sub_agents": sub_agents,
            "digital_human_request": digital_human_request,
            "digital_human_job": digital_human_job,
            "next_actions": self._next_actions(
                route=route,
                request_context=request_context,
                digital_human_job=digital_human_job,
            ),
            "boundaries": [
                "The main agent routes and prepares handoffs; it does not publish, control accounts, or bypass review.",
                "RAG evidence is grounding context and must remain reviewable before claims are used in final output.",
                "Digital-human and ComfyUI steps stay behind explicit operator approval and runtime readiness gates.",
                "The default identity route is a fictional AI virtual host; real portrait cutouts require explicit operator override.",
            ],
            "generated_at": datetime.now(UTC),
        }

    def _digital_human_request(
        self,
        *,
        operation: Any,
        objective: str,
        target_channels: list[str],
        request_context: dict[str, Any],
        rag_context: dict[str, Any],
        route: str,
    ) -> dict[str, Any]:
        script = str(request_context.get("script") or "").strip()
        if not script:
            script = self._fallback_script(operation=operation, objective=objective, rag_context=rag_context)
        voice_profile = dict(request_context.get("voice_profile") or {})
        voice_profile.setdefault("style", request_context.get("style") or "realistic commercial operator vlog")
        voice_profile.setdefault(
            "normalization_target",
            "natural human operator speech; avoid generic ad-read cadence and robotic pacing",
        )
        planning_context = {
            "source": "commercial_video_main_agent",
            "commercial_operation": {
                "operation_id": str(getattr(operation, "id", "")),
                "title": str(getattr(operation, "title", "")),
                "objective": str(getattr(operation, "objective", "")),
                "target_audience": getattr(operation, "target_audience", None),
                "channels": list(getattr(operation, "channels", []) or []),
                "success_metrics": list(getattr(operation, "success_metrics", []) or []),
            },
            "route_decision": {
                "route": route,
                "requires_digital_human": route == "digital_human_video",
                "requires_generated_scene_continuity": True,
                "needs_ai_virtual_person": bool(request_context.get("needs_ai_virtual_person", True)),
                "allow_real_person_cutout": bool(request_context.get("allow_real_person_cutout", False)),
                "primary_character_source": (
                    "ai_generated_fictional_host"
                    if request_context.get("needs_ai_virtual_person", True)
                    and not request_context.get("allow_real_person_cutout", False)
                    else "operator_supplied_authorized_reference"
                ),
                "requires_rag_grounding": bool(rag_context.get("used_retrieval")),
                "prefer_fast_seed_planning": True,
            },
            "rag_context": rag_context,
            "operator_style": request_context.get("style"),
        }
        return {
            "objective": objective,
            "script": script,
            "provider": request_context.get("provider"),
            "avatar_asset_id": self._string_or_none(request_context.get("avatar_asset_id")),
            "material_asset_ids": [str(item) for item in request_context.get("material_asset_ids", [])],
            "reference_asset_ids": [str(item) for item in request_context.get("reference_asset_ids", [])],
            "target_channels": target_channels,
            "voice_profile": voice_profile,
            "aspect_ratio": request_context.get("aspect_ratio") or "9:16",
            "duration_seconds": request_context.get("duration_seconds"),
            "llm_planning_enabled": bool(request_context.get("llm_planning_enabled", True)),
            "planning_context": planning_context,
            "handoff_reason": "Video route selected by commercial main agent.",
        }

    def _sub_agents(
        self,
        *,
        route: str,
        rag_context: dict[str, Any],
        request_context: dict[str, Any],
        digital_human_job: dict[str, Any] | None,
    ) -> list[dict[str, Any]]:
        rag_status = str(rag_context.get("status") or "not_requested")
        job_status = str(digital_human_job.get("job_status")) if digital_human_job else None
        shot_count = int(digital_human_job.get("shot_execution_plan_count") or 0) if digital_human_job else 0
        return [
            {
                "agent_name": "commercial_video_main_agent",
                "role": "route_controller",
                "status": "complete",
                "input": ["operation_objective", "channels", "operator_video_request"],
                "output": ["route_decision", "sub_agent_handoff_plan"],
            },
            {
                "agent_name": "rag_agent",
                "role": "business_context_grounding",
                "status": "complete" if rag_context.get("used_retrieval") else rag_status,
                "input": ["knowledge_collection", "operation_query"],
                "output": ["retrieved_evidence", "source_materials", "claim_boundaries"],
            },
            {
                "agent_name": "creative_director_agent",
                "role": "story_script_shot_design",
                "status": "complete" if digital_human_job and request_context.get("llm_planning_enabled", True) else "ready",
                "input": ["objective", "rag_context", "avatar_and_material_references"],
                "output": ["character_bible", "voiceover", "story_beats", "shot_plan"],
            },
            {
                "agent_name": "digital_human_video_agent",
                "role": "digital_human_job_owner",
                "status": job_status or ("ready_to_create_job" if route == "digital_human_video" else "not_selected"),
                "input": ["ai_virtual_identity_or_avatar_asset", "voice_profile", "creative_plan"],
                "output": ["digital_human_video_job", "provider_request"],
            },
            {
                "agent_name": "shot_execution_agent",
                "role": "per_shot_render_contracts",
                "status": "complete" if shot_count else ("waiting_for_digital_human_job" if not digital_human_job else "ready_for_operator_review"),
                "input": ["llm_creative_plan", "workflow_template", "material_references"],
                "output": ["shot_execution_plan", "prompt_contract", "workflow_contract"],
            },
            {
                "agent_name": "voice_normalization_agent",
                "role": "human_voice_direction",
                "status": "planned",
                "input": ["voiceover_script", "voice_profile"],
                "output": ["tts_direction", "anti_ai_voice_checks"],
            },
            {
                "agent_name": "comfyui_render_agent",
                "role": "guarded_render_handoff",
                "status": "blocked_until_operator_runtime_gate",
                "input": ["shot_execution_plan", "workflow_readiness", "gpu_queue_gate"],
                "output": ["queued_comfyui_video_job", "render_outputs"],
            },
            {
                "agent_name": "quality_review_agent",
                "role": "final_video_acceptance",
                "status": "waiting",
                "input": ["rendered_video", "story_brief", "identity_rules"],
                "output": ["acceptance_report", "revision_decision"],
            },
        ]

    def _fallback_script(self, *, operation: Any, objective: str, rag_context: dict[str, Any]) -> str:
        evidence_items = rag_context.get("evidence_items") if isinstance(rag_context.get("evidence_items"), list) else []
        proof = ""
        if evidence_items:
            first = evidence_items[0] if isinstance(evidence_items[0], dict) else {}
            proof = str(first.get("text_excerpt") or "").strip()[:180]
        title = str(getattr(operation, "title", "") or "Commercial video")
        audience = str(getattr(operation, "target_audience", "") or "target customers")
        return "\n".join(
            [
                f"Opening: I am taking you inside {title}, where the goal is {objective}.",
                f"Story: For {audience}, show the real environment, service flow, and operator standard through coherent scenes.",
                f"Proof: {proof or 'Use the retrieved business evidence and uploaded materials as the factual anchor.'}",
                "Close: Invite the viewer to book, visit, or contact the operator for the next step.",
            ]
        )

    def _next_actions(
        self,
        *,
        route: str,
        request_context: dict[str, Any],
        digital_human_job: dict[str, Any] | None,
    ) -> list[str]:
        actions = []
        if route != "digital_human_video":
            return ["Review route decision and continue with content or asset brief generation."]
        if request_context.get("needs_ai_virtual_person", True) and not request_context.get("allow_real_person_cutout", False):
            actions.append("Generate and review one fictional AI virtual-host identity; do not use a real portrait cutout as the default route.")
        elif not request_context.get("avatar_asset_id"):
            actions.append("Upload or select one authorized portrait asset for digital-human identity continuity.")
        has_scene_reference = bool(
            request_context.get("scene_image_uri")
            or request_context.get("source_video_uri")
            or request_context.get("reference_video_uri")
        )
        if (
            not request_context.get("material_asset_ids")
            and not request_context.get("reference_asset_ids")
            and not has_scene_reference
        ):
            actions.append("Attach venue, product, and style reference materials so generated scenes can restore the business environment.")
        if digital_human_job is None:
            actions.append("Create the digital-human video job with LLM planning enabled.")
        else:
            actions.append("Prepare the shot execution plan, bind the ComfyUI workflow, and record runtime readiness evidence.")
        actions.append("Review RAG evidence, creative plan, voice direction, and shot plan before guarded rendering.")
        return actions

    def _route(self, *, objective: str, target_channels: list[str], request_context: dict[str, Any]) -> str:
        route_hint = str(request_context.get("route_hint") or "auto").strip().lower()
        if route_hint and route_hint != "auto":
            return route_hint
        haystack = " ".join(
            [
                objective,
                str(request_context.get("channel") or ""),
                str(request_context.get("style") or ""),
                " ".join(target_channels),
            ]
        ).lower()
        if any(keyword.lower() in haystack for keyword in self.video_keywords):
            return "digital_human_video"
        return "commercial_content"

    def _route_rationale(self, *, route: str, rag_context: dict[str, Any]) -> str:
        if route == "digital_human_video":
            if rag_context.get("used_retrieval"):
                return "The request asks for a commercial video and has retrieved business context for grounded story and scene planning."
            return "The request asks for a commercial video; RAG context is unavailable or empty, so the video plan must be reviewed carefully."
        return "The request does not clearly require digital-human video generation."

    def _objective(self, *, operation: Any, request_context: dict[str, Any]) -> str:
        value = str(request_context.get("objective") or "").strip()
        return value or str(getattr(operation, "objective", "") or "").strip()

    def _target_channels(self, *, operation: Any, request_context: dict[str, Any]) -> list[str]:
        channels: list[str] = []
        for item in [*(getattr(operation, "channels", []) or []), *(request_context.get("target_channels") or [])]:
            clean = str(item).strip()
            if clean and clean not in channels:
                channels.append(clean)
        channel = str(request_context.get("channel") or "").strip()
        if channel and channel not in channels:
            channels.append(channel)
        return channels or ["short_video"]

    @staticmethod
    def _string_or_none(value: Any) -> str | None:
        text = str(value).strip() if value is not None else ""
        return text or None
