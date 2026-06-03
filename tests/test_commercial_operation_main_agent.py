"""Commercial operation main Agent routing tests."""

from __future__ import annotations

from app.commercial_operations.main_agent import CommercialOperationMainAgent


def _operation(**overrides):  # type: ignore[no-untyped-def]
    payload = {
        "id": "operation-1",
        "workspace_id": "workspace-test",
        "title": "Lead generation operation",
        "objective": "Increase qualified leads with reviewed marketing content.",
        "target_audience": "local buyers",
        "channels": ["newsletter"],
        "knowledge_collection": "ai_knowledge_base",
        "success_metrics": ["qualified_leads"],
        "constraints": ["human approval required"],
        "metadata": {},
    }
    payload.update(overrides)
    return payload


def _loop(stage: str, *, counts: dict[str, int] | None = None) -> dict[str, object]:
    return {
        "loop_status": "in_progress",
        "current_stage_key": stage,
        "completion_ratio": 0.2,
        "counts": counts or {"knowledge_links": 0},
    }


def _skill(stage_key: str, status: str = "waiting") -> dict[str, str]:
    return {
        "skill_key": f"{stage_key}_skill",
        "stage_key": stage_key,
        "status": status,
    }


def _skills(**statuses: str) -> list[dict[str, str]]:
    stage_keys = [
        "operation_topic",
        "task_planning",
        "knowledge_context",
        "content_production",
        "human_approval",
        "client_execution",
        "result_recording",
        "data_observation",
        "data_analysis",
        "content_improvement",
    ]
    return [_skill(stage_key, statuses.get(stage_key, "waiting")) for stage_key in stage_keys]


def _plan(operation: dict, stage: str, *, statuses: dict[str, str] | None = None, counts: dict[str, int] | None = None):
    return CommercialOperationMainAgent().plan(
        operation=operation,
        loop_summary=_loop(stage, counts=counts),
        skills=_skills(**(statuses or {})),
        next_skill_key=f"{stage}_skill",
        next_action="Next action from loop.",
        evidence=["loop_status=in_progress"],
        orchestration_status="active",
    )


def _plan_with_intervention(operation: dict):
    return CommercialOperationMainAgent().plan(
        operation=operation,
        loop_summary=_loop("content_production", counts={"knowledge_links": 1}),
        skills=_skills(knowledge_context="complete"),
        next_skill_key="content_production_skill",
        next_action="Next action from loop.",
        evidence=["loop_status=in_progress"],
        orchestration_status="active",
        production_intervention_queue={
            "contract": "production_closed_loop_intervention_main_agent_input",
            "operation_in_queue": True,
            "queue_summary": {"contract": "production_closed_loop_intervention_queue_summary"},
            "recommended_action": {
                "contract": "production_closed_loop_intervention_queue_recommended_action",
                "action_key": "acknowledge_intervention_queue_item",
                "reason": "highest_priority_item_has_no_operator_acknowledgement",
                "operator_confirmed_required": True,
                "server_side_external_execution": False,
            },
        },
    )


def _plan_with_delivery_gate(operation: dict, *, stage: str = "loop_complete"):
    return CommercialOperationMainAgent().plan(
        operation=operation,
        loop_summary=_loop(stage, counts={"knowledge_links": 1}),
        skills=_skills(knowledge_context="complete", human_approval="complete"),
        next_skill_key=f"{stage}_skill",
        next_action="Next action from loop.",
        evidence=["loop_status=in_progress"],
        orchestration_status="active",
        production_delivery_plan={
            "contract": "production_closed_loop_delivery_plan_main_agent_input",
            "delivery_status": "blocked_by_critical_gate",
            "completion_percent": 85,
            "next_focus": "configure_real_openclaw_publish_provider",
            "open_gate_count": 1,
            "critical_gate_count": 1,
            "ready_for_handoff": False,
            "operation_gate_related": False,
            "immediate_actions": [
                {
                    "gate_key": "configure_real_openclaw_publish_provider",
                    "gate_status": "critical",
                    "title": "Configure real OpenClaw publish provider",
                    "owner": "technical_operator",
                    "blocking_reasons": ["openclaw_provider_is_mock"],
                    "operator_next_actions": ["Switch the customer-machine OpenClaw provider from mock."],
                }
            ],
        },
    )


def test_main_agent_routes_knowledge_stage_before_content() -> None:
    plan = _plan(_operation(), "knowledge_context")

    decision = plan["routing_decision"]
    assert decision["recommended_track"] == "knowledge_retrieval"
    assert decision["selected_agents"] == ["commercial_operation_agent", "rag_agent"]
    assert decision["next_executable_contract"]["track"] == "knowledge_retrieval"
    assert decision["next_executable_contract"]["status"] == "draft"


def test_main_agent_blocks_knowledge_when_no_source_exists() -> None:
    plan = _plan(
        _operation(knowledge_collection=None),
        "knowledge_context",
        counts={"knowledge_links": 0},
    )

    decision = plan["routing_decision"]
    assert decision["recommended_track"] == "knowledge_retrieval"
    assert "knowledge_source_missing" in decision["blocked_by"]
    assert decision["next_executable_contract"]["status"] == "blocked"


