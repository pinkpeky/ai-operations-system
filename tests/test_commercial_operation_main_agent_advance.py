"""Commercial operation main Agent loop advancement tests."""

from __future__ import annotations

import json
from uuid import UUID

import pytest
from pydantic import TypeAdapter
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes.commercial_operations import advance_commercial_operation_main_agent_loop
from app.commercial_operations import service as commercial_operation_service
from app.commercial_operations.service import CommercialOperationService
from app.core.workspace_context import WorkspaceContext
from app.models import (
    CommercialOperation,
    CommercialOperationApproval,
    CommercialOperationAssetRequest,
    CommercialOperationContentDraft,
    CommercialOperationDeliverable,
    CommercialOperationEvidenceSnapshot,
    CommercialOperationExecutionRequest,
    CommercialOperationExecutionRun,
    CommercialOperationMonitoringObservation,
    CommercialOperationOptimizationDecision,
    CommercialOperationPlan,
    CommercialOperationProductionTask,
    CommercialOperationResult,
)
from app.schemas.commercial_operation import (
    CommercialOperationMainAgentAdvanceRequest,
    CommercialOperationMainAgentAdvanceResponse,
)
from app.schemas.llm import LLMHealthResponse, LLMRequest, LLMResponse


def _record_id(response: dict, bucket: str = "created_records") -> UUID:
    return UUID(response[bucket][0]["id"])


class FakeOperationPlanLLMClient:
    last_request: LLMRequest | None = None

    def __init__(self, settings=None) -> None:  # type: ignore[no-untyped-def]
        self.settings = settings

    async def health_check(self) -> LLMHealthResponse:
        return LLMHealthResponse(provider="local", model="fake-operation-planner", reachable=True)

    async def generate(self, request: LLMRequest) -> LLMResponse:
        type(self).last_request = request
        payload = {
            "title": "LLM plan: commercial KTV launch",
            "objective_summary": "LLM generated objective summary with booking conversion, approval gates, and material assumptions.",
            "audience_strategy": "Local guests who need premium private-room entertainment.",
            "channel_strategy": [
                {
                    "channel": "douyin",
                    "role": "primary",
                    "campaign_focus": "night booking conversion",
                    "message_positioning": "Show the room atmosphere, performer energy, and booking reason.",
                    "review_gate": "operation_plan_approval_required",
                    "publishing_boundary": "human-approved publish package required",
                }
            ],
            "content_strategy": {
                "core_positioning": "Premium KTV night-out booking",
                "creative_direction": "A virtual singer with microphone, standing posture, camera awareness, and short dance motion.",
                "narrative_arc": ["opening room reveal", "performer sings and gestures", "booking call to action"],
                "video_audio_direction": "Use a first frame plus reference performance rhythm before video generation.",
                "approval_boundary": "human approval before production",
                "runtime_boundary": "no runtime execution during planning",
            },
            "production_scope": [
                {
                    "task_type": "copy",
                    "channel": "douyin",
                    "title": "LLM copy task",
                    "brief": "Prepare hook, script, caption, and hashtags for review.",
                    "workflow_selection_required": False,
                    "assigned_agent": "text_content_agent",
                    "output_requirements": [{"output_type": "copy", "review_required": True}],
                },
                {
                    "task_type": "image",
                    "channel": "douyin",
                    "title": "LLM first frame task",
                    "brief": "Generate or edit the KTV scene first frame with a virtual singer and microphone.",
                    "workflow_selection_required": True,
                    "assigned_agent": "visual_asset_agent",
                    "output_requirements": [{"output_type": "image", "review_required": True}],
                },
                {
                    "task_type": "media",
                    "media_subtype": "audio_video",
                    "channel": "douyin",
                    "title": "LLM video and audio task",
                    "brief": "Use approved first frame and reference rhythm to create singing/dancing video output.",
                    "workflow_selection_required": True,
                    "assigned_agent": "video_content_agent",
                    "output_requirements": [{"output_type": "audio_video", "review_required": True}],
                },
            ],
            "material_requirements": [
                {"material_type": "scene_image", "required": True, "reason": "Needed for first-frame generation."},
                {"material_type": "reference_video", "required": True, "reason": "Needed for singing/dancing rhythm."},
            ],
            "kpis": [
                {"name": "booking_intent", "source": "operator_defined", "review_required": True},
            ],
            "publish_schedule": [
                {
                    "channel": "douyin",
                    "schedule_status": "draft",
                    "cadence": "operator_configured",
                    "approval_gate": "publish_package_approval_required",
                }
            ],
            "risk_notes": "Operator approval is required before ComfyUI, publishing, account control, or data pullback.",
        }
        return LLMResponse(
            provider="local",
            model="fake-operation-planner",
            content=json.dumps(payload),
            usage={"prompt_tokens": 100, "completion_tokens": 200},
        )


