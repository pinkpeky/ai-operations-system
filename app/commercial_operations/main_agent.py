"""Global commercial-operation main Agent routing.

Domain services gather operation state. This module owns the deterministic
operation-level routing decision and returns a reviewable execution contract.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TrackDefinition:
    """Static specialist-track definition used by the main Agent."""

    track_key: str
    display_name: str
    owner_agent: str
    stage_keys: tuple[str, ...]
    required_inputs: tuple[str, ...]
    expected_outputs: tuple[str, ...]
    boundary: str
    execution_boundary: str
    available_actions: tuple[str, ...]
    quality_gates: tuple[str, ...]
    next_action: str


class CommercialOperationMainAgent:
    """Route one commercial operation loop to the next specialist track."""

    agent_name = "commercial_operation_agent"
    workflow_collection = "comfyui_cu130_workflows"

    video_keywords = (
        "video",
        "short video",
        "reel",
        "tiktok",
        "douyin",
        "数字人",
        "短视频",
        "视频",
        "口播",
        "直播",
        "ktv",
        "商k",
        "抖音",
    )
    visual_keywords = (
        "image",
        "poster",
        "cover",
        "banner",
        "visual",
        "图文",
        "图片",
        "海报",
        "封面",
        "素材",
        "小红书",
    )
    text_keywords = (
        "copy",
        "email",
        "post",
        "script",
        "comment",
        "message",
        "文案",
        "私信",
        "评论",
        "话术",
        "脚本",
    )
    workflow_keywords = (
        "comfyui",
        "workflow",
        "工作流",
        "生成",
        "数字人",
        "视频",
        "图片",
        "音频",
    )
    publish_keywords = (
        "publish",
        "post",
        "openclaw",
        "playwright",
        "发布",
        "投放",
        "账号",
    )
    analytics_keywords = (
        "metric",
        "analytics",
        "result",
        "optimization",
        "数据",
        "复盘",
        "转化",
        "评论",
        "优化",
    )

    track_definitions = (
        TrackDefinition(
            track_key="operation_strategy",
            display_name="Operation strategy",
            owner_agent="operation_strategy_agent",
            stage_keys=("operation_topic", "task_planning"),
            required_inputs=("objective", "target_audience", "channels", "constraints", "success_metrics"),
            expected_outputs=("positioning", "audience", "channel_strategy", "success_metrics"),
            boundary="Strategy only; it does not create publishable assets or execute external actions.",
            execution_boundary="metadata_only_review_required",
            available_actions=("clarify_objective", "regenerate_plan_outline", "set_success_metrics"),
            quality_gates=("objective_is_specific", "audience_is_named", "success_metrics_are_reviewable"),
            next_action="Clarify objective, audience, channels, constraints, and success metrics.",
        ),
        TrackDefinition(
            track_key="knowledge_retrieval",
            display_name="Knowledge retrieval",
            owner_agent="rag_agent",
            stage_keys=("knowledge_context",),
            required_inputs=("knowledge_collection", "source_documents", "operation_query"),
            expected_outputs=("evidence_snapshot", "source_coverage", "claim_boundaries"),
            boundary="Reads approved knowledge only; retrieved sources must remain reviewable.",
            execution_boundary="metadata_only_review_required",
            available_actions=("search_knowledge", "generate_evidence_snapshot", "review_source_coverage"),
            quality_gates=("sources_are_reviewable", "claims_have_evidence", "workspace_scope_is_enforced"),
            next_action="Prepare or review knowledge evidence before content production.",
        ),
        TrackDefinition(
            track_key="content_strategy",
            display_name="Content strategy",
            owner_agent="content_strategy_agent",
            stage_keys=("content_production",),
            required_inputs=("operation_objective", "rag_evidence", "channel_requirements"),
            expected_outputs=("content_mode_decision", "content_brief", "asset_plan"),
            boundary="Chooses a content mode and brief only; it does not generate final media or publish.",
            execution_boundary="metadata_only_review_required",
            available_actions=("choose_content_mode", "prepare_content_brief", "define_asset_plan"),
            quality_gates=("content_mode_matches_goal", "channel_constraints_are_named", "approval_required"),
            next_action="Choose whether this cycle needs text, visual assets, video, or a mixed package.",
        ),
        TrackDefinition(
            track_key="text_content",
            display_name="Text content",
            owner_agent="text_content_agent",
            stage_keys=("content_production", "content_improvement"),
            required_inputs=("operation_objective", "rag_evidence", "channel_requirements"),
            expected_outputs=("title", "copy", "script", "comment_reply", "private_message"),
            boundary="Creates reviewable text artifacts only; no publishing occurs.",
            execution_boundary="metadata_only_review_required",
            available_actions=("generate_copy_draft", "generate_script", "generate_reply_templates"),
            quality_gates=("evidence_backed_claims", "channel_fit", "human_review_before_publish"),
            next_action="Generate or refine reviewed text assets for the current channel.",
        ),
        TrackDefinition(
            track_key="visual_asset",
            display_name="Visual asset",
            owner_agent="visual_asset_agent",
            stage_keys=("content_production",),
            required_inputs=("asset_brief", "brand_constraints", "source_materials"),
            expected_outputs=("cover_brief", "poster_brief", "image_workflow_candidates"),
            boundary="Prepares visual briefs and workflow candidates; generation remains behind review/runtime gates.",
            execution_boundary="metadata_only_until_guarded_runtime",
            available_actions=("prepare_visual_brief", "rank_image_workflows", "request_asset_review"),
            quality_gates=("brand_consistency", "asset_rights_reviewed", "workflow_runtime_validated"),
            next_action="Prepare visual asset requirements or image workflow candidates.",
        ),
        TrackDefinition(
            track_key="video_content",
            display_name="Video content",
            owner_agent="video_content_agent",
            stage_keys=("content_production",),
            required_inputs=("script", "source_materials", "video_analysis_result", "workflow_knowledge"),
            expected_outputs=("shot_plan", "workflow_candidates", "video_execution_package"),
            boundary="Plans video and selects workflows only; ComfyUI rendering remains gated.",
            execution_boundary="metadata_only_until_guarded_runtime",
            available_actions=("prepare_video_brief", "request_video_analysis", "rank_video_workflows"),
            quality_gates=("video_analysis_verified", "model_readiness_verified", "human_review_before_render"),
            next_action="Prepare the video brief and workflow candidates without starting rendering.",
        ),
        TrackDefinition(
            track_key="workflow_selection",
            display_name="Workflow selection",
            owner_agent="workflow_selection_agent",
            stage_keys=("content_production",),
            required_inputs=("operation_brief", "asset_state", "workflow_rag_documents"),
            expected_outputs=("ranked_workflows", "rejected_workflows", "execution_package_draft"),
            boundary="Ranks workflows and prepares contracts; it does not mutate ComfyUI graphs or submit queues.",
            execution_boundary="metadata_only_until_guarded_runtime",
            available_actions=("rank_workflows", "prepare_execution_package", "record_rejected_workflows"),
            quality_gates=("workflow_knowledge_ingested", "required_models_verified", "fallback_workflow_named"),
            next_action="Rank workflow candidates from approved workflow knowledge before execution planning.",
        ),
        TrackDefinition(
            track_key="production_intervention",
            display_name="Production intervention",
            owner_agent="commercial_operation_agent",
            stage_keys=("production_intervention",),
            required_inputs=("intervention_queue_item", "recommended_action", "operator_confirmation"),
            expected_outputs=("reviewable_intervention_action", "operator_next_step", "audit_boundary"),
            boundary="Routes stale/watch closed-loop intervention only; it does not execute, acknowledge, remind, publish, or control accounts automatically.",
            execution_boundary="metadata_only_review_required",
            available_actions=(
                "acknowledge_intervention_queue_item",
                "record_intervention_reminder_dispatch",
                "wait_for_reminder_cooldown",
                "review_intervention_queue_item",
            ),
            quality_gates=(
                "operator_confirmed_required",
                "dedicated_endpoint_required",
                "no_server_side_openclaw_or_playwright",
            ),
            next_action="Review the production intervention recommendation before using the dedicated queue endpoint.",
        ),
        TrackDefinition(
            track_key="production_delivery",
            display_name="Production delivery plan",
            owner_agent="commercial_operation_agent",
            stage_keys=("production_delivery",),
            required_inputs=("delivery_plan", "recommended_gate", "operator_confirmation"),
            expected_outputs=("reviewable_delivery_gate", "operator_next_step", "delivery_boundary"),
            boundary="Routes workspace delivery gates only; it does not approve, publish, execute OpenClaw, or control accounts automatically.",
            execution_boundary="metadata_only_review_required",
            available_actions=(
                "review_delivery_gate",
                "resolve_operation_readiness_gate",
                "configure_real_openclaw_publish_provider",
                "acknowledge_intervention_queue_item",
            ),
            quality_gates=(
                "delivery_plan_is_derived_from_acceptance_summary",
                "operator_confirmed_required",
                "no_server_side_openclaw_or_playwright",
            ),
            next_action="Review the production delivery gate plan and resolve the recommended gate manually.",
        ),
        TrackDefinition(
            track_key="review_gate",
            display_name="Human review gate",
            owner_agent="review_agent",
            stage_keys=("human_approval",),
            required_inputs=("drafts", "evidence", "execution_request", "risk_controls"),
            expected_outputs=("approval_decision", "reviewer_notes", "audit_status"),
            boundary="Blocks execution until an operator explicitly approves the next step.",
            execution_boundary="metadata_only_review_required",
            available_actions=("approve", "reject", "request_changes", "archive"),
            quality_gates=("reviewer_identity_recorded", "risk_controls_reviewed", "approval_audit_written"),
            next_action="Approve, reject, or request changes before any execution handoff.",
        ),
        TrackDefinition(
            track_key="client_execution",
            display_name="Client execution",
            owner_agent="client_execution_agent",
            stage_keys=("client_execution",),
            required_inputs=("approved_deliverable", "customer_account_confirmation", "execution_runbook"),
            expected_outputs=("openclaw_playwright_handoff", "execution_run_record"),
            boundary="Customer-machine execution only after approval; server does not control accounts directly.",
            execution_boundary="client_machine_after_approval",
            available_actions=("prepare_handoff", "start_execution_run", "record_failure_recovery"),
            quality_gates=("approval_complete", "customer_machine_ready", "account_control_not_server_side"),
            next_action="Prepare or run the approved customer-machine execution handoff.",
        ),
        TrackDefinition(
            track_key="result_recording",
            display_name="Result recording",
            owner_agent="publish_result_agent",
            stage_keys=("result_recording",),
            required_inputs=("execution_run_record", "operator_evidence", "business_signal"),
            expected_outputs=("result_record", "evidence_links", "outcome_summary"),
            boundary="Stores operator-observed results; it does not ingest platform analytics automatically.",
            execution_boundary="metadata_only_review_required",
            available_actions=("record_result", "attach_evidence", "send_result_for_review"),
            quality_gates=("execution_run_terminal", "evidence_attached", "result_review_required"),
            next_action="Record execution outcome, evidence, and commercial signals.",
        ),
        TrackDefinition(
            track_key="analytics_observation",
            display_name="Analytics observation",
            owner_agent="analytics_agent",
            stage_keys=("data_observation",),
            required_inputs=("approved_result", "metric_snapshot", "qualitative_signal"),
            expected_outputs=("monitoring_observation", "signal_summary", "anomaly_notes"),
            boundary="Captures reviewed metrics and notes only; no automatic account scraping occurs.",
            execution_boundary="metadata_only_review_required",
            available_actions=("record_metric_snapshot", "summarize_comment_topics", "mark_anomalies"),
            quality_gates=("result_approved", "metric_source_named", "observation_review_required"),
            next_action="Capture observed platform metrics and qualitative signals.",
        ),
        TrackDefinition(
            track_key="analytics_optimization",
            display_name="Analytics and optimization",
            owner_agent="analytics_agent",
            stage_keys=("data_analysis",),
            required_inputs=("approved_observation", "operation_objective", "risk_controls"),
            expected_outputs=("optimization_decision", "next_cycle_brief"),
            boundary="Produces reviewed recommendations only; it does not auto-change live campaigns.",
            execution_boundary="metadata_only_reviewed_recommendation",
            available_actions=("create_optimization_decision", "compare_previous_results", "prepare_next_cycle_brief"),
            quality_gates=("observation_approved", "evidence_supports_recommendation", "review_before_next_cycle"),
            next_action="Analyze approved observations and prepare the next reviewed optimization decision.",
        ),
        TrackDefinition(
            track_key="next_cycle_content",
            display_name="Next-cycle content",
            owner_agent="content_strategy_agent",
            stage_keys=("content_improvement",),
            required_inputs=("approved_optimization_decision", "previous_artifacts", "latest_evidence"),
            expected_outputs=("next_cycle_operation_plan", "next_cycle_production_tasks", "next_loop_start"),
            boundary="Prepares the next reviewed production cycle; it does not publish or execute.",
            execution_boundary="metadata_only_review_required",
            available_actions=("prepare_next_cycle", "carry_forward_improvements", "request_new_draft"),
            quality_gates=("optimization_decision_approved", "changes_are_reviewable", "new_cycle_has_approval_gate"),
            next_action="Use the approved optimization decision to prepare the next production cycle.",
        ),
    )

    def plan(
        self,
        *,
        operation: dict[str, Any],
        loop_summary: dict[str, Any],
        skills: list[dict[str, Any]],
        next_skill_key: str | None,
        next_action: str,
        evidence: list[str],
        orchestration_status: str,
        production_intervention_queue: dict[str, Any] | None = None,
        production_delivery_plan: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Return a complete, reviewable global routing plan."""

        current_stage = str(loop_summary.get("current_stage_key") or "loop_complete")
        signals = self._operation_signals(operation=operation)
        skills_by_stage = {str(skill.get("stage_key")): skill for skill in skills}
        clean_production_intervention_queue = production_intervention_queue or {}
        clean_production_delivery_plan = production_delivery_plan or {}
        track_key = self._select_track(
            current_stage=current_stage,
            signals=signals,
            skills_by_stage=skills_by_stage,
            next_skill_key=next_skill_key,
            production_intervention_queue=clean_production_intervention_queue,
            production_delivery_plan=clean_production_delivery_plan,
        )
        specialist_tracks = self._build_specialist_tracks(
            operation=operation,
            loop_summary=loop_summary,
            current_stage=current_stage,
            selected_track_key=track_key,
            signals=signals,
            skills_by_stage=skills_by_stage,
            production_intervention_queue=clean_production_intervention_queue,
            production_delivery_plan=clean_production_delivery_plan,
        )
        routing_decision = self._build_operation_routing_decision(
            operation=operation,
            loop_summary=loop_summary,
            specialist_tracks=specialist_tracks,
            selected_track_key=track_key,
            next_skill_key=next_skill_key,
            next_action=next_action,
            evidence=evidence,
            signals=signals,
            current_stage=current_stage,
            production_intervention_queue=clean_production_intervention_queue,
            production_delivery_plan=clean_production_delivery_plan,
        )
        return {
            "controller_agent": self._controller_agent(),
            "routing_decision": routing_decision,
            "specialist_tracks": specialist_tracks,
            "route_decision": {
                "decision_key": "route_next_skill",
                "agent_name": self.agent_name,
                "skill_key": routing_decision["recommended_track"],
                "decision_type": "global_operation_routing",
                "status": orchestration_status,
                "rationale": routing_decision["rationale"],
                "next_action": routing_decision["next_action"],
                "evidence": routing_decision["evidence"],
            },
        }

    def _controller_agent(self) -> dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "display_name": "Commercial Operation Agent",
            "mode": "deterministic_global_orchestrator",
            "uses_existing_agents": [
                "rag_agent",
                "operation_strategy_agent",
                "content_strategy_agent",
                "text_content_agent",
                "visual_asset_agent",
                "video_content_agent",
                "workflow_selection_agent",
                "review_agent",
                "client_execution_agent",
                "publish_result_agent",
                "analytics_agent",
            ],
            "capabilities": [
                "goal_to_plan",
                "stage_aware_routing",
                "content_mode_selection",
                "specialist_track_selection",
                "knowledge_grounding",
                "execution_contract_generation",
                "approval_boundary",
                "client_handoff",
                "metric_feedback",
                "next_cycle_planning",
            ],
        }

    def _select_track(
        self,
        *,
        current_stage: str,
        signals: dict[str, Any],
        skills_by_stage: dict[str, dict[str, Any]],
        next_skill_key: str | None,
        production_intervention_queue: dict[str, Any],
        production_delivery_plan: dict[str, Any],
    ) -> str:
        if self._operation_needs_production_intervention(production_intervention_queue):
            return "production_intervention"
        if next_skill_key == "production_delivery_skill":
            return "production_delivery"
        if current_stage in {"operation_topic", "task_planning"}:
            return "operation_strategy"
        if current_stage == "knowledge_context":
            return "knowledge_retrieval"
        if current_stage == "content_production":
            if signals["needs_video"]:
                return "video_content"
            if signals["needs_visual"]:
                return "visual_asset"
            if signals["needs_workflow"]:
                return "workflow_selection"
            if not signals["has_clear_content_mode"]:
                return "content_strategy"
            return "text_content"
        if current_stage == "human_approval":
            return "review_gate"
        if current_stage == "client_execution":
            return "client_execution"
        if current_stage == "result_recording":
            return "result_recording"
        if current_stage == "data_observation":
            return "analytics_observation"
        if current_stage == "data_analysis":
            return "analytics_optimization"
        if current_stage == "content_improvement":
            return "next_cycle_content"
        if next_skill_key:
            return self._track_for_skill(next_skill_key)
        if self._skill_status(skills_by_stage, "content_improvement") == "complete":
            return "next_cycle_content"
        return "operation_strategy"

    @staticmethod
    def _track_for_skill(skill_key: str) -> str:
        mapping = {
            "operation_intake_skill": "operation_strategy",
            "task_planning_skill": "operation_strategy",
            "knowledge_retrieval_skill": "knowledge_retrieval",
            "content_generation_skill": "content_strategy",
            "approval_gate_skill": "review_gate",
            "client_execution_skill": "client_execution",
            "result_recording_skill": "result_recording",
            "data_observation_skill": "analytics_observation",
            "analysis_improvement_skill": "analytics_optimization",
            "next_cycle_content_skill": "next_cycle_content",
            "production_delivery_skill": "production_delivery",
        }
        return mapping.get(skill_key, "operation_strategy")

    def _build_specialist_tracks(
        self,
        *,
        operation: dict[str, Any],
        loop_summary: dict[str, Any],
        current_stage: str,
        selected_track_key: str,
        signals: dict[str, Any],
        skills_by_stage: dict[str, dict[str, Any]],
        production_intervention_queue: dict[str, Any],
        production_delivery_plan: dict[str, Any],
    ) -> list[dict[str, Any]]:
        tracks = []
        production_intervention_action = self._production_intervention_action(production_intervention_queue)
        production_delivery_gate = self._production_delivery_gate(production_delivery_plan)
        for definition in self.track_definitions:
            blocked_by = self._blocked_by(
                definition=definition,
                selected_track_key=selected_track_key,
                loop_summary=loop_summary,
                operation=operation,
                signals=signals,
                skills_by_stage=skills_by_stage,
            )
            status = self._track_status(
                definition=definition,
                current_stage=current_stage,
                selected_track_key=selected_track_key,
                blocked_by=blocked_by,
                skills_by_stage=skills_by_stage,
            )
            tracks.append(
                {
                    "track_key": definition.track_key,
                    "display_name": definition.display_name,
                    "owner_agent": definition.owner_agent,
                    "stage_key": definition.stage_keys[0],
                    "status": status,
                    "priority": self._track_priority(definition, selected_track_key=selected_track_key, status=status),
                    "trigger_signals": self._track_signals(definition.track_key, signals),
                    "required_inputs": list(definition.required_inputs),
                    "expected_outputs": list(definition.expected_outputs),
                    "boundary": definition.boundary,
                    "execution_boundary": definition.execution_boundary,
                    "available_actions": list(definition.available_actions),
                    "quality_gates": list(definition.quality_gates),
                    "blocked_by": blocked_by,
                    "next_action": self._track_next_action(definition, selected_track_key, blocked_by),
                    "production_intervention_recommended_action": (
                        production_intervention_action if definition.track_key == "production_intervention" else {}
                    ),
                    "production_delivery_recommended_gate": (
                        production_delivery_gate if definition.track_key == "production_delivery" else {}
                    ),
                }
            )
        return sorted(tracks, key=lambda item: item["priority"], reverse=True)

    def _build_operation_routing_decision(
        self,
        *,
        operation: dict[str, Any],
        loop_summary: dict[str, Any],
        specialist_tracks: list[dict[str, Any]],
        selected_track_key: str,
        next_skill_key: str | None,
        next_action: str,
        evidence: list[str],
        signals: dict[str, Any],
        current_stage: str,
        production_intervention_queue: dict[str, Any],
        production_delivery_plan: dict[str, Any],
    ) -> dict[str, Any]:
        selected_track = next(
            (track for track in specialist_tracks if track["track_key"] == selected_track_key),
            specialist_tracks[0] if specialist_tracks else None,
        )
        selected_agents = self._selected_agents(selected_track_key=selected_track_key)
        required_collections = self._required_knowledge_collections(
            operation=operation,
            selected_track_key=selected_track_key,
        )
        blocked_by = list(selected_track.get("blocked_by", [])) if selected_track else []
        reason_codes = self._reason_codes(
            selected_track_key=selected_track_key,
            current_stage=current_stage,
            signals=signals,
            blocked_by=blocked_by,
            production_intervention_queue=production_intervention_queue,
            production_delivery_plan=production_delivery_plan,
        )
        contract = self._execution_contract(
            operation=operation,
            selected_track=selected_track,
            selected_track_key=selected_track_key,
            current_stage=current_stage,
            next_skill_key=next_skill_key,
            required_collections=required_collections,
            signals=signals,
            production_intervention_queue=production_intervention_queue,
            production_delivery_plan=production_delivery_plan,
        )
        rationale = self._routing_rationale(
            operation=operation,
            track_key=selected_track_key,
            current_stage=current_stage,
            next_skill_key=next_skill_key,
            reason_codes=reason_codes,
            production_intervention_queue=production_intervention_queue,
            production_delivery_plan=production_delivery_plan,
        )
        production_intervention_action = self._production_intervention_action(production_intervention_queue)
        intervention_required = self._operation_needs_production_intervention(production_intervention_queue)
        production_delivery_gate = self._production_delivery_gate(production_delivery_plan)
        delivery_required = self._operation_needs_production_delivery_plan(
            production_delivery_plan,
            current_stage=current_stage,
        )
        return {
            "decision_key": "operation_routing_decision",
            "controller_agent": self.agent_name,
            "decision_mode": "deterministic_stage_and_signal_router",
            "confidence": self._confidence(selected_track=selected_track, blocked_by=blocked_by),
            "current_stage": None if current_stage == "loop_complete" else current_stage,
            "recommended_track": selected_track_key,
            "selected_track_status": selected_track.get("status") if selected_track else "waiting",
            "selected_skill_key": next_skill_key,
            "selected_agents": selected_agents,
            "required_knowledge_collections": required_collections,
            "required_inputs": list(selected_track.get("required_inputs", [])) if selected_track else [],
            "blocked_by": blocked_by,
            "reason_codes": reason_codes,
            "quality_gates": list(selected_track.get("quality_gates", [])) if selected_track else [],
            "next_executable_contract": contract,
            "production_intervention_required": intervention_required,
            "production_intervention_recommended_action": production_intervention_action,
            "production_intervention_queue_summary": (
                production_intervention_queue.get("queue_summary")
                if isinstance(production_intervention_queue.get("queue_summary"), dict)
                else {}
            ),
            "production_delivery_plan_required": delivery_required,
            "production_delivery_recommended_gate": production_delivery_gate,
            "production_delivery_plan_summary": self._production_delivery_plan_summary(production_delivery_plan),
            "rationale": rationale,
            "next_action": self._decision_next_action(
                selected_track,
                next_action,
                production_intervention_queue=production_intervention_queue,
                production_delivery_plan=production_delivery_plan,
            ),
            "evidence": [
                *evidence,
                f"recommended_track={selected_track_key}",
                f"selected_skill_key={next_skill_key or 'loop_complete'}",
                *self._production_intervention_evidence(production_intervention_queue),
                *self._production_delivery_evidence(production_delivery_plan),
                *[f"signal:{item}" for item in signals["matched_signals"]],
                *[f"blocked_by:{item}" for item in blocked_by],
            ],
        }

    def _execution_contract(
        self,
        *,
        operation: dict[str, Any],
        selected_track: dict[str, Any] | None,
        selected_track_key: str,
        current_stage: str,
        next_skill_key: str | None,
        required_collections: list[str],
        signals: dict[str, Any],
        production_intervention_queue: dict[str, Any],
        production_delivery_plan: dict[str, Any],
    ) -> dict[str, Any]:
        owner_agent = selected_track.get("owner_agent") if selected_track else self.agent_name
        production_intervention_action = self._production_intervention_action(production_intervention_queue)
        production_delivery_gate = self._production_delivery_gate(production_delivery_plan)
        return {
            "contract_version": "1.0",
            "track": selected_track_key,
            "selected_agent": owner_agent,
            "selected_skill_key": next_skill_key,
            "selected_workflow": None,
            "handoff_target": self._handoff_target(selected_track_key),
            "input_assets": [],
            "parameters": {
                "operation_id": str(operation.get("id") or ""),
                "current_stage": None if current_stage == "loop_complete" else current_stage,
                "next_skill_key": next_skill_key,
                "knowledge_collections": required_collections,
                "matched_signals": signals["matched_signals"],
                "production_intervention_required": self._operation_needs_production_intervention(
                    production_intervention_queue
                ),
                "production_intervention_recommended_action": production_intervention_action,
                "production_delivery_plan_required": self._operation_needs_production_delivery_plan(
                    production_delivery_plan,
                    current_stage=current_stage,
                ),
                "production_delivery_recommended_gate": production_delivery_gate,
                "production_delivery_plan_summary": self._production_delivery_plan_summary(production_delivery_plan),
            },
            "requested_outputs": list(selected_track.get("expected_outputs", [])) if selected_track else [],
            "allowed_actions": list(selected_track.get("available_actions", [])) if selected_track else [],
            "forbidden_actions": self._forbidden_actions(selected_track_key),
            "quality_gates": list(selected_track.get("quality_gates", [])) if selected_track else [],
            "approval_required": True,
            "execution_boundary": selected_track.get("execution_boundary") if selected_track else "metadata_only_review_required",
            "status": "blocked" if selected_track and selected_track.get("blocked_by") else "draft",
        }

    def _blocked_by(
        self,
        *,
        definition: TrackDefinition,
        selected_track_key: str,
        loop_summary: dict[str, Any],
        operation: dict[str, Any],
        signals: dict[str, Any],
        skills_by_stage: dict[str, dict[str, Any]],
    ) -> list[str]:
        counts = loop_summary.get("counts", {}) if isinstance(loop_summary.get("counts"), dict) else {}
        blocked: list[str] = []
        knowledge_ready = self._skill_status(skills_by_stage, "knowledge_context") == "complete"
        approval_ready = self._skill_status(skills_by_stage, "human_approval") == "complete"
        execution_done = self._skill_status(skills_by_stage, "client_execution") == "complete"
        result_ready = self._skill_status(skills_by_stage, "result_recording") == "complete"
        observation_ready = self._skill_status(skills_by_stage, "data_observation") == "complete"

        if definition.track_key == "knowledge_retrieval":
            has_source = bool(operation.get("knowledge_collection")) or int(counts.get("knowledge_links", 0) or 0) > 0
            if not has_source:
                blocked.append("knowledge_source_missing")
        if definition.track_key in {"content_strategy", "text_content", "visual_asset", "video_content", "workflow_selection"}:
            if not knowledge_ready and selected_track_key == definition.track_key:
                blocked.append("knowledge_evidence_not_approved")
        if definition.track_key == "video_content":
            if signals["needs_video"]:
                metadata = operation.get("metadata") if isinstance(operation.get("metadata"), dict) else {}
                has_video_agent_package = bool(
                    metadata.get("video_agent_execution_package")
                    or metadata.get("video_agent_execution_package_id")
                    or metadata.get("workflow_selection")
                    or int(counts.get("production_tasks", 0) or 0) > 0
                )
                if not has_video_agent_package:
                    blocked.append("video_agent_execution_package_required")
        if definition.track_key == "workflow_selection" and selected_track_key == "workflow_selection":
            blocked.append("workflow_rag_ingestion_not_verified")
        if definition.track_key == "client_execution" and not approval_ready:
            blocked.append("human_approval_required")
        if definition.track_key == "result_recording" and not execution_done:
            blocked.append("completed_execution_run_required")
        if definition.track_key == "analytics_observation" and not result_ready:
            blocked.append("approved_result_required")
        if definition.track_key == "analytics_optimization" and not observation_ready:
            blocked.append("approved_observation_required")
        if definition.track_key == "next_cycle_content" and self._skill_status(skills_by_stage, "data_analysis") != "complete":
            blocked.append("approved_optimization_decision_required")
        return list(dict.fromkeys(blocked))

    def _track_status(
        self,
        *,
        definition: TrackDefinition,
        current_stage: str,
        selected_track_key: str,
        blocked_by: list[str],
        skills_by_stage: dict[str, dict[str, Any]],
    ) -> str:
        if definition.track_key == selected_track_key:
            return "blocked" if blocked_by else "recommended"
        stage_statuses = [self._skill_status(skills_by_stage, stage_key) for stage_key in definition.stage_keys]
        if stage_statuses and all(status == "complete" for status in stage_statuses):
            return "complete"
        if current_stage in definition.stage_keys:
            return "active"
        if blocked_by:
            return "blocked"
        return "available"

    @staticmethod
    def _track_priority(definition: TrackDefinition, *, selected_track_key: str, status: str) -> int:
        if definition.track_key == selected_track_key:
            return 100 if status != "blocked" else 95
        if status == "active":
            return 70
        if status == "available":
            return 30
        if status == "complete":
            return 10
        return 5

    @staticmethod
    def _track_next_action(definition: TrackDefinition, selected_track_key: str, blocked_by: list[str]) -> str:
        if definition.track_key != selected_track_key:
            return definition.next_action
        if blocked_by:
            return f"Resolve blocking condition(s): {', '.join(blocked_by)}."
        return definition.next_action

    def _operation_signals(self, *, operation: dict[str, Any]) -> dict[str, Any]:
        text = self._operation_text(operation)
        video_signals = self._matches(text, self.video_keywords)
        visual_signals = self._matches(text, self.visual_keywords)
        text_signals = self._matches(text, self.text_keywords)
        workflow_signals = self._matches(text, self.workflow_keywords)
        publish_signals = self._matches(text, self.publish_keywords)
        analytics_signals = self._matches(text, self.analytics_keywords)
        matched = list(
            dict.fromkeys(
                [
                    *video_signals,
                    *visual_signals,
                    *text_signals,
                    *workflow_signals,
                    *publish_signals,
                    *analytics_signals,
                ]
            )
        )
        return {
            "needs_video": bool(video_signals),
            "needs_visual": bool(visual_signals),
            "needs_text": bool(text_signals) or not (video_signals or visual_signals or workflow_signals),
            "needs_workflow": bool(workflow_signals),
            "needs_publish": bool(publish_signals),
            "needs_analytics": bool(analytics_signals),
            "has_clear_content_mode": bool(video_signals or visual_signals or text_signals or workflow_signals),
            "video_signals": video_signals,
            "visual_signals": visual_signals,
            "text_signals": text_signals or ["default_content_need"],
            "workflow_signals": workflow_signals,
            "publish_signals": publish_signals,
            "analytics_signals": analytics_signals,
            "matched_signals": matched,
        }

    @staticmethod
    def _operation_text(operation: dict[str, Any]) -> str:
        metadata = operation.get("metadata") if isinstance(operation.get("metadata"), dict) else {}
        metadata_text = " ".join(str(value) for value in metadata.values() if isinstance(value, str))
        return " ".join(
            [
                str(operation.get("title") or ""),
                str(operation.get("objective") or ""),
                str(operation.get("target_audience") or ""),
                " ".join(str(item) for item in operation.get("channels", []) or []),
                " ".join(str(item) for item in operation.get("success_metrics", []) or []),
                " ".join(str(item) for item in operation.get("constraints", []) or []),
                metadata_text,
            ]
        ).lower()

    @staticmethod
    def _matches(text: str, keywords: tuple[str, ...]) -> list[str]:
        return [keyword for keyword in keywords if keyword.lower() in text]

    @staticmethod
    def _skill_status(skills_by_stage: dict[str, dict[str, Any]], stage_key: str) -> str:
        return str((skills_by_stage.get(stage_key) or {}).get("status") or "waiting")

    @staticmethod
    def _track_signals(track_key: str, signals: dict[str, Any]) -> list[str]:
        if track_key == "production_intervention":
            return ["production_closed_loop_intervention_queue"]
        if track_key == "production_delivery":
            return ["production_closed_loop_delivery_plan"]
        if track_key == "video_content":
            return signals["video_signals"]
        if track_key == "visual_asset":
            return signals["visual_signals"]
        if track_key == "workflow_selection":
            return signals["workflow_signals"]
        if track_key == "text_content":
            return signals["text_signals"]
        if track_key == "client_execution":
            return signals["publish_signals"]
        if track_key in {"analytics_observation", "analytics_optimization"}:
            return signals["analytics_signals"]
        return []

    @staticmethod
    def _selected_agents(*, selected_track_key: str) -> list[str]:
        mapping = {
            "operation_strategy": ["commercial_operation_agent", "operation_strategy_agent"],
            "knowledge_retrieval": ["commercial_operation_agent", "rag_agent"],
            "content_strategy": ["commercial_operation_agent", "rag_agent", "content_strategy_agent"],
            "text_content": ["commercial_operation_agent", "rag_agent", "text_content_agent"],
            "visual_asset": ["commercial_operation_agent", "rag_agent", "visual_asset_agent", "workflow_selection_agent"],
            "video_content": ["commercial_operation_agent", "rag_agent", "video_content_agent", "workflow_selection_agent"],
            "workflow_selection": ["commercial_operation_agent", "rag_agent", "workflow_selection_agent"],
            "production_intervention": ["commercial_operation_agent", "review_agent"],
            "production_delivery": ["commercial_operation_agent", "review_agent"],
            "review_gate": ["commercial_operation_agent", "review_agent"],
            "client_execution": ["commercial_operation_agent", "review_agent", "client_execution_agent"],
            "result_recording": ["commercial_operation_agent", "publish_result_agent"],
            "analytics_observation": ["commercial_operation_agent", "analytics_agent"],
            "analytics_optimization": ["commercial_operation_agent", "analytics_agent", "review_agent"],
            "next_cycle_content": ["commercial_operation_agent", "content_strategy_agent", "text_content_agent"],
        }
        return mapping.get(selected_track_key, ["commercial_operation_agent"])

    def _required_knowledge_collections(self, *, operation: dict[str, Any], selected_track_key: str) -> list[str]:
        collections = []
        if operation.get("knowledge_collection"):
            collections.append(str(operation["knowledge_collection"]))
        if selected_track_key in {"visual_asset", "video_content", "workflow_selection"}:
            collections.append(self.workflow_collection)
        return list(dict.fromkeys(collections))

    @staticmethod
    def _reason_codes(
        *,
        selected_track_key: str,
        current_stage: str,
        signals: dict[str, Any],
        blocked_by: list[str],
        production_intervention_queue: dict[str, Any] | None = None,
        production_delivery_plan: dict[str, Any] | None = None,
    ) -> list[str]:
        codes = [f"stage:{current_stage}", f"track:{selected_track_key}"]
        production_intervention_action = CommercialOperationMainAgent._production_intervention_action(
            production_intervention_queue or {}
        )
        production_delivery_gate = CommercialOperationMainAgent._production_delivery_gate(
            production_delivery_plan or {}
        )
        if selected_track_key == "production_intervention":
            codes.append(
                f"production_intervention:{production_intervention_action.get('action_key') or 'none'}"
            )
        if selected_track_key == "production_delivery":
            codes.append(f"production_delivery_gate:{production_delivery_gate.get('gate_key') or 'none'}")
        if signals["matched_signals"]:
            codes.extend(f"signal:{signal}" for signal in signals["matched_signals"])
        if blocked_by:
            codes.extend(f"blocked:{item}" for item in blocked_by)
        return list(dict.fromkeys(codes))

    @staticmethod
    def _confidence(*, selected_track: dict[str, Any] | None, blocked_by: list[str]) -> float:
        if selected_track is None:
            return 0.0
        if selected_track.get("status") == "recommended" and not blocked_by:
            return 0.9
        if selected_track.get("status") == "blocked":
            return 0.72
        return 0.8

    @staticmethod
    def _handoff_target(selected_track_key: str) -> str:
        if selected_track_key == "client_execution":
            return "customer_machine"
        if selected_track_key == "production_delivery":
            return "server_metadata"
        if selected_track_key in {"video_content", "visual_asset", "workflow_selection"}:
            return "guarded_runtime_after_review"
        return "server_metadata"

    @staticmethod
    def _forbidden_actions(selected_track_key: str) -> list[str]:
        common = ["no_approval_bypass", "no_secret_exposure"]
        if selected_track_key == "production_intervention":
            return [
                *common,
                "no_intervention_record_without_operator_confirmation",
                "no_target_endpoint_execution_from_router",
                "no_server_side_openclaw_or_playwright",
            ]
        if selected_track_key == "production_delivery":
            return [
                *common,
                "no_delivery_gate_mutation_without_operator_confirmation",
                "no_target_endpoint_execution_from_router",
                "no_server_side_openclaw_or_playwright",
            ]
        if selected_track_key == "client_execution":
            return [*common, "no_server_side_account_control", "no_unapproved_publish"]
        if selected_track_key in {"video_content", "visual_asset", "workflow_selection"}:
            return [*common, "no_comfyui_queue_submit_without_runtime_gate", "no_model_download_or_install"]
        if selected_track_key in {"analytics_observation", "analytics_optimization"}:
            return [*common, "no_unapproved_platform_scraping", "no_roi_claim_without_evidence"]
        return [*common, "no_publish", "no_external_runtime_call"]

    @staticmethod
    def _routing_rationale(
        *,
        operation: dict[str, Any],
        track_key: str,
        current_stage: str,
        next_skill_key: str | None,
        reason_codes: list[str],
        production_intervention_queue: dict[str, Any] | None = None,
        production_delivery_plan: dict[str, Any] | None = None,
    ) -> str:
        title = str(operation.get("title") or "the operation")
        reason_text = ", ".join(reason_codes[:4])
        if track_key == "production_intervention":
            action = CommercialOperationMainAgent._production_intervention_action(
                production_intervention_queue or {}
            )
            return (
                f"{title} has a stale/watch production closed-loop intervention recommendation "
                f"({action.get('action_key') or 'none'}); the main Agent routes to operator review without executing it."
            )
        if track_key == "production_delivery":
            gate = CommercialOperationMainAgent._production_delivery_gate(production_delivery_plan or {})
            return (
                f"{title} has an open production delivery gate "
                f"({gate.get('gate_key') or 'none'}); the main Agent routes to the delivery plan without executing it."
            )
        if track_key == "video_content":
            return (
                f"{title} is in {current_stage}; video-oriented signals were found ({reason_text}), "
                "so the main Agent routes to the video specialist while rendering remains gated."
            )
        if track_key == "visual_asset":
            return (
                f"{title} is in {current_stage}; visual asset signals were found ({reason_text}), "
                "so the main Agent routes to visual asset planning before any generation runtime."
            )
        if track_key == "knowledge_retrieval":
            return (
                f"{title} is in {current_stage}; the next skill is {next_skill_key or 'knowledge retrieval'}, "
                "so source evidence must be prepared before production."
            )
        if track_key == "client_execution":
            return (
                f"{title} is in {current_stage}; approved handoff state should move through customer-machine "
                "execution controls, not server-side account control."
            )
        if track_key in {"analytics_observation", "analytics_optimization"}:
            return (
                f"{title} is in {current_stage}; the operation has reached feedback analysis, "
                "so the main Agent routes to analytics with review boundaries."
            )
        return (
            f"{title} is in {current_stage}; the main Agent routes to {track_key} based on "
            f"stage state and signals ({reason_text})."
        )

    @staticmethod
    def _decision_next_action(
        selected_track: dict[str, Any] | None,
        fallback: str,
        *,
        production_intervention_queue: dict[str, Any] | None = None,
        production_delivery_plan: dict[str, Any] | None = None,
    ) -> str:
        if selected_track is None:
            return fallback
        blocked_by = selected_track.get("blocked_by") or []
        if blocked_by:
            return f"Resolve blocking condition(s): {', '.join(str(item) for item in blocked_by)}."
        if selected_track.get("track_key") == "production_intervention":
            action = CommercialOperationMainAgent._production_intervention_action(
                production_intervention_queue or {}
            )
            action_key = str(action.get("action_key") or "review_intervention_queue_item")
            reason = str(action.get("reason") or "production_intervention_queue_recommended_action")
            return f"Review production intervention action `{action_key}` before using the dedicated endpoint: {reason}."
        if selected_track.get("track_key") == "production_delivery":
            gate = CommercialOperationMainAgent._production_delivery_gate(production_delivery_plan or {})
            gate_key = str(gate.get("gate_key") or "review_delivery_gate")
            action = str((gate.get("operator_next_actions") or ["Review the production delivery gate."])[0])
            return f"Review production delivery gate `{gate_key}` before using any target endpoint: {action}"
        return str(selected_track.get("next_action") or fallback)

    @staticmethod
    def _production_delivery_gate(production_delivery_plan: dict[str, Any]) -> dict[str, Any]:
        actions = production_delivery_plan.get("immediate_actions")
        if isinstance(actions, list):
            for action in actions:
                if isinstance(action, dict):
                    return action
        gate = production_delivery_plan.get("recommended_gate")
        return gate if isinstance(gate, dict) else {}

    @classmethod
    def _operation_needs_production_delivery_plan(
        cls,
        production_delivery_plan: dict[str, Any],
        *,
        current_stage: str,
    ) -> bool:
        gate = cls._production_delivery_gate(production_delivery_plan)
        if not gate:
            return False
        if str(gate.get("gate_status") or "complete") == "complete":
            return False
        gate_key = str(gate.get("gate_key") or "")
        if bool(production_delivery_plan.get("operation_gate_related")):
            return True
        return gate_key == "configure_real_openclaw_publish_provider" and current_stage in {
            "client_execution",
            "result_recording",
            "data_observation",
            "data_analysis",
            "content_improvement",
            "loop_complete",
        }

    @staticmethod
    def _production_delivery_plan_summary(production_delivery_plan: dict[str, Any]) -> dict[str, Any]:
        if not production_delivery_plan:
            return {}
        return {
            "contract": production_delivery_plan.get("contract"),
            "delivery_status": production_delivery_plan.get("delivery_status"),
            "completion_percent": production_delivery_plan.get("completion_percent"),
            "next_focus": production_delivery_plan.get("next_focus"),
            "open_gate_count": production_delivery_plan.get("open_gate_count"),
            "critical_gate_count": production_delivery_plan.get("critical_gate_count"),
            "ready_for_handoff": production_delivery_plan.get("ready_for_handoff"),
            "operation_gate_related": production_delivery_plan.get("operation_gate_related"),
        }

    @classmethod
    def _production_delivery_evidence(cls, production_delivery_plan: dict[str, Any]) -> list[str]:
        if not production_delivery_plan:
            return []
        gate = cls._production_delivery_gate(production_delivery_plan)
        return [
            f"production_delivery_status={production_delivery_plan.get('delivery_status') or 'none'}",
            f"production_delivery_gate={gate.get('gate_key') or 'none'}",
            f"production_delivery_contract={production_delivery_plan.get('contract') or 'none'}",
        ]

    @staticmethod
    def _production_intervention_action(production_intervention_queue: dict[str, Any]) -> dict[str, Any]:
        action = production_intervention_queue.get("recommended_action")
        return action if isinstance(action, dict) else {}

    @classmethod
    def _operation_needs_production_intervention(cls, production_intervention_queue: dict[str, Any]) -> bool:
        if not bool(production_intervention_queue.get("operation_in_queue")):
            return False
        item = production_intervention_queue.get("item")
        if isinstance(item, dict):
            staleness_status = str(item.get("staleness_status") or "none")
            escalation_recommended = bool(item.get("escalation_recommended"))
            if staleness_status == "watch" and not escalation_recommended:
                return False
        action_key = str(cls._production_intervention_action(production_intervention_queue).get("action_key") or "")
        return bool(action_key and action_key != "none")

    @classmethod
    def _production_intervention_evidence(cls, production_intervention_queue: dict[str, Any]) -> list[str]:
        if not production_intervention_queue:
            return []
        action = cls._production_intervention_action(production_intervention_queue)
        return [
            f"production_intervention_operation_in_queue={bool(production_intervention_queue.get('operation_in_queue'))}",
            f"production_intervention_action={action.get('action_key') or 'none'}",
            f"production_intervention_contract={action.get('contract') or 'none'}",
        ]