def test_main_agent_routes_video_signal_without_running_runtime() -> None:
    plan = _plan(
        _operation(
            title="Douyin KTV digital human video campaign",
            objective="Use a scene image to make a short video with a digital human spokesperson.",
            channels=["douyin"],
        ),
        "content_production",
        statuses={"knowledge_context": "complete"},
    )

    decision = plan["routing_decision"]
    assert decision["recommended_track"] == "video_content"
    assert "video_content_agent" in decision["selected_agents"]
    assert "workflow_selection_agent" in decision["selected_agents"]
    assert "comfyui_cu130_workflows" in decision["required_knowledge_collections"]
    assert "video_agent_execution_package_required" in decision["blocked_by"]
    assert "video_analysis_model_not_verified" not in decision["blocked_by"]
    assert decision["next_executable_contract"]["execution_boundary"] == "metadata_only_until_guarded_runtime"
    assert "no_comfyui_queue_submit_without_runtime_gate" in decision["next_executable_contract"]["forbidden_actions"]


def test_main_agent_routes_ambiguous_content_to_content_strategy() -> None:
    plan = _plan(
        _operation(objective="Improve customer acquisition for the next campaign."),
        "content_production",
        statuses={"knowledge_context": "complete"},
    )

    decision = plan["routing_decision"]
    assert decision["recommended_track"] == "content_strategy"
    assert "content_strategy_agent" in decision["selected_agents"]


def test_main_agent_routes_later_loop_stages() -> None:
    cases = [
        ("human_approval", "review_gate"),
        ("client_execution", "client_execution"),
        ("result_recording", "result_recording"),
        ("data_observation", "analytics_observation"),
        ("data_analysis", "analytics_optimization"),
        ("content_improvement", "next_cycle_content"),
    ]
    for stage, expected_track in cases:
        plan = _plan(_operation(), stage)
        assert plan["routing_decision"]["recommended_track"] == expected_track


def test_main_agent_prioritizes_production_intervention_recommended_action() -> None:
    plan = _plan_with_intervention(_operation())

    decision = plan["routing_decision"]
    assert decision["recommended_track"] == "production_intervention"
    assert decision["production_intervention_required"] is True
    assert (
        decision["production_intervention_recommended_action"]["contract"]
        == "production_closed_loop_intervention_queue_recommended_action"
    )
    assert decision["production_intervention_recommended_action"]["action_key"] == "acknowledge_intervention_queue_item"
    assert decision["next_executable_contract"]["track"] == "production_intervention"
    assert decision["next_executable_contract"]["parameters"]["production_intervention_required"] is True
    assert "no_target_endpoint_execution_from_router" in decision["next_executable_contract"]["forbidden_actions"]
    assert any(item == "production_intervention_action=acknowledge_intervention_queue_item" for item in decision["evidence"])
    assert plan["specialist_tracks"][0]["track_key"] == "production_intervention"


def test_main_agent_exposes_delivery_plan_gate_without_stealing_route() -> None:
    plan = _plan_with_delivery_gate(_operation(), stage="content_improvement")

    decision = plan["routing_decision"]
    assert decision["recommended_track"] == "next_cycle_content"
    assert decision["production_delivery_plan_required"] is True
    assert decision["production_delivery_recommended_gate"]["gate_key"] == "configure_real_openclaw_publish_provider"
    assert decision["production_delivery_plan_summary"]["contract"] == "production_closed_loop_delivery_plan_main_agent_input"
    assert decision["next_executable_contract"]["track"] == "next_cycle_content"
    assert (
        decision["next_executable_contract"]["parameters"]["production_delivery_recommended_gate"]["gate_key"]
        == "configure_real_openclaw_publish_provider"
    )
    assert any(item == "production_delivery_gate=configure_real_openclaw_publish_provider" for item in decision["evidence"])
    assert plan["specialist_tracks"][0]["track_key"] == "next_cycle_content"


def test_main_agent_routes_explicit_delivery_skill_to_delivery_plan_gate() -> None:
    plan = CommercialOperationMainAgent().plan(
        operation=_operation(),
        loop_summary=_loop("content_improvement", counts={"knowledge_links": 1}),
        skills=_skills(knowledge_context="complete", human_approval="complete"),
        next_skill_key="production_delivery_skill",
        next_action="Next action from loop.",
        evidence=["loop_status=in_progress"],
        orchestration_status="active",
        production_delivery_plan={
            "contract": "production_closed_loop_delivery_plan_main_agent_input",
            "delivery_status": "blocked_by_critical_gate",
            "completion_percent": 85,
            "next_focus": "configure_real_openclaw_publish_provider",
            "open_gate_count": 1,
            "critical_gate_count": 1,
            "ready_for_handoff": False,
            "operation_gate_related": False,
            "immediate_actions": [
                {
                    "gate_key": "configure_real_openclaw_publish_provider",
                    "gate_status": "critical",
                    "title": "Configure real OpenClaw publish provider",
                    "owner": "technical_operator",
                    "blocking_reasons": ["openclaw_provider_is_mock"],
                    "operator_next_actions": ["Switch the customer-machine OpenClaw provider from mock."],
                }
            ],
        },
    )

    decision = plan["routing_decision"]
    assert decision["recommended_track"] == "production_delivery"
    assert decision["next_executable_contract"]["track"] == "production_delivery"
    assert "no_target_endpoint_execution_from_router" in decision["next_executable_contract"]["forbidden_actions"]
    assert plan["specialist_tracks"][0]["track_key"] == "production_delivery"