class EchoingOperationPlanLLMClient:
    def __init__(self, settings=None) -> None:  # type: ignore[no-untyped-def]
        self.settings = settings

    async def health_check(self) -> LLMHealthResponse:
        return LLMHealthResponse(provider="local", model="echoing-operation-planner", reachable=True)

    async def generate(self, request: LLMRequest) -> LLMResponse:
        echoed_context = request.user_prompt.split("INPUT_CONTEXT_JSON:", 1)[-1].strip()
        return LLMResponse(
            provider="local",
            model="echoing-operation-planner",
            content=echoed_context,
            usage={"prompt_tokens": 100, "completion_tokens": 100},
        )


@pytest.mark.asyncio
async def test_main_agent_advance_blocks_without_knowledge_source(session: AsyncSession) -> None:
    _ = (
        CommercialOperation,
        CommercialOperationApproval,
        CommercialOperationContentDraft,
    )
    service = CommercialOperationService(session)
    operation = await service.create_operation(
        workspace_id="workspace-main-agent-advance",
        user_id="operator",
        title="No source operation",
        objective="Create reviewed marketing content.",
        channels=["newsletter"],
    )

    response = await service.advance_main_agent_loop(
        workspace_id=operation.workspace_id,
        operation_id=operation.id,
        actor_user_id="operator",
    )

    assert response["advance_status"] == "created"
    assert response["advanced_track"] == "operation_strategy"
    assert response["created_records"][0]["kind"] == "operation_plan"
    await service.set_operation_plan_status(
        workspace_id=operation.workspace_id,
        operation_id=operation.id,
        plan_id=_record_id(response),
        status="approved",
        actor_user_id="operator",
        reviewer_notes="Plan approved.",
    )

    tasks = await service.advance_main_agent_loop(
        workspace_id=operation.workspace_id,
        operation_id=operation.id,
        actor_user_id="operator",
    )
    assert tasks["advance_status"] == "created"
    assert tasks["created_records"][0]["kind"] == "production_task"

    blocked = await service.advance_main_agent_loop(
        workspace_id=operation.workspace_id,
        operation_id=operation.id,
        actor_user_id="operator",
    )
    assert blocked["advance_status"] == "blocked"
    assert blocked["advanced_track"] == "knowledge_retrieval"
    assert blocked["blocked_by"] == ["knowledge_source_missing"]
    assert blocked["created_records"] == []
    TypeAdapter(CommercialOperationMainAgentAdvanceResponse).validate_python(blocked)


@pytest.mark.asyncio
async def test_main_agent_advance_route_creates_knowledge_gate(session: AsyncSession) -> None:
    _ = (
        CommercialOperation,
        CommercialOperationApproval,
        CommercialOperationContentDraft,
    )
    service = CommercialOperationService(session)
    operation = await service.create_operation(
        workspace_id="workspace-main-agent-route",
        user_id="operator",
        title="Route operation",
        objective="Create reviewed post content.",
        channels=["post"],
        knowledge_collection="ai_knowledge_base",
    )

    response = await advance_commercial_operation_main_agent_loop(
        operation_id=operation.id,
        request=CommercialOperationMainAgentAdvanceRequest(operator_note="route smoke"),
        session=session,
        context=WorkspaceContext(workspace_id=operation.workspace_id, user_id="operator"),
    )

    assert response.advance_status == "created"
    assert response.advanced_track == "operation_strategy"
    assert response.created_records[0]["kind"] == "operation_plan"
    await service.set_operation_plan_status(
        workspace_id=operation.workspace_id,
        operation_id=operation.id,
        plan_id=UUID(response.created_records[0]["id"]),
        status="approved",
        actor_user_id="operator",
        reviewer_notes="Plan approved.",
    )

    tasks = await service.advance_main_agent_loop(
        workspace_id=operation.workspace_id,
        operation_id=operation.id,
        actor_user_id="operator",
    )
    assert tasks["advance_status"] == "created"
    assert tasks["created_records"][0]["kind"] == "production_task"

    knowledge_gate = await advance_commercial_operation_main_agent_loop(
        operation_id=operation.id,
        request=CommercialOperationMainAgentAdvanceRequest(operator_note="route smoke"),
        session=session,
        context=WorkspaceContext(workspace_id=operation.workspace_id, user_id="operator"),
    )
    assert knowledge_gate.advance_status == "created"
    assert knowledge_gate.advanced_track == "knowledge_retrieval"
    assert knowledge_gate.created_records[0]["kind"] == "approval"


@pytest.mark.asyncio
async def test_main_agent_plan_first_goal_submit_forces_operation_strategy(
    session: AsyncSession,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _ = (
        CommercialOperation,
        CommercialOperationPlan,
    )
    service = CommercialOperationService(session)
    operation = await service.create_operation(
        workspace_id="workspace-main-agent-plan-first",
        user_id="operator",
        title="Existing project with intervention pressure",
        objective="Generate a business KTV operation plan.",
        channels=["douyin"],
        knowledge_collection="operations",
    )

    async def fake_agent_skill_orchestration(**kwargs):  # type: ignore[no-untyped-def]
        assert kwargs["operation_id"] == operation.id
        return {
            "routing_decision": {
                "recommended_track": "production_intervention",
                "selected_track_status": "recommended",
                "selected_skill_key": "knowledge_retrieval_skill",
                "blocked_by": [],
                "reason_codes": ["production_intervention:acknowledge_intervention_queue_item"],
                "next_executable_contract": {"execution_boundary": "metadata_only_review_required"},
            }
        }

    monkeypatch.setattr(service, "get_agent_skill_orchestration", fake_agent_skill_orchestration)

    response = await service.advance_main_agent_loop(
        workspace_id=operation.workspace_id,
        operation_id=operation.id,
        actor_user_id="operator",
        operator_note="plan-first submit",
        metadata={"plan_first_goal_submit": True},
    )

    assert response["advance_status"] == "created"
    assert response["advanced_track"] == "operation_strategy"
    assert response["created_records"][0]["kind"] == "operation_plan"
    assert response["routing_decision"]["plan_first_goal_submit_forced_operation_strategy"] is True
    assert response["routing_decision"]["original_recommended_track"] == "production_intervention"
    stored_plans = await service.list_operation_plans(workspace_id=operation.workspace_id, operation_id=operation.id)
    assert stored_plans[0].plan_status == "ready_for_review"


@pytest.mark.asyncio
async def test_main_agent_operation_plan_generation_uses_llm_structured_payload(
    session: AsyncSession,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _ = (
        CommercialOperation,
        CommercialOperationPlan,
    )
    FakeOperationPlanLLMClient.last_request = None
    monkeypatch.setattr(commercial_operation_service, "LLMClient", FakeOperationPlanLLMClient)
    service = CommercialOperationService(session)
    operation = await service.create_operation(
        workspace_id="workspace-main-agent-llm-plan",
        user_id="operator",
        title="Commercial KTV launch",
        objective="Generate a KTV operation plan with image, video, and copy outputs.",
        target_audience="Local premium KTV guests",
        channels=["douyin"],
        knowledge_collection="commercial_ktv_knowledge",
        success_metrics=["booking_intent"],
        constraints=["human approval required"],
    )

    response = await service.advance_main_agent_loop(
        workspace_id=operation.workspace_id,
        operation_id=operation.id,
        actor_user_id="operator",
        metadata={"plan_first_goal_submit": True},
    )

    assert response["advance_status"] == "created"
    assert response["advanced_track"] == "operation_strategy"
    stored_plans = await service.list_operation_plans(workspace_id=operation.workspace_id, operation_id=operation.id)
    stored_plan = stored_plans[0]
    assert stored_plan.title == "LLM plan: commercial KTV launch"
    assert stored_plan.objective_summary.startswith("LLM generated objective summary")
    assert stored_plan.content_strategy["creative_direction"].startswith("A virtual singer")
    assert {item["task_type"] for item in stored_plan.production_scope} == {"copy", "image", "media"}
    metadata = stored_plan.plan_metadata["main_agent_advance"]
    assert metadata["plan_generation_source"] == "llm"
    assert metadata["llm_generation_status"] == "parsed"
    assert metadata["llm_model"] == "fake-operation-planner"
    assert metadata["rag_context_status"] == "collection_name_only_no_retrieved_chunks"
    assert FakeOperationPlanLLMClient.last_request is not None
    assert "required_json_schema" in FakeOperationPlanLLMClient.last_request.user_prompt


@pytest.mark.asyncio
async def test_main_agent_operation_plan_generation_rejects_llm_prompt_echo(
    session: AsyncSession,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _ = (
        CommercialOperation,
        CommercialOperationPlan,
    )
    monkeypatch.setattr(commercial_operation_service, "LLMClient", EchoingOperationPlanLLMClient)
    service = CommercialOperationService(session)
    operation = await service.create_operation(
        workspace_id="workspace-main-agent-llm-echo",
        user_id="operator",
        title="Prompt echo operation",
        objective="Generate a KTV operation plan.",
        channels=["douyin"],
        knowledge_collection="commercial_ktv_knowledge",
    )

    response = await service.advance_main_agent_loop(
        workspace_id=operation.workspace_id,
        operation_id=operation.id,
        actor_user_id="operator",
        metadata={"plan_first_goal_submit": True},
    )

    assert response["advance_status"] == "created"
    stored_plan = (
        await service.list_operation_plans(workspace_id=operation.workspace_id, operation_id=operation.id)
    )[0]
    assert stored_plan.title == "Operation plan: Prompt echo operation"
    metadata = stored_plan.plan_metadata["main_agent_advance"]
    assert metadata["plan_generation_source"] == "fallback"
    assert metadata["llm_generation_status"] == "unparseable_json"
    assert metadata["llm_model"] == "echoing-operation-planner"


@pytest.mark.asyncio
async def test_main_agent_advance_derives_copy_image_media_tasks_from_approved_plan(
    session: AsyncSession,
) -> None:
    _ = (
        CommercialOperation,
        CommercialOperationPlan,
        CommercialOperationProductionTask,
    )
    service = CommercialOperationService(session)
    operation = await service.create_operation(
        workspace_id="workspace-main-agent-project-objects",
        user_id="operator",
        title="Douyin KTV digital human launch",
        objective="Create a Douyin KTV short video campaign with copy, cover image, music, and audio-video output.",
        target_audience="local KTV customers",
        channels=["douyin"],
        knowledge_collection="ai_knowledge_base",
        success_metrics=["views", "bookings"],
        constraints=["human approval required"],
    )

    plan = await service.advance_main_agent_loop(
        workspace_id=operation.workspace_id,
        operation_id=operation.id,
        actor_user_id="operator",
    )
    assert plan["advance_status"] == "created"
    assert plan["advanced_track"] == "operation_strategy"
    assert plan["created_records"][0]["kind"] == "operation_plan"
    plan_id = _record_id(plan)

    stored_plans = await service.list_operation_plans(workspace_id=operation.workspace_id, operation_id=operation.id)
    assert stored_plans[0].plan_status == "ready_for_review"
    assert {item["task_type"] for item in stored_plans[0].production_scope} == {"copy", "image", "media"}
    assert "运营目标：" in stored_plans[0].objective_summary
    assert "审批边界：" in stored_plans[0].objective_summary
    assert stored_plans[0].content_strategy["creative_direction"]
    assert stored_plans[0].content_strategy["narrative_arc"]
    assert any(item["material_type"] == "reference_video" for item in stored_plans[0].material_requirements)
    assert stored_plans[0].publish_schedule[0]["approval_gate"] == "publish_package_approval_required"

    await service.set_operation_plan_status(
        workspace_id=operation.workspace_id,
        operation_id=operation.id,
        plan_id=plan_id,
        status="approved",
        actor_user_id="operator",
        reviewer_notes="Plan approved.",
    )

    tasks = await service.advance_main_agent_loop(
        workspace_id=operation.workspace_id,
        operation_id=operation.id,
        actor_user_id="operator",
    )
    assert tasks["advance_status"] == "created"
    assert tasks["advanced_track"] == "operation_strategy"
    assert [record["kind"] for record in tasks["created_records"]] == [
        "production_task",
        "production_task",
        "production_task",
    ]

    stored_tasks = await service.list_production_tasks(workspace_id=operation.workspace_id, operation_id=operation.id)
    assert {task.task_type for task in stored_tasks} == {"copy", "image", "media"}
    media_task = next(task for task in stored_tasks if task.task_type == "media")
    assert media_task.media_subtype == "audio_video"
    assert {task.task_status for task in stored_tasks} == {"ready_for_review"}
    assert {task.operation_plan_id for task in stored_tasks} == {plan_id}
    TypeAdapter(CommercialOperationMainAgentAdvanceResponse).validate_python(tasks)


@pytest.mark.asyncio
async def test_main_agent_advance_forms_metadata_closed_loop(session: AsyncSession) -> None:
    _ = (
        CommercialOperation,
        CommercialOperationApproval,
        CommercialOperationAssetRequest,
        CommercialOperationContentDraft,
        CommercialOperationDeliverable,
        CommercialOperationEvidenceSnapshot,
        CommercialOperationExecutionRequest,
        CommercialOperationExecutionRun,
        CommercialOperationMonitoringObservation,
        CommercialOperationOptimizationDecision,
        CommercialOperationPlan,
        CommercialOperationProductionTask,
        CommercialOperationResult,
    )
    service = CommercialOperationService(session)
    operation = await service.create_operation(
        workspace_id="workspace-main-agent-advance",
        user_id="operator",
        title="Newsletter post operation",
        objective="Create a reviewed newsletter post, publish from the customer machine, and improve from results.",
        target_audience="local buyers",
        channels=["newsletter"],
        knowledge_collection="ai_knowledge_base",
        success_metrics=["qualified_leads"],
        constraints=["human approval required"],
    )

    dry_run = await service.advance_main_agent_loop(
        workspace_id=operation.workspace_id,
        operation_id=operation.id,
        actor_user_id="operator",
        dry_run=True,
    )
    assert dry_run["advance_status"] == "dry_run"
    assert dry_run["created_records"][0]["kind"] == "operation_plan"

    operation_plan = await service.advance_main_agent_loop(
        workspace_id=operation.workspace_id,
        operation_id=operation.id,
        actor_user_id="operator",
    )
    assert operation_plan["advance_status"] == "created"
    assert operation_plan["advanced_track"] == "operation_strategy"
    assert operation_plan["created_records"][0]["kind"] == "operation_plan"
    await service.set_operation_plan_status(
        workspace_id=operation.workspace_id,
        operation_id=operation.id,
        plan_id=_record_id(operation_plan),
        status="approved",
        actor_user_id="operator",
        reviewer_notes="Operation plan approved.",
    )

    production_tasks = await service.advance_main_agent_loop(
        workspace_id=operation.workspace_id,
        operation_id=operation.id,
        actor_user_id="operator",
    )
    assert production_tasks["advance_status"] == "created"
    assert production_tasks["advanced_track"] == "operation_strategy"
    assert all(record["kind"] == "production_task" for record in production_tasks["created_records"])
    for task in await service.list_production_tasks(workspace_id=operation.workspace_id, operation_id=operation.id):
        await service.set_production_task_status(
            workspace_id=operation.workspace_id,
            operation_id=operation.id,
            production_task_id=task.id,
            status="approved",
            actor_user_id="operator",
            reviewer_notes="Production task approved.",
        )

    knowledge_gate = await service.advance_main_agent_loop(
        workspace_id=operation.workspace_id,
        operation_id=operation.id,
        actor_user_id="operator",
    )
    assert knowledge_gate["advance_status"] == "created"
    assert knowledge_gate["advanced_track"] == "knowledge_retrieval"
    assert knowledge_gate["after_stage_key"] == "knowledge_context"
    assert knowledge_gate["operation_loop"]["loop_status"] == "review_required"
    await service.approve_approval(
        workspace_id=operation.workspace_id,
        operation_id=operation.id,
        approval_id=_record_id(knowledge_gate),
        reviewer_user_id="operator",
        reviewer_notes="Knowledge source coverage approved.",
    )

    content = await service.advance_main_agent_loop(
        workspace_id=operation.workspace_id,
        operation_id=operation.id,
        actor_user_id="operator",
    )
    assert content["advance_status"] == "created"
    assert content["advanced_track"] in {"content_strategy", "text_content"}
    assert content["created_records"][0]["kind"] == "content_draft"
    draft_id = _record_id(content)
    await service.approve_content_draft(
        workspace_id=operation.workspace_id,
        operation_id=operation.id,
        draft_id=draft_id,
        approved_by="operator",
        reviewer_notes="Draft approved for packaging.",
    )

    deliverable = await service.advance_main_agent_loop(
        workspace_id=operation.workspace_id,
        operation_id=operation.id,
        actor_user_id="operator",
    )
    assert deliverable["advance_status"] == "created"
    assert deliverable["created_records"][0]["kind"] == "deliverable"
    deliverable_id = _record_id(deliverable)
    await service.approve_deliverable(
        workspace_id=operation.workspace_id,
        operation_id=operation.id,
        deliverable_id=deliverable_id,
        approved_by="operator",
        reviewer_notes="Deliverable approved.",
    )
    await service.package_deliverable(
        workspace_id=operation.workspace_id,
        operation_id=operation.id,
        deliverable_id=deliverable_id,
        packaged_by="operator",
        result_summary="Packaged for execution request.",
    )

    execution_request = await service.advance_main_agent_loop(
        workspace_id=operation.workspace_id,
        operation_id=operation.id,
        actor_user_id="operator",
    )
    assert execution_request["advance_status"] == "created"
    assert execution_request["created_records"][0]["kind"] == "execution_request"
    execution_request_id = _record_id(execution_request)
    await service.approve_execution_request(
        workspace_id=operation.workspace_id,
        operation_id=operation.id,
        execution_request_id=execution_request_id,
        approved_by="operator",
        reviewer_notes="Execution request approved.",
    )
    await service.prepare_execution_request(
        workspace_id=operation.workspace_id,
        operation_id=operation.id,
        execution_request_id=execution_request_id,
        prepared_by="operator",
        result_summary="Prepared for queued metadata run.",
    )

    execution_run = await service.advance_main_agent_loop(
        workspace_id=operation.workspace_id,
        operation_id=operation.id,
        actor_user_id="operator",
    )
    assert execution_run["advance_status"] == "created"
    assert execution_run["created_records"][0]["kind"] == "execution_run"
    execution_run_id = _record_id(execution_run)
    await service.start_execution_run(
        workspace_id=operation.workspace_id,
        operation_id=operation.id,
        execution_run_id=execution_run_id,
        started_by="operator",
        operator_notes="Customer-machine run started.",
    )
    await service.succeed_execution_run(
        workspace_id=operation.workspace_id,
        operation_id=operation.id,
        execution_run_id=execution_run_id,
        completed_by="operator",
        result_summary="Published manually from customer machine.",
        result_payload={"platform": "newsletter", "published": True},
    )

    result = await service.advance_main_agent_loop(
        workspace_id=operation.workspace_id,
        operation_id=operation.id,
        actor_user_id="operator",
    )
    assert result["advance_status"] == "created"
    assert result["created_records"][0]["kind"] == "result"
    result_id = _record_id(result)
    await service.approve_result(
        workspace_id=operation.workspace_id,
        operation_id=operation.id,
        result_id=result_id,
        approved_by="operator",
        reviewer_notes="Result approved.",
    )

    observation = await service.advance_main_agent_loop(
        workspace_id=operation.workspace_id,
        operation_id=operation.id,
        actor_user_id="operator",
    )
    assert observation["advance_status"] == "created"
    assert observation["created_records"][0]["kind"] == "monitoring_observation"
    observation_id = _record_id(observation)
    await service.approve_monitoring_observation(
        workspace_id=operation.workspace_id,
        operation_id=operation.id,
        observation_id=observation_id,
        approved_by="operator",
        reviewer_notes="Observation approved.",
    )

    decision = await service.advance_main_agent_loop(
        workspace_id=operation.workspace_id,
        operation_id=operation.id,
        actor_user_id="operator",
    )
    assert decision["advance_status"] == "created"
    assert decision["created_records"][0]["kind"] == "optimization_decision"
    decision_id = _record_id(decision)
    await service.approve_optimization_decision(
        workspace_id=operation.workspace_id,
        operation_id=operation.id,
        decision_id=decision_id,
        approved_by="operator",
        reviewer_notes="Optimization approved.",
    )

    next_cycle = await service.advance_main_agent_loop(
        workspace_id=operation.workspace_id,
        operation_id=operation.id,
        actor_user_id="operator",
    )
    assert next_cycle["advance_status"] == "created"
    assert next_cycle["advanced_track"] == "next_cycle_content"
    assert next_cycle["created_records"][0]["kind"] == "operation_plan"
    assert {record["kind"] for record in next_cycle["created_records"]} >= {"operation_plan", "production_task"}
    next_cycle_plans = await service.list_operation_plans(
        workspace_id=operation.workspace_id,
        operation_id=operation.id,
    )
    generated_next_plan = next(
        plan
        for plan in next_cycle_plans
        if (plan.plan_metadata or {}).get("production_closed_loop_next_cycle", {}).get("source_decision_id")
        == str(decision_id)
    )
    assert generated_next_plan.plan_status == "ready_for_review"
    generated_next_tasks = [
        task
        for task in await service.list_production_tasks(
            workspace_id=operation.workspace_id,
            operation_id=operation.id,
        )
        if task.operation_plan_id == generated_next_plan.id
    ]
    assert generated_next_tasks
    assert {task.task_status for task in generated_next_tasks} == {"ready_for_review"}
    assert next_cycle["after_stage_key"] is None
    TypeAdapter(CommercialOperationMainAgentAdvanceResponse).validate_python(next_cycle)
