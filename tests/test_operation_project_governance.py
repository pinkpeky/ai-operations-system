"""Operation project governance API tests."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.api.router import create_api_router
from app.core.errors import AppError, app_error_handler
from app.db.base import Base
from app.db.postgres import get_session
from app.models import (
    CommercialOperation,
    CommercialOperationContentDraft,
    CommercialOperationDeliverable,
    CommercialOperationExecutionRequest,
    CommercialOperationExecutionRun,
    CommercialOperationFinalSelection,
    CommercialOperationMonitoringObservation,
    CommercialOperationOutputCandidate,
    CommercialOperationPlan,
    CommercialOperationPlatformMetricSnapshot,
    CommercialOperationProductionTask,
    CommercialOperationProjectMaterial,
    CommercialOperationPublishPackage,
    CommercialOperationOptimizationDecision,
    CommercialOperationResult,
    CommercialOperationWorkflowSelection,
    OutputArtifact,
)


@pytest.mark.asyncio
async def test_operation_project_governance_closed_loop_api() -> None:
    _ = (
        CommercialOperation,
        CommercialOperationPlan,
        CommercialOperationProjectMaterial,
        CommercialOperationProductionTask,
        CommercialOperationWorkflowSelection,
        CommercialOperationOutputCandidate,
        CommercialOperationFinalSelection,
        CommercialOperationPublishPackage,
        CommercialOperationPlatformMetricSnapshot,
        OutputArtifact,
    )
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    app = FastAPI()
    app.add_exception_handler(AppError, app_error_handler)
    app.include_router(create_api_router())

    async def override_get_session():  # type: ignore[no-untyped-def]
        async with session_factory() as db_session:
            yield db_session

    app.dependency_overrides[get_session] = override_get_session
    headers = {"X-Workspace-Id": "workspace-operation-project", "X-User-Id": "operator-1"}

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            created = await client.post(
                "/api/v1/commercial-operations",
                headers=headers,
                json={
                    "title": "KTV weekend launch",
                    "objective": "Generate one approved weekend social campaign.",
                    "channels": ["douyin"],
                    "success_metrics": ["views", "bookings"],
                },
            )
            assert created.status_code == 201
            operation_id = created.json()["id"]

            operation_plan = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/operation-plans",
                headers=headers,
                json={
                    "title": "Weekend launch plan",
                    "objective_summary": "Drive weekend KTV room bookings.",
                    "channel_strategy": [{"platform": "douyin", "cadence": "daily"}],
                    "content_strategy": {"tracks": ["copy", "image", "audio_video"]},
                    "production_scope": [
                        {"task_type": "copy", "count": 1},
                        {"task_type": "image", "count": 1},
                        {"task_type": "media", "media_subtype": "audio_video", "count": 1},
                    ],
                    "material_requirements": [{"material_type": "scene_image"}],
                    "kpis": [{"name": "views", "target": 5000}],
                    "publish_schedule": [{"platform": "douyin", "window": "20:00"}],
                },
            )
            assert operation_plan.status_code == 201
            plan_id = operation_plan.json()["id"]
            assert operation_plan.json()["plan_status"] == "draft"

            ready_plan = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/operation-plans/{plan_id}/ready",
                headers=headers,
                json={"reviewer_notes": "Ready for approval."},
            )
            assert ready_plan.status_code == 200
            assert ready_plan.json()["plan_status"] == "ready_for_review"

            approved_plan = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/operation-plans/{plan_id}/approve",
                headers=headers,
                json={"reviewer_notes": "Approved."},
            )
            assert approved_plan.status_code == 200
            assert approved_plan.json()["plan_status"] == "approved"
            assert approved_plan.json()["approved_by"] == "operator-1"

            derived_tasks = await client.get(
                f"/api/v1/commercial-operations/{operation_id}/production-tasks",
                headers=headers,
            )
            assert derived_tasks.status_code == 200
            derived_task_items = derived_tasks.json()["items"]
            assert len(derived_task_items) >= 3
            assert {item["task_type"] for item in derived_task_items} >= {"copy", "image", "media"}
            assert all(item["task_status"] == "ready_for_review" for item in derived_task_items)
            assert all(item["operation_plan_id"] == plan_id for item in derived_task_items)

            material = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/project-materials",
                headers=headers,
                json={
                    "material_type": "scene_image",
                    "name": "Main private room scene",
                    "source_uri": "D:/ai-operations-system/input/商k/场景/main-room.png",
                    "authorization_status": "authorized",
                    "tags": ["scene", "ktv"],
                },
            )
            assert material.status_code == 201
            material_id = material.json()["id"]

            approved_material = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/project-materials/{material_id}/approve",
                headers=headers,
                json={"reviewer_notes": "Authorized scene material."},
            )
            assert approved_material.status_code == 200
            assert approved_material.json()["material_status"] == "approved"
            assert approved_material.json()["reviewed_by"] == "operator-1"

            missing_media_subtype = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/production-tasks",
                headers=headers,
                json={
                    "operation_plan_id": plan_id,
                    "task_type": "media",
                    "channel": "douyin",
                    "title": "Invalid media task",
                },
            )
            assert missing_media_subtype.status_code == 400

            production_task = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/production-tasks",
                headers=headers,
                json={
                    "operation_plan_id": plan_id,
                    "task_type": "media",
                    "media_subtype": "audio_video",
                    "channel": "douyin",
                    "title": "Digital human music promo",
                    "brief": "Create a standing singer with microphone in the selected scene.",
                    "source_material_ids": [material_id],
                    "output_requirements": [{"format": "mp4", "aspect_ratio": "9:16"}],
                    "target_specs": {"duration_policy": "match_reference"},
                    "assigned_agent": "video_content_agent",
                },
            )
            assert production_task.status_code == 201
            task_id = production_task.json()["id"]
            assert production_task.json()["media_subtype"] == "audio_video"

            workflow_candidates = await client.get(
                f"/api/v1/commercial-operations/{operation_id}/production-tasks/{task_id}/workflow-candidates?limit=4",
                headers=headers,
            )
            assert workflow_candidates.status_code == 200
            workflow_candidate_body = workflow_candidates.json()
            assert workflow_candidate_body["operation_id"] == operation_id
            assert workflow_candidate_body["production_task_id"] == task_id
            assert workflow_candidate_body["required_capabilities"][:2] == ["image_to_video", "digital_human"]
            assert workflow_candidate_body["library_metadata"]["document_count"] >= len(workflow_candidate_body["items"])
            assert workflow_candidate_body["items"]
            first_workflow_candidate = workflow_candidate_body["items"][0]
            assert first_workflow_candidate["workflow_source"] == "comfyui_cu130_rag"
            assert first_workflow_candidate["workflow_name"]
            assert first_workflow_candidate["capabilities"]
            assert first_workflow_candidate["input_requirements"]
            assert first_workflow_candidate["expected_outputs"]
            assert first_workflow_candidate["metadata"]["selection_boundary"] == "operator_must_confirm_before_runtime_execution"

            started_task = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/production-tasks/{task_id}/start",
                headers=headers,
                json={"reviewer_notes": "Approved to start media production."},
            )
            assert started_task.status_code == 200
            assert started_task.json()["task_status"] == "in_progress"
            assert started_task.json()["started_at"] is not None

            workflow_selection = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/workflow-selections",
                headers=headers,
                json={
                    "production_task_id": task_id,
                    "workflow_source": "comfyui",
                    "workflow_name": "qwen-image-edit-first-frame-plus-wan-kj-i2v",
                    "workflow_kind": "first_frame_to_audio_video",
                    "output_type": "audio_video",
                    "candidate_summary": "Generate first frame, then animate with reference audio.",
                    "input_requirements": [{"name": "scene_image"}, {"name": "reference_audio"}],
                    "expected_outputs": [{"type": "video", "format": "mp4"}],
                    "recommendation_reason": "Requires human confirmation because workflow cost and runtime vary.",
                    "estimated_duration_seconds": 6000,
                    "estimated_vram_mb": 22000,
                    "validation_status": "operator_checked",
                },
            )
            assert workflow_selection.status_code == 201
            workflow_selection_id = workflow_selection.json()["id"]
            assert workflow_selection.json()["selection_status"] == "recommended"

            approved_workflow = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/workflow-selections/{workflow_selection_id}/approve",
                headers=headers,
                json={"reviewer_notes": "Use this workflow for the first production pass."},
            )
            assert approved_workflow.status_code == 200
            assert approved_workflow.json()["selection_status"] == "approved"

            output_prep_package = await client.get(
                f"/api/v1/commercial-operations/{operation_id}/production-tasks/{task_id}/output-prep-package",
                headers=headers,
            )
            assert output_prep_package.status_code == 200
            prep_body = output_prep_package.json()
            assert prep_body["operation_id"] == operation_id
            assert prep_body["production_task_id"] == task_id
            assert prep_body["readiness_status"] == "ready_for_candidate_registration"
            assert prep_body["blocking_reasons"] == []
            assert prep_body["approved_workflow_selection_id"] == workflow_selection_id
            assert prep_body["candidate_blueprint"]["workflow_name"] == "qwen-image-edit-first-frame-plus-wan-kj-i2v"
            assert prep_body["candidate_blueprint"]["mime_type"] == "video/mp4"
            assert "approved_workflow_selection" in {item["name"] for item in prep_body["required_inputs"]}
            assert prep_body["expected_outputs"]
            assert "operator_registers_real_output_or_reviewable_text" in prep_body["review_gates"]
            assert prep_body["output_storage_policy"]["browser_preview_requires_http_or_asset_url"] is True
            assert prep_body["metadata"]["selection_boundary"] == "operator_must_review_output_before_final_selection"

            output_candidate = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/output-candidates",
                headers=headers,
                json={
                    "production_task_id": task_id,
                    "workflow_selection_id": workflow_selection_id,
                    "candidate_type": "audio_video",
                    "title": "KTV promo candidate A",
                    "preview_uri": "D:/ai-operations-system/output/商k/视频生成/candidate-a.mp4",
                    "source_uri": "D:/ai-operations-system/output/商k/视频生成/candidate-a.mp4",
                    "mime_type": "video/mp4",
                    "duration_seconds": 18.5,
                    "generation_summary": "Standing digital human singing with microphone.",
                    "quality_checks": ["previewable", "contains_audio"],
                },
            )
            assert output_candidate.status_code == 201
            candidate_id = output_candidate.json()["id"]

            selected_candidate = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/output-candidates/{candidate_id}/select",
                headers=headers,
                json={"reviewer_notes": "Best movement and scene match."},
            )
            assert selected_candidate.status_code == 200
            assert selected_candidate.json()["candidate_status"] == "selected"
            assert selected_candidate.json()["selected_by"] == "operator-1"

            final_selection = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/final-selections",
                headers=headers,
                json={
                    "production_task_id": task_id,
                    "output_candidate_id": candidate_id,
                    "final_type": "audio_video",
                    "title": "Final KTV weekend video",
                    "selection_reason": "Selected after human preview.",
                    "platform_targets": ["douyin"],
                },
            )
            assert final_selection.status_code == 201
            final_selection_id = final_selection.json()["id"]

            approved_final = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/final-selections/{final_selection_id}/approve",
                headers=headers,
                json={"reviewer_notes": "Approved for publishing copy packaging."},
            )
            assert approved_final.status_code == 200
            assert approved_final.json()["selection_status"] == "approved"

            publish_prep_package = await client.get(
                f"/api/v1/commercial-operations/{operation_id}/final-selections/{final_selection_id}/publish-prep-package",
                headers=headers,
            )
            assert publish_prep_package.status_code == 200
            publish_prep_body = publish_prep_package.json()
            assert publish_prep_body["operation_id"] == operation_id
            assert publish_prep_body["final_selection_id"] == final_selection_id
            assert publish_prep_body["readiness_status"] == "ready_for_publish_package_registration"
            assert publish_prep_body["blocking_reasons"] == []
            assert publish_prep_body["selected_output_candidate"]["id"] == candidate_id
            assert publish_prep_body["package_blueprints"][0]["platform"] == "douyin"
            assert publish_prep_body["package_blueprints"][0]["publish_payload"]["output_candidate_id"] == candidate_id
            assert "operator_must_review_platform_copy" in publish_prep_body["review_gates"]
            assert publish_prep_body["platform_policy"]["douyin"]["requires_manual_account_confirmation"] is True
            assert publish_prep_body["metadata"]["selection_boundary"] == "operator_must_approve_publish_package_before_client_execution"

            publish_package = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/publish-packages",
                headers=headers,
                json={
                    "final_selection_id": final_selection_id,
                    "platform": "douyin",
                    "account_ref": "ktv-main-account",
                    "title": "周末订房福利",
                    "body": "今晚来唱，包厢氛围和活动都准备好了。",
                    "hashtags": ["商K", "周末唱歌"],
                    "cover_candidate_id": candidate_id,
                    "publish_payload": {"visibility": "public"},
                },
            )
            assert publish_package.status_code == 201
            package_id = publish_package.json()["id"]

            approved_package = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/publish-packages/{package_id}/approve",
                headers=headers,
                json={"reviewer_notes": "Approved for guarded customer-machine execution handoff."},
            )
            assert approved_package.status_code == 200
            assert approved_package.json()["package_status"] == "approved"

            execution_handoff = await client.get(
                f"/api/v1/commercial-operations/{operation_id}/publish-packages/{package_id}/client-execution-handoff",
                headers=headers,
            )
            assert execution_handoff.status_code == 200
            execution_handoff_body = execution_handoff.json()
            assert execution_handoff_body["operation_id"] == operation_id
            assert execution_handoff_body["publish_package_id"] == package_id
            assert execution_handoff_body["readiness_status"] == "ready_for_client_execution_handoff"
            assert execution_handoff_body["blocking_reasons"] == []
            assert execution_handoff_body["package_status"] == "approved"
            assert execution_handoff_body["platform"] == "douyin"
            assert execution_handoff_body["publish_package"]["id"] == package_id
            assert execution_handoff_body["final_selection"]["id"] == final_selection_id
            assert execution_handoff_body["selected_output_candidate"]["id"] == candidate_id
            assert execution_handoff_body["execution_status"] == {}
            assert execution_handoff_body["account_confirmation"]["required"] is True
            assert execution_handoff_body["account_confirmation"]["account_ref_present"] is True
            assert execution_handoff_body["dry_run_plan"]["required"] is True
            assert "openclaw_playwright_dry_run_evidence_required_before_real_publish" in execution_handoff_body["review_gates"]
            assert execution_handoff_body["metadata"]["execution_boundary"] == "handoff_only_no_openclaw_or_playwright_execution_on_server"

            prepared_package = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/publish-packages/{package_id}/prepare",
                headers=headers,
                json={"reviewer_notes": "Client execution handoff checked."},
            )
            assert prepared_package.status_code == 200
            assert prepared_package.json()["package_status"] == "prepared"

            unconfirmed_execution_status = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/publish-packages/{package_id}/execution-status",
                headers=headers,
                json={"execution_status": "queued", "operator_confirmed": False},
            )
            assert unconfirmed_execution_status.status_code == 400
            assert "operator_confirmed" in unconfirmed_execution_status.text

            queued_execution_status = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/publish-packages/{package_id}/execution-status",
                headers=headers,
                json={
                    "execution_status": "queued",
                    "operator_confirmed": True,
                    "customer_machine_id": "customer-machine-1",
                    "progress": 5,
                    "execution_log": [{"title": "publish_package_claimed", "status": "queued"}],
                    "metadata": {"test": "phase_69a_queued"},
                },
            )
            assert queued_execution_status.status_code == 200
            queued_status_body = queued_execution_status.json()
            assert queued_status_body["execution_status"] == "queued"
            assert queued_status_body["package_status"] == "prepared"
            assert queued_status_body["customer_machine_id"] == "customer-machine-1"
            assert queued_status_body["progress"] == 5
            assert queued_status_body["latest_attempt"]["source"] == "customer_machine_publish_execution_status"
            assert queued_status_body["latest_attempt"]["metadata"]["test"] == "phase_69a_queued"
            assert queued_status_body["execution_history"][0]["execution_status"] == "queued"
            assert queued_status_body["retry_policy"]["can_retry"] is False
            assert queued_status_body["retry_policy"]["status_update_required_before_result_capture"] is True
            assert queued_status_body["metadata"]["phase"] == "69A"
            assert queued_status_body["metadata"]["contract"] == "customer_machine_publish_execution_status"
            assert queued_status_body["metadata"]["server_does_not_control_real_accounts"] is True
            assert (
                queued_status_body["metadata"]["server_execution_boundary"]
                == "status tracking only; customer-machine performs platform actions after operator approval"
            )
            publish_attempt_id = queued_status_body["attempt_id"]

            running_execution_status = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/publish-packages/{package_id}/execution-status",
                headers=headers,
                json={
                    "execution_status": "running",
                    "operator_confirmed": True,
                    "customer_machine_id": "customer-machine-1",
                    "attempt_id": publish_attempt_id,
                    "progress": 55,
                    "execution_log": [{"title": "openclaw_playwright_dry_run_started", "status": "running"}],
                    "metadata": {"test": "phase_69a_running"},
                },
            )
            assert running_execution_status.status_code == 200
            running_status_body = running_execution_status.json()
            assert running_status_body["attempt_id"] == publish_attempt_id
            assert running_status_body["execution_status"] == "running"
            assert running_status_body["progress"] == 55
            assert len(running_status_body["execution_history"]) == 2
            assert "capture_publish_execution_result_after_platform_submission" in running_status_body["next_actions"]

            needs_operator_status = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/publish-packages/{package_id}/execution-status",
                headers=headers,
                json={
                    "execution_status": "needs_operator",
                    "operator_confirmed": True,
                    "customer_machine_id": "customer-machine-1",
                    "attempt_id": publish_attempt_id,
                    "progress": 60,
                    "failure_reason": "Platform verification prompt requires operator confirmation.",
                    "retry_after_seconds": 300,
                    "evidence_links": [{"title": "Verification prompt", "url": "file:///evidence/verify.png"}],
                    "metadata": {"test": "phase_69a_needs_operator"},
                },
            )
            assert needs_operator_status.status_code == 200
            needs_operator_body = needs_operator_status.json()
            assert needs_operator_body["attempt_id"] == publish_attempt_id
            assert needs_operator_body["execution_status"] == "needs_operator"
            assert needs_operator_body["package_status"] == "prepared"
            assert needs_operator_body["failure_reason"] == "Platform verification prompt requires operator confirmation."
            assert len(needs_operator_body["execution_history"]) == 3
            assert needs_operator_body["retry_policy"]["can_retry"] is True
            assert needs_operator_body["retry_policy"]["requires_operator_intervention"] is True
            assert needs_operator_body["retry_policy"]["retry_after_seconds"] == 300
            assert "operator_reviews_platform_prompt_or_account_issue" in needs_operator_body["next_actions"]

            publish_status_readiness = await client.get(
                f"/api/v1/commercial-operations/{operation_id}/production-closed-loop/readiness?platform=douyin",
                headers=headers,
            )
            assert publish_status_readiness.status_code == 200
            publish_status_readiness_body = publish_status_readiness.json()
            assert publish_status_readiness_body["metadata"]["phase"] == "69C"
            assert publish_status_readiness_body["readiness_status"] == "ready_for_customer_machine_execution"
            assert publish_status_readiness_body["current_stage_key"] == "client_execution_result"
            assert publish_status_readiness_body["counts"]["publish_execution_statuses"] == 1
            assert publish_status_readiness_body["latest_records"]["publish_execution_status"]["execution_status"] == "needs_operator"
            assert (
                publish_status_readiness_body["metadata"]["latest_publish_execution_status"]
                == "needs_operator"
            )
            assert (
                "publish_execution_status_tracks_customer_machine_progress_before_result_capture"
                in publish_status_readiness_body["acceptance_gates"]
            )
            publish_status_stage_by_key = {
                stage["stage_key"]: stage for stage in publish_status_readiness_body["stages"]
            }
            assert publish_status_stage_by_key["publish_package"]["status"] == "complete"
            assert publish_status_stage_by_key["client_execution_result"]["status"] == "blocked"
            assert (
                "customer_machine_publish_execution_needs_operator"
                in publish_status_stage_by_key["client_execution_result"]["blocking_reasons"]
            )

            publish_status_next_action = await client.get(
                f"/api/v1/commercial-operations/{operation_id}/production-closed-loop/next-action?platform=douyin",
                headers=headers,
            )
            assert publish_status_next_action.status_code == 200
            publish_status_next_action_body = publish_status_next_action.json()
            assert publish_status_next_action_body["current_stage_key"] == "client_execution_result"
            assert publish_status_next_action_body["selected_action_key"] == "update_customer_machine_publish_execution_status"
            assert publish_status_next_action_body["selected_action"]["endpoint"].endswith(
                f"/publish-packages/{package_id}/execution-status"
            )
            assert publish_status_next_action_body["selected_action"]["expected_result"]["record_type"] == "PublishExecutionStatus"
            assert (
                publish_status_next_action_body["selected_action"]["boundary"]
                == "customer_machine_status_tracking_only_no_server_side_openclaw_or_playwright_execution"
            )

            publish_status_action_audit = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/production-closed-loop/next-action/audit-records?platform=douyin",
                headers=headers,
                json={
                    "action_key": publish_status_next_action_body["selected_action_key"],
                    "stage_key": publish_status_next_action_body["selected_action"]["stage_key"],
                    "action_status": "confirmed",
                    "operator_confirmed": True,
                    "target_method": publish_status_next_action_body["selected_action"]["method"],
                    "target_endpoint": publish_status_next_action_body["selected_action"]["endpoint"],
                    "submitted_payload": {
                        "execution_status": "running",
                        "operator_confirmed": True,
                        "customer_machine_id": "customer-machine-1",
                    },
                    "execution_summary": "Operator confirmed the customer-machine publish execution status update.",
                    "boundary_checks": ["no_server_side_external_execution", "customer_machine_status_only"],
                    "metadata": {"test": "phase_69e_publish_status_audit"},
                },
            )
            assert publish_status_action_audit.status_code == 201
            publish_status_action_audit_body = publish_status_action_audit.json()
            assert publish_status_action_audit_body["action_key"] == "update_customer_machine_publish_execution_status"
            assert (
                publish_status_action_audit_body["contract_snapshot"]["action"]["expected_result"]["record_type"]
                == "PublishExecutionStatus"
            )

            running_retry_execution_status = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/publish-packages/{package_id}/execution-status",
                headers=headers,
                json={
                    "execution_status": "running",
                    "operator_confirmed": True,
                    "customer_machine_id": "customer-machine-1",
                    "attempt_id": publish_attempt_id,
                    "progress": 72,
                    "evidence_links": [{"title": "Retry after operator confirmation", "url": "file:///evidence/retry.png"}],
                    "metadata": {"test": "phase_69e_running_retry"},
                },
            )
            assert running_retry_execution_status.status_code == 200
            assert running_retry_execution_status.json()["execution_status"] == "running"

            publish_status_result_binding = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/production-closed-loop/next-action/audit-records/{publish_status_action_audit_body['audit_id']}/result-binding",
                headers=headers,
                json={
                    "result_record_type": "PublishExecutionStatus",
                    "result_record_id": package_id,
                    "result_status": "running",
                    "result_endpoint": publish_status_next_action_body["selected_action"]["endpoint"],
                    "evidence_links": [{"title": "Execution status API response", "url": "file:///evidence/status-running.json"}],
                    "operator_confirmed": True,
                    "binding_notes": "Bind metadata-backed publish execution status to the action audit.",
                    "metadata": {"test": "phase_69e_publish_status_binding"},
                },
            )
            assert publish_status_result_binding.status_code == 201
            publish_status_result_binding_body = publish_status_result_binding.json()
            assert publish_status_result_binding_body["result_record_type"] == "PublishExecutionStatus"
            assert publish_status_result_binding_body["result_record_id"] == package_id
            assert publish_status_result_binding_body["metadata"]["contract"] == "production_closed_loop_action_result_binding"

            publish_status_record_validation = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/production-closed-loop/next-action/audit-records/{publish_status_action_audit_body['audit_id']}/result-binding/record-validation",
                headers=headers,
                json={
                    "operator_confirmed": True,
                    "validation_notes": "Validate metadata-backed PublishExecutionStatus before readiness refresh.",
                    "metadata": {"test": "phase_69e_publish_status_record_validation"},
                },
            )
            assert publish_status_record_validation.status_code == 200
            publish_status_record_validation_body = publish_status_record_validation.json()
            assert publish_status_record_validation_body["validation_status"] == "record_verified"
            assert publish_status_record_validation_body["result_record_type"] == "PublishExecutionStatus"
            assert publish_status_record_validation_body["record_status"] == "running"
            assert publish_status_record_validation_body["status_field"] == "execution_status"
            assert "PublishExecutionStatus" in publish_status_record_validation_body["supported_record_types"]
            assert (
                publish_status_record_validation_body["record_summary"]["metadata_record"]["execution_status"]
                == "running"
            )
            assert (
                publish_status_record_validation_body["metadata"]["contract"]
                == "production_closed_loop_action_result_record_validation"
            )

            succeeded_execution_status = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/publish-packages/{package_id}/execution-status",
                headers=headers,
                json={
                    "execution_status": "succeeded",
                    "operator_confirmed": True,
                    "customer_machine_id": "customer-machine-1",
                    "attempt_id": publish_attempt_id,
                    "progress": 95,
                    "evidence_links": [{"title": "Submitted page", "url": "file:///evidence/submitted.png"}],
                    "metadata": {"test": "phase_69c_succeeded"},
                },
            )
            assert succeeded_execution_status.status_code == 200
            assert succeeded_execution_status.json()["execution_status"] == "succeeded"
            assert (
                succeeded_execution_status.json()["metadata"]["client_publish_execution_dry_run_gate"][
                    "dry_run_verified"
                ]
                is False
            )

            dry_run_blocked_readiness = await client.get(
                f"/api/v1/commercial-operations/{operation_id}/production-closed-loop/readiness?platform=douyin",
                headers=headers,
            )
            assert dry_run_blocked_readiness.status_code == 200
            dry_run_blocked_readiness_body = dry_run_blocked_readiness.json()
            assert (
                dry_run_blocked_readiness_body["latest_records"]["publish_execution_dry_run_gate"][
                    "gate_status"
                ]
                == "dry_run_required"
            )
            dry_run_blocked_stage_by_key = {
                stage["stage_key"]: stage for stage in dry_run_blocked_readiness_body["stages"]
            }
            assert (
                "client_publish_openclaw_dry_run_required_before_result_capture"
                in dry_run_blocked_stage_by_key["client_execution_result"]["blocking_reasons"]
            )

            dry_run_required_next_action = await client.get(
                f"/api/v1/commercial-operations/{operation_id}/production-closed-loop/next-action?platform=douyin",
                headers=headers,
            )
            assert dry_run_required_next_action.status_code == 200
            dry_run_required_next_action_body = dry_run_required_next_action.json()
            assert (
                dry_run_required_next_action_body["selected_action_key"]
                == "record_client_publish_openclaw_dry_run_bridge_status"
            )
            assert dry_run_required_next_action_body["selected_action"]["endpoint"].endswith(
                f"/publish-packages/{package_id}/execution-status"
            )
            assert (
                dry_run_required_next_action_body["selected_action"]["payload_template"]["metadata"]["contract"]
                == "client_publish_execution_dry_run_bridge"
            )
            assert (
                "client_publish_openclaw_dry_run_required_before_result_capture"
                in dry_run_required_next_action_body["selected_action"]["blocking_reasons"]
            )

            blocked_publish_execution_result = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/publish-packages/{package_id}/execution-result",
                headers=headers,
                json={
                    "publish_succeeded": True,
                    "platform_content_id": "douyin-video-1",
                    "published_url": "https://www.douyin.com/video/douyin-video-1",
                    "execution_summary": "Customer machine attempted to submit success without 70H dry-run evidence.",
                    "evidence_links": [{"title": "Publish screenshot", "url": "file:///evidence/publish.png"}],
                    "dry_run_evidence": [{"title": "Dry-run screenshot", "url": "file:///evidence/dry-run.png"}],
                    "execution_log": [{"title": "publish_completed_on_customer_machine", "status": "succeeded"}],
                    "observed_metrics": {"views": 120, "likes": 8},
                    "metric_snapshot_summary": "Initial metrics reported by customer machine.",
                },
            )
            assert blocked_publish_execution_result.status_code == 400
            assert (
                "client_publish_openclaw_dry_run_required_before_result_capture"
                in blocked_publish_execution_result.text
            )

            dry_run_bridge_status = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/publish-packages/{package_id}/execution-status",
                headers=headers,
                json={
                    "execution_status": "running",
                    "operator_confirmed": True,
                    "customer_machine_id": "customer-machine-1",
                    "attempt_id": publish_attempt_id,
                    "progress": 35,
                    "evidence_links": [{"title": "OpenClaw dry-run", "url": "file:///evidence/openclaw-dry-run.png"}],
                    "execution_log": [
                        {
                            "title": "Phase 70H Client Publish OpenClaw Dry-Run Bridge",
                            "status": "succeeded",
                            "provider": "mock",
                        }
                    ],
                    "metadata": {
                        "phase": "70H",
                        "contract": "client_publish_execution_dry_run_bridge",
                        "no_real_publish": True,
                    },
                },
            )
            assert dry_run_bridge_status.status_code == 200
            dry_run_bridge_status_body = dry_run_bridge_status.json()
            assert dry_run_bridge_status_body["execution_status"] == "running"
            assert (
                dry_run_bridge_status_body["metadata"]["client_publish_execution_dry_run_gate"]["gate_status"]
                == "dry_run_verified"
            )
            assert (
                dry_run_bridge_status_body["metadata"]["dry_run_gate_contract"]
                == "client_publish_execution_dry_run_result_gate"
            )

            succeeded_after_dry_run_status = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/publish-packages/{package_id}/execution-status",
                headers=headers,
                json={
                    "execution_status": "succeeded",
                    "operator_confirmed": True,
                    "customer_machine_id": "customer-machine-1",
                    "attempt_id": publish_attempt_id,
                    "progress": 95,
                    "evidence_links": [{"title": "Submitted page", "url": "file:///evidence/submitted.png"}],
                    "metadata": {"test": "phase_70i_succeeded_after_dry_run"},
                },
            )
            assert succeeded_after_dry_run_status.status_code == 200
            assert (
                succeeded_after_dry_run_status.json()["metadata"]["client_publish_execution_dry_run_gate"][
                    "dry_run_verified"
                ]
                is True
            )
            assert (
                succeeded_after_dry_run_status.json()["metadata"]["client_publish_execution_submit_gate"][
                    "submit_verified"
                ]
                is False
            )

            submit_required_next_action = await client.get(
                f"/api/v1/commercial-operations/{operation_id}/production-closed-loop/next-action?platform=douyin",
                headers=headers,
            )
            assert submit_required_next_action.status_code == 200
            submit_required_next_action_body = submit_required_next_action.json()
            assert (
                submit_required_next_action_body["selected_action_key"]
                == "record_client_publish_submit_bridge_status"
            )
            assert submit_required_next_action_body["selected_action"]["endpoint"].endswith(
                f"/publish-packages/{package_id}/execution-status"
            )
            assert (
                submit_required_next_action_body["selected_action"]["payload_template"]["metadata"]["contract"]
                == "client_publish_execution_submit_bridge"
            )
            assert (
                "client_publish_submit_evidence_required_before_result_capture"
                in submit_required_next_action_body["selected_action"]["blocking_reasons"]
            )

            blocked_submit_gate_result = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/publish-packages/{package_id}/execution-result",
                headers=headers,
                json={
                    "publish_succeeded": True,
                    "platform_content_id": "douyin-video-1",
                    "published_url": "https://www.douyin.com/video/douyin-video-1",
                    "execution_summary": "Customer machine attempted to submit success without 70J submit evidence.",
                    "evidence_links": [{"title": "Publish screenshot", "url": "file:///evidence/publish.png"}],
                    "dry_run_evidence": [{"title": "Dry-run screenshot", "url": "file:///evidence/dry-run.png"}],
                    "execution_log": [{"title": "publish_completed_on_customer_machine", "status": "succeeded"}],
                    "observed_metrics": {"views": 120, "likes": 8},
                    "metric_snapshot_summary": "Initial metrics reported by customer machine.",
                },
            )
            assert blocked_submit_gate_result.status_code == 400
            assert "client_publish_submit_evidence_required_before_result_capture" in blocked_submit_gate_result.text

            submit_bridge_status = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/publish-packages/{package_id}/execution-status",
                headers=headers,
                json={
                    "execution_status": "succeeded",
                    "operator_confirmed": True,
                    "customer_machine_id": "customer-machine-1",
                    "attempt_id": publish_attempt_id,
                    "progress": 95,
                    "evidence_links": [{"title": "Real submit evidence", "url": "file:///evidence/real-submit.png"}],
                    "execution_log": [
                        {
                            "title": "Phase 70J Client Publish Submit Bridge",
                            "status": "succeeded",
                            "provider": "real-openclaw",
                            "mock": False,
                            "actual_publish_performed": True,
                            "operator_final_submit_confirmed": True,
                        }
                    ],
                    "metadata": {
                        "phase": "70J",
                        "contract": "client_publish_execution_submit_bridge",
                        "actual_publish_performed": True,
                        "operator_final_submit_confirmed": True,
                        "local_openclaw_provider": "real-openclaw",
                        "local_openclaw_mock": False,
                    },
                },
            )
            assert submit_bridge_status.status_code == 200
            submit_bridge_status_body = submit_bridge_status.json()
            assert submit_bridge_status_body["execution_status"] == "succeeded"
            assert (
                submit_bridge_status_body["metadata"]["client_publish_execution_submit_gate"]["gate_status"]
                == "submit_verified"
            )
            assert (
                submit_bridge_status_body["metadata"]["submit_gate_contract"]
                == "client_publish_execution_submit_result_gate"
            )

            publish_result_next_action = await client.get(
                f"/api/v1/commercial-operations/{operation_id}/production-closed-loop/next-action?platform=douyin",
                headers=headers,
            )
            assert publish_result_next_action.status_code == 200
            publish_result_next_action_body = publish_result_next_action.json()
            assert publish_result_next_action_body["selected_action_key"] == "submit_customer_machine_execution_result"
            assert publish_result_next_action_body["selected_action"]["endpoint"].endswith(
                f"/publish-packages/{package_id}/execution-result"
            )

            publish_execution_result = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/publish-packages/{package_id}/execution-result",
                headers=headers,
                json={
                    "publish_succeeded": True,
                    "platform_content_id": "douyin-video-1",
                    "published_url": "https://www.douyin.com/video/douyin-video-1",
                    "execution_summary": "Customer machine completed guarded publishing with operator evidence.",
                    "evidence_links": [{"title": "Publish screenshot", "url": "file:///evidence/publish.png"}],
                    "dry_run_evidence": [{"title": "Dry-run screenshot", "url": "file:///evidence/dry-run.png"}],
                    "execution_log": [{"title": "publish_completed_on_customer_machine", "status": "succeeded"}],
                    "observed_metrics": {"views": 120, "likes": 8},
                    "metric_snapshot_summary": "Initial metrics reported by customer machine.",
                },
            )
            assert publish_execution_result.status_code == 201
            publish_execution_result_body = publish_execution_result.json()
            assert publish_execution_result_body["result_status"] == "captured_success"
            assert publish_execution_result_body["publish_succeeded"] is True
            assert publish_execution_result_body["platform_content_id"] == "douyin-video-1"
            assert publish_execution_result_body["publish_package"]["package_status"] == "published"
            assert publish_execution_result_body["publish_package"]["published_at"] is not None
            assert publish_execution_result_body["created_metric_snapshot"]["snapshot_status"] == "collected"
            assert publish_execution_result_body["created_metric_snapshot"]["metrics"]["views"] == 120
            initial_snapshot_id = publish_execution_result_body["created_metric_snapshot"]["id"]
            assert publish_execution_result_body["execution_result"]["server_side_external_execution"] is False
            assert (
                publish_execution_result_body["execution_result"]["client_publish_execution_dry_run_gate"][
                    "dry_run_verified"
                ]
                is True
            )
            assert (
                publish_execution_result_body["execution_result"]["client_publish_execution_submit_gate"][
                    "submit_verified"
                ]
                is True
            )
            assert (
                "client_publish_openclaw_dry_run_verified_before_result_capture"
                in publish_execution_result_body["review_gates"]
            )
            assert (
                "client_publish_submit_evidence_verified_before_result_capture"
                in publish_execution_result_body["review_gates"]
            )
            assert (
                publish_execution_result_body["metadata"]["dry_run_gate_contract"]
                == "client_publish_execution_dry_run_result_gate"
            )
            assert (
                publish_execution_result_body["metadata"]["submit_gate_contract"]
                == "client_publish_execution_submit_result_gate"
            )
            assert publish_execution_result_body["metadata"]["result_boundary"] == "operator_reported_evidence_not_server_side_publish"

            metric_snapshot = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/platform-metric-snapshots",
                headers=headers,
                json={
                    "publish_package_id": package_id,
                    "platform": "douyin",
                    "platform_content_id": "douyin-video-1",
                    "source_type": "connector",
                    "metrics": {"views": 6800, "likes": 320, "comments": 18},
                    "summary": "First-day performance exceeds baseline.",
                },
            )
            assert metric_snapshot.status_code == 201
            snapshot_id = metric_snapshot.json()["id"]
            assert metric_snapshot.json()["snapshot_status"] == "collected"

            approved_snapshot = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/platform-metric-snapshots/{snapshot_id}/approve",
                headers=headers,
                json={"reviewer_notes": "Approved for closed-loop analysis."},
            )
            assert approved_snapshot.status_code == 200
            assert approved_snapshot.json()["snapshot_status"] == "approved"

            metric_analysis_schedule = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/metric-analysis-schedule",
                headers=headers,
                json={
                    "enabled": True,
                    "local_time": "21:30",
                    "timezone": "UTC",
                    "lookback_hours": 24,
                    "platform_scope": ["douyin"],
                    "metric_requirements": ["views", "likes", "comments"],
                },
            )
            assert metric_analysis_schedule.status_code == 200
            schedule_body = metric_analysis_schedule.json()
            assert schedule_body["schedule_status"] == "scheduled"
            assert schedule_body["enabled"] is True
            assert schedule_body["local_time"] == "21:30"
            assert schedule_body["timezone"] == "UTC"
            assert schedule_body["published_package_count"] == 1
            assert schedule_body["latest_metric_snapshot"]["id"] in {snapshot_id, initial_snapshot_id}
            assert schedule_body["analysis_contract"]["scheduler_should_poll"] is True
            assert schedule_body["analysis_contract"]["time_basis"] == "operator_configured_local_time_with_utc_next_run_at"
            assert "operator_can_configure_daily_analysis_time_per_project" in schedule_body["review_gates"]

            read_metric_analysis_schedule = await client.get(
                f"/api/v1/commercial-operations/{operation_id}/metric-analysis-schedule",
                headers=headers,
            )
            assert read_metric_analysis_schedule.status_code == 200
            assert read_metric_analysis_schedule.json()["local_time"] == "21:30"

            metric_pullback_handoff = await client.get(
                f"/api/v1/commercial-operations/{operation_id}/metric-analysis-schedule/pullback-handoff?force=true",
                headers=headers,
            )
            assert metric_pullback_handoff.status_code == 200
            pullback_body = metric_pullback_handoff.json()
            assert pullback_body["handoff_status"] == "ready_for_customer_machine_metric_pullback"
            assert pullback_body["forced"] is True
            assert pullback_body["published_packages"][0]["id"] == package_id
            assert pullback_body["pullback_tasks"][0]["publish_package_id"] == package_id
            assert pullback_body["pullback_tasks"][0]["platform_content_id"] == "douyin-video-1"
            assert pullback_body["target_metric_keys"] == ["views", "likes", "comments"]
            assert pullback_body["analysis_run_request_template"]["collected_metrics"][0]["source_type"] == "customer_machine_metric_pullback"
            assert pullback_body["client_adapter_plan"]["submission_endpoint"].endswith("/metric-analysis-schedule/run")
            assert pullback_body["metadata"]["contract"] == "customer_machine_metric_pullback_handoff"
            assert "metric_values_must_be_returned_with_evidence_links" in pullback_body["review_gates"]

            metric_adapter_profile = await client.get(
                f"/api/v1/commercial-operations/{operation_id}/metric-analysis-schedule/pullback-handoff/adapter-profile?platform=douyin&force=true",
                headers=headers,
            )
            assert metric_adapter_profile.status_code == 200
            profile_body = metric_adapter_profile.json()
            assert profile_body["profile_status"] == "ready_for_customer_machine_adapter"
            assert profile_body["adapter_profile_id"] == "douyin_metric_pullback_v1"
            assert profile_body["handoff"]["handoff_status"] == "ready_for_customer_machine_metric_pullback"
            assert "播放量" in profile_body["field_aliases"]["views"]
            assert "browser_assist_must_not_collect_credentials_or_bypass_verification" in profile_body["review_gates"]
            assert profile_body["browser_assist_plan"]["requires_human_confirmation_before_navigation"] is True
            assert profile_body["export_import_contract"]["parser_status"] == "customer_machine_preview_parser_enabled"
            assert profile_body["export_import_contract"]["parser_endpoint"] == "adapter-profile/parse-export"
            assert profile_body["submission_template"]["payload"]["adapter_mode"] == "douyin_customer_machine_profile_v1"
            assert profile_body["metadata"]["contract"] == "douyin_customer_machine_metric_adapter_profile"

            metric_export_preview = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/metric-analysis-schedule/pullback-handoff/adapter-profile/parse-export",
                headers=headers,
                json={
                    "platform": "douyin",
                    "force": True,
                    "export_format": "csv",
                    "raw_text": f"publish_package_id,platform_content_id,播放量,点赞,评论\n{package_id},douyin-video-1,7300,380,24\n",
                    "evidence_links": [{"title": "analytics export", "url": "file:///evidence/analytics-68o.csv"}],
                    "operator_confirmed": True,
                    "metadata": {"adapter_run_id": "client-metric-run-1"},
                },
            )
            assert metric_export_preview.status_code == 200
            metric_export_preview_body = metric_export_preview.json()
            assert metric_export_preview_body["preview_status"] == "ready_for_68m_submission"
            assert metric_export_preview_body["accepted_metric_count"] == 1
            assert metric_export_preview_body["accepted_metrics"][0]["metrics"]["views"] == 7300
            assert metric_export_preview_body["accepted_metrics"][0]["metrics"]["likes"] == 380
            assert metric_export_preview_body["submission_payload"]["adapter_mode"] == "douyin_customer_machine_export_import_v1"
            assert metric_export_preview_body["metadata"]["contract"] == "customer_machine_metric_export_import_parser"
            assert "metric_columns_must_match_68n_field_aliases" in metric_export_preview_body["review_gates"]

            metric_browser_assist = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/metric-analysis-schedule/pullback-handoff/adapter-profile/browser-assist-session",
                headers=headers,
                json={
                    "platform": "douyin",
                    "force": True,
                    "operator_confirmed": True,
                    "open_target_url": True,
                    "metadata": {"browser_assist_session_id": "browser-assist-test-1"},
                },
            )
            assert metric_browser_assist.status_code == 200
            metric_browser_assist_body = metric_browser_assist.json()
            assert metric_browser_assist_body["session_status"] == "ready_for_customer_machine_browser_assist"
            assert metric_browser_assist_body["browser_assist_session_id"] == "browser-assist-test-1"
            assert metric_browser_assist_body["target_task_count"] == 1
            assert metric_browser_assist_body["navigation_targets"][0]["operator_must_confirm_account_before_reading"] is True
            assert "credential_collection" in metric_browser_assist_body["forbidden_actions"]
            assert "views" in [item["metric_key"] for item in metric_browser_assist_body["extraction_fields"]]
            assert metric_browser_assist_body["submission_template"]["payload"]["adapter_mode"] == "douyin_customer_machine_browser_assist_v1"
            assert metric_browser_assist_body["metadata"]["contract"] == "customer_machine_browser_assist_metric_pullback_session"

            metric_dispatch_queue = await client.get(
                "/api/v1/commercial-operations/metric-analysis-dispatch?platform=douyin&force=true&limit=10",
                headers=headers,
            )
            assert metric_dispatch_queue.status_code == 200
            metric_dispatch_body = metric_dispatch_queue.json()
            assert metric_dispatch_body["dispatch_status"] == "ready_for_customer_machine_dispatch"
            assert metric_dispatch_body["forced"] is True
            assert metric_dispatch_body["platform"] == "douyin"
            assert metric_dispatch_body["ready_dispatch_count"] >= 1
            assert metric_dispatch_body["metadata"]["contract"] == "metric_analysis_dispatch_queue"
            dispatch_item = next(item for item in metric_dispatch_body["items"] if item["operation_id"] == operation_id)
            assert dispatch_item["dispatch_status"] == "ready_for_customer_machine_dispatch"
            assert dispatch_item["handoff"]["handoff_status"] == "ready_for_customer_machine_metric_pullback"
            assert dispatch_item["pullback_task_count"] == 1
            assert "customer_machine_export_import_parser" in dispatch_item["available_collection_modes"]
            assert dispatch_item["customer_machine_actions"][2]["endpoint"].endswith("/adapter-profile/parse-export")
            assert dispatch_item["metadata"]["contract"] == "metric_analysis_dispatch_queue_item"
            assert "customer_machine_operator_confirms_account_before_collection" in dispatch_item["review_gates"]

            blocked_dispatch_claim = await client.post(
                "/api/v1/commercial-operations/metric-analysis-dispatch/claims",
                headers=headers,
                json={
                    "platform": "douyin",
                    "force": True,
                    "collection_mode": "customer_machine_export_import_parser",
                    "customer_machine_id": "client-machine-1",
                    "operator_confirmed": False,
                    "target_operation_id": operation_id,
                },
            )
            assert blocked_dispatch_claim.status_code == 200
            assert blocked_dispatch_claim.json()["claim_status"] == "blocked_operator_confirmation_required"

            dispatch_claim = await client.post(
                "/api/v1/commercial-operations/metric-analysis-dispatch/claims",
                headers=headers,
                json={
                    "platform": "douyin",
                    "force": True,
                    "collection_mode": "customer_machine_export_import_parser",
                    "customer_machine_id": "client-machine-1",
                    "operator_confirmed": True,
                    "lease_seconds": 900,
                    "target_operation_id": operation_id,
                    "metadata": {"claim_reason": "api test"},
                },
            )
            assert dispatch_claim.status_code == 200
            dispatch_claim_body = dispatch_claim.json()
            assert dispatch_claim_body["claim_status"] == "claimed"
            assert dispatch_claim_body["operation_id"] == operation_id
            assert dispatch_claim_body["collection_mode"] == "customer_machine_export_import_parser"
            assert dispatch_claim_body["claim_record"]["dispatch_item_snapshot"]["pullback_task_count"] == 1
            assert dispatch_claim_body["metadata"]["contract"] == "customer_machine_metric_dispatch_claim"
            assert "one_active_claim_per_dispatch_idempotency_key" in dispatch_claim_body["review_gates"]
            claim_id = dispatch_claim_body["claim_id"]

            dispatch_claims = await client.get(
                "/api/v1/commercial-operations/metric-analysis-dispatch/claims?limit=10",
                headers=headers,
            )
            assert dispatch_claims.status_code == 200
            dispatch_claims_body = dispatch_claims.json()
            assert dispatch_claims_body["active_count"] == 1
            assert dispatch_claims_body["items"][0]["claim_id"] == claim_id
            assert dispatch_claims_body["metadata"]["contract"] == "customer_machine_metric_dispatch_claim_list"

            running_dispatch_claim = await client.post(
                f"/api/v1/commercial-operations/metric-analysis-dispatch/claims/{claim_id}/status",
                headers=headers,
                json={
                    "claim_status": "running",
                    "progress": 45,
                    "operator_notes": "Customer machine opened the analytics page.",
                },
            )
            assert running_dispatch_claim.status_code == 200
            assert running_dispatch_claim.json()["claim_status"] == "running"
            assert running_dispatch_claim.json()["claim_record"]["progress"] == 45

            customer_machine_poll = await client.post(
                "/api/v1/commercial-operations/metric-analysis-dispatch/customer-poll",
                headers=headers,
                json={
                    "platform": "douyin",
                    "force": True,
                    "customer_machine_id": "client-machine-1",
                    "auto_claim": False,
                    "target_operation_id": operation_id,
                },
            )
            assert customer_machine_poll.status_code == 200
            customer_machine_poll_body = customer_machine_poll.json()
            assert customer_machine_poll_body["poll_status"] == "active_claim_in_progress"
            assert customer_machine_poll_body["assigned_claims"][0]["claim_id"] == claim_id
            assert customer_machine_poll_body["claim_list"]["active_count"] == 1
            assert customer_machine_poll_body["dispatch_queue"]["ready_dispatch_count"] >= 1
            assert customer_machine_poll_body["metadata"]["contract"] == "customer_machine_metric_dispatch_poller"
            assert "auto_claim_requires_operator_confirmation" in customer_machine_poll_body["review_gates"]

            customer_machine_poll_scheduler = await client.post(
                "/api/v1/commercial-operations/metric-analysis-dispatch/customer-poll/scheduler",
                headers=headers,
                json={
                    "platform": "douyin",
                    "force": True,
                    "customer_machine_id": "client-machine-1",
                    "scheduler_enabled": True,
                    "auto_claim": False,
                    "requested_poll_interval_seconds": 90,
                    "target_operation_id": operation_id,
                    "notification_channels": ["customer_console", "local_worker"],
                },
            )
            assert customer_machine_poll_scheduler.status_code == 200
            scheduler_body = customer_machine_poll_scheduler.json()
            assert scheduler_body["scheduler_status"] == "scheduler_active_claim_in_progress"
            assert scheduler_body["scheduler_enabled"] is True
            assert scheduler_body["recommended_poll_interval_seconds"] == 90
            assert scheduler_body["poll_result"]["poll_status"] == "active_claim_in_progress"
            assert scheduler_body["client_timer_payload"]["endpoint"].endswith("/customer-poll")
            assert scheduler_body["notification_events"][0]["event_type"] == "metric_dispatch_active_claim"
            assert scheduler_body["metadata"]["contract"] == "customer_machine_metric_dispatch_poll_scheduler"
            assert "customer_machine_owns_timer_and_notifications" in scheduler_body["review_gates"]

            metric_pullback_submission = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/metric-analysis-schedule/pullback-handoff/submit-result",
                headers=headers,
                json=metric_export_preview_body["submission_payload"],
            )
            assert metric_pullback_submission.status_code == 200
            pullback_submission_body = metric_pullback_submission.json()
            assert pullback_submission_body["submission_status"] == "submitted_to_analysis_runner"
            assert pullback_submission_body["adapter_run_id"] == "client-metric-run-1"
            assert pullback_submission_body["submitted_metric_count"] == 1
            assert pullback_submission_body["accepted_metric_count"] == 1
            assert pullback_submission_body["rejected_metric_count"] == 0
            assert pullback_submission_body["accepted_metrics"][0]["metrics"]["views"] == 7300
            assert pullback_submission_body["metric_analysis_run"]["run_status"] == "collected"
            assert pullback_submission_body["metric_analysis_run"]["created_metric_snapshots"][0]["metrics"]["likes"] == 380
            assert pullback_submission_body["metadata"]["contract"] == "customer_machine_metric_pullback_result_intake"
            assert "evidence_links_required_for_each_metric_submission" in pullback_submission_body["review_gates"]

            completed_dispatch_claim = await client.post(
                f"/api/v1/commercial-operations/metric-analysis-dispatch/claims/{claim_id}/status",
                headers=headers,
                json={
                    "claim_status": "completed",
                    "progress": 100,
                    "operator_notes": "68M accepted the metric export import payload.",
                    "metadata": {"metric_submission_status": pullback_submission_body["submission_status"]},
                },
            )
            assert completed_dispatch_claim.status_code == 200
            assert completed_dispatch_claim.json()["claim_status"] == "completed"
            assert completed_dispatch_claim.json()["claim_record"]["progress"] == 100
            assert completed_dispatch_claim.json()["metadata"]["contract"] == "customer_machine_metric_dispatch_claim_status"

            auto_customer_machine_poll = await client.post(
                "/api/v1/commercial-operations/metric-analysis-dispatch/customer-poll",
                headers=headers,
                json={
                    "platform": "douyin",
                    "force": True,
                    "collection_mode": "customer_machine_export_import_parser",
                    "customer_machine_id": "client-machine-2",
                    "auto_claim": True,
                    "operator_confirmed": True,
                    "target_operation_id": operation_id,
                    "metadata": {"poll_reason": "api auto claim test"},
                },
            )
            assert auto_customer_machine_poll.status_code == 200
            auto_poll_body = auto_customer_machine_poll.json()
            assert auto_poll_body["poll_status"] == "auto_claimed"
            assert auto_poll_body["auto_claimed"] is True
            assert auto_poll_body["claim_result"]["claim_status"] == "claimed"
            assert auto_poll_body["claim_result"]["customer_machine_id"] == "client-machine-2"
            assert auto_poll_body["redispatch_candidates"] == []
            assert auto_poll_body["metadata"]["contract"] == "customer_machine_metric_dispatch_poller"

            metric_analysis_run = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/metric-analysis-schedule/run",
                headers=headers,
                json={
                    "force": True,
                    "collected_metrics": [
                        {
                            "publish_package_id": package_id,
                            "platform": "douyin",
                            "platform_content_id": "douyin-video-1",
                            "source_type": "customer_machine_metric_pullback",
                            "metrics": {"views": 7200, "likes": 360, "comments": 22},
                            "summary": "Scheduled daily pullback from the customer machine.",
                            "evidence_links": [{"title": "analytics screenshot", "url": "file:///evidence/analytics.png"}],
                        }
                    ],
                    "operator_notes": "Force-run scheduled analysis in the API test.",
                },
            )
            assert metric_analysis_run.status_code == 200
            analysis_run_body = metric_analysis_run.json()
            assert analysis_run_body["run_status"] == "collected"
            assert analysis_run_body["forced"] is True
            assert analysis_run_body["created_metric_snapshots"][0]["snapshot_status"] == "collected"
            assert analysis_run_body["created_metric_snapshots"][0]["metrics"]["views"] == 7200
            assert analysis_run_body["analysis_package"]["analysis_ready"] is True
            assert analysis_run_body["analysis_package"]["requires_operator_approval_before_optimization"] is True
            assert analysis_run_body["metadata"]["contract"] == "scheduled_metric_analysis_runner"
            assert "platform_metrics_must_come_from_connector_or_customer_machine_evidence" in analysis_run_body["review_gates"]

            production_readiness = await client.get(
                f"/api/v1/commercial-operations/{operation_id}/production-closed-loop/readiness?platform=douyin&force_metric_due=true",
                headers=headers,
            )
            assert production_readiness.status_code == 200
            readiness_body = production_readiness.json()
            assert readiness_body["operation_id"] == operation_id
            assert readiness_body["workspace_id"] == "workspace-operation-project"
            assert readiness_body["metadata"]["contract"] == "production_closed_loop_e2e_readiness"
            assert readiness_body["readiness_status"] == "ready_for_metric_feedback"
            assert readiness_body["ready_for_customer_machine_execution"] is True
            assert readiness_body["ready_for_metric_feedback"] is True
            assert readiness_body["current_stage_key"] == "analysis_improvement"
            assert readiness_body["metric_schedule"]["enabled"] is True
            assert readiness_body["metric_dispatch"]["dispatch_status"] == "ready_for_customer_machine_dispatch"
            assert readiness_body["metric_claims"]["completed_count"] >= 1
            assert readiness_body["counts"]["publish_packages"] == 1
            assert readiness_body["counts"]["platform_metric_snapshots"] >= 3
            assert "publish_package_is_approved_before_customer_machine_execution" in readiness_body["acceptance_gates"]
            assert "does_not_run_openclaw_or_playwright_on_server" in readiness_body["boundaries"]
            stage_by_key = {stage["stage_key"]: stage for stage in readiness_body["stages"]}
            assert stage_by_key["plan_approval"]["status"] == "complete"
            assert stage_by_key["workflow_selection"]["status"] == "complete"
            assert stage_by_key["client_execution_result"]["status"] == "complete"
            assert stage_by_key["metric_feedback"]["status"] == "complete"
            assert stage_by_key["analysis_improvement"]["status"] == "blocked"

            production_acceptance_summary = await client.get(
                "/api/v1/commercial-operations/production-closed-loop/acceptance-summary?platform=douyin&force_metric_due=true",
                headers=headers,
            )
            assert production_acceptance_summary.status_code == 200
            acceptance_summary_body = production_acceptance_summary.json()
            assert acceptance_summary_body["workspace_id"] == "workspace-operation-project"
            assert acceptance_summary_body["metadata"]["contract"] == "production_closed_loop_acceptance_summary"
            assert acceptance_summary_body["metadata"]["source_readiness_contract"] == "production_closed_loop_e2e_readiness"
            assert acceptance_summary_body["metadata"]["server_side_external_execution"] is False
            assert acceptance_summary_body["operation_count"] >= 1
            assert acceptance_summary_body["accepted_count"] >= 1
            assert acceptance_summary_body["ready_for_customer_machine_execution_count"] >= 1
            assert acceptance_summary_body["ready_for_metric_feedback_count"] >= 1
            assert acceptance_summary_body["blocked_count"] >= 1
            assert acceptance_summary_body["completion_percent"] >= 60
            assert acceptance_summary_body["completion_level"] in {"operable", "production_ready", "closed_loop_ready"}
            assert acceptance_summary_body["metadata"]["completion_score_contract"] == "production_closed_loop_completion_score"
            assert (
                acceptance_summary_body["metadata"]["provider_readiness_contract"]
                == "server_acceptance_openclaw_provider_readiness_gate"
            )
            assert acceptance_summary_body["score_breakdown"]["operation_presence"] == 10
            assert acceptance_summary_body["score_breakdown"]["accepted_readiness"] >= 20
            assert acceptance_summary_body["score_breakdown"]["real_publish_provider_ready"] == 0
            assert acceptance_summary_body["openclaw_provider_readiness"]["ready"] is False
            assert (
                acceptance_summary_body["openclaw_provider_readiness"]["contract"]
                == "server_acceptance_openclaw_provider_readiness_gate"
            )
            assert acceptance_summary_body["release_ready"] is False
            assert acceptance_summary_body["release_gate_total_count"] == 6
            assert acceptance_summary_body["release_gate_ready_count"] < acceptance_summary_body["release_gate_total_count"]
            assert acceptance_summary_body["release_gate_status_counts"]["blocked"] >= 1
            release_gate_by_key = {
                gate["gate_key"]: gate for gate in acceptance_summary_body["release_gate_checklist"]
            }
            assert release_gate_by_key["operation_project_readiness"]["ready"] is False
            assert release_gate_by_key["customer_machine_execution_handoff"]["ready"] is True
            assert release_gate_by_key["real_openclaw_publish_provider"]["ready"] is False
            assert release_gate_by_key["customer_machine_publish_result_evidence"]["ready"] is True
            assert release_gate_by_key["metric_feedback_and_next_cycle"]["ready"] is False
            assert release_gate_by_key["intervention_queue_clear"]["ready"] in {True, False}
            assert "production_release_gate_checklist_is_machine_readable" in acceptance_summary_body["acceptance_gates"]
            assert "approve_analysis_and_next_cycle_decision" in acceptance_summary_body["remaining_gates"]
            assert "configure_real_openclaw_publish_provider" in acceptance_summary_body["remaining_gates"]
            assert acceptance_summary_body["next_focus"] in {
                "approve_analysis_and_next_cycle_decision",
                "clear_blocking_reasons",
            }
            assert acceptance_summary_body["readiness_status_counts"]["ready_for_metric_feedback"] >= 1
            assert acceptance_summary_body["current_stage_counts"]["analysis_improvement"] >= 1
            assert "production_closed_loop_e2e_readiness" in acceptance_summary_body["acceptance_gates"]
            assert "does_not_run_openclaw_or_playwright_on_server" in acceptance_summary_body["boundaries"]
            assert any(item["operation_id"] == operation_id for item in acceptance_summary_body["operations"])
            assert any(item["operation_id"] == operation_id for item in acceptance_summary_body["top_blockers"])

            production_delivery_plan = await client.get(
                "/api/v1/commercial-operations/production-closed-loop/delivery-plan?platform=douyin&force_metric_due=true",
                headers=headers,
            )
            assert production_delivery_plan.status_code == 200
            delivery_plan_body = production_delivery_plan.json()
            assert delivery_plan_body["workspace_id"] == "workspace-operation-project"
            assert delivery_plan_body["metadata"]["contract"] == "production_closed_loop_delivery_plan"
            assert delivery_plan_body["metadata"]["source_contract"] == "production_closed_loop_acceptance_summary"
            assert delivery_plan_body["metadata"]["server_side_external_execution"] is False
            assert delivery_plan_body["metadata"]["actual_publish_performed"] is False
            assert delivery_plan_body["completion_percent"] == acceptance_summary_body["completion_percent"]
            assert delivery_plan_body["acceptance_status"] == acceptance_summary_body["acceptance_status"]
            assert delivery_plan_body["open_gate_count"] >= 1
            assert delivery_plan_body["critical_gate_count"] >= 1
            assert delivery_plan_body["ready_for_handoff"] is False
            assert delivery_plan_body["delivery_status"] in {"blocked_by_critical_gate", "operator_action_required"}
            delivery_gate_by_key = {item["gate_key"]: item for item in delivery_plan_body["gate_plan"]}
            assert delivery_gate_by_key["configure_real_openclaw_publish_provider"]["gate_status"] == "critical"
            assert delivery_gate_by_key["configure_real_openclaw_publish_provider"]["owner"] == "technical_operator"
            assert "real_publish_provider_not_configured" in delivery_gate_by_key["configure_real_openclaw_publish_provider"]["blocking_reasons"]
            assert delivery_gate_by_key["approve_analysis_and_next_cycle_decision"]["gate_status"] in {"open", "critical"}
            assert operation_id in delivery_gate_by_key["approve_analysis_and_next_cycle_decision"]["related_operation_ids"]
            assert delivery_plan_body["immediate_actions"][0]["gate_key"] == delivery_plan_body["next_focus"]
            assert "production_closed_loop_acceptance_summary" in delivery_plan_body["acceptance_gates"]
            assert "does_not_run_openclaw_or_playwright_on_server" in delivery_plan_body["boundaries"]

            production_delivery_action_packages = await client.get(
                "/api/v1/commercial-operations/production-closed-loop/delivery-action-packages?platform=douyin&force_metric_due=true",
                headers=headers,
            )
            assert production_delivery_action_packages.status_code == 200
            delivery_action_package_body = production_delivery_action_packages.json()
            assert delivery_action_package_body["workspace_id"] == "workspace-operation-project"
            assert delivery_action_package_body["metadata"]["phase"] == "70W"
            assert (
                delivery_action_package_body["metadata"]["contract"]
                == "production_closed_loop_delivery_action_packages"
            )
            assert delivery_action_package_body["metadata"]["source_contract"] == "production_closed_loop_delivery_plan"
            assert delivery_action_package_body["metadata"]["server_side_external_execution"] is False
            assert delivery_action_package_body["metadata"]["actual_publish_performed"] is False
            assert delivery_action_package_body["delivery_status"] == delivery_plan_body["delivery_status"]
            assert delivery_action_package_body["completion_percent"] == delivery_plan_body["completion_percent"]
            assert delivery_action_package_body["package_count"] >= 1
            assert delivery_action_package_body["step_count"] >= 1
            assert delivery_action_package_body["immediate_action_packages"][0]["gate_key"] == delivery_plan_body["next_focus"]
            assert "delivery_action_packages_are_derived_from_gates" in delivery_action_package_body["acceptance_gates"]
            assert "delivery_action_packages_only_no_external_execution" in delivery_action_package_body["boundaries"]
            package_by_key = {item["gate_key"]: item for item in delivery_action_package_body["gate_packages"]}
            provider_package = package_by_key["configure_real_openclaw_publish_provider"]
            assert provider_package["target_console"] == "technical_operator_console"
            assert provider_package["external_execution_allowed"] is False
            assert provider_package["action_steps"][0]["endpoint"] == "/openclaw/provider-diagnostics"
            assert provider_package["action_steps"][0]["server_side_external_execution"] is False
            assert "operator_confirmation_required_before_mutation" in provider_package["action_steps"][0]["guardrails"]
            next_cycle_package = package_by_key["approve_analysis_and_next_cycle_decision"]
            assert operation_id in next_cycle_package["related_operation_ids"]
            assert next_cycle_package["action_steps"][0]["operation_id"] == operation_id
            assert next_cycle_package["action_steps"][0]["endpoint"].endswith(f"/{operation_id}/optimization-decisions")
            assert next_cycle_package["action_steps"][0]["payload_template"]["operator_confirmed"] is False

            delivery_action_evidence = await client.post(
                "/api/v1/commercial-operations/production-closed-loop/delivery-action-packages/evidence-records",
                headers=headers,
                json={
                    "gate_key": "configure_real_openclaw_publish_provider",
                    "action_key": provider_package["recommended_action_key"],
                    "evidence_status": "blocked",
                    "operator_confirmed": False,
                    "evidence_summary": "OpenClaw provider remains mock; real adapter configuration is pending.",
                    "operator_notes": "Recorded from the delivery action package panel.",
                    "metadata": {"source": "api_test_delivery_action_evidence"},
                },
            )
            assert delivery_action_evidence.status_code == 201
            delivery_action_evidence_body = delivery_action_evidence.json()
            assert delivery_action_evidence_body["workspace_id"] == "workspace-operation-project"
            assert delivery_action_evidence_body["operation_id"] == operation_id
            assert delivery_action_evidence_body["gate_key"] == "configure_real_openclaw_publish_provider"
            assert delivery_action_evidence_body["action_key"] == provider_package["recommended_action_key"]
            assert delivery_action_evidence_body["evidence_status"] == "blocked"
            assert delivery_action_evidence_body["target_console"] == "technical_operator_console"
            assert delivery_action_evidence_body["metadata"]["phase"] == "70X"
            assert delivery_action_evidence_body["metadata"]["contract"] == "production_closed_loop_delivery_action_evidence"
            assert delivery_action_evidence_body["metadata"]["source_contract"] == "production_closed_loop_delivery_action_packages"
            assert delivery_action_evidence_body["metadata"]["server_side_external_execution"] is False
            assert delivery_action_evidence_body["metadata"]["actual_publish_performed"] is False
            assert "delivery_action_package_contract_matched" in delivery_action_evidence_body["boundary_checks"]
            assert "does_not_execute_target_endpoint" in delivery_action_evidence_body["boundaries"]

            delivery_action_evidence_list = await client.get(
                "/api/v1/commercial-operations/production-closed-loop/delivery-action-packages/evidence-records?gate_key=configure_real_openclaw_publish_provider",
                headers=headers,
            )
            assert delivery_action_evidence_list.status_code == 200
            delivery_action_evidence_list_body = delivery_action_evidence_list.json()
            assert delivery_action_evidence_list_body["workspace_id"] == "workspace-operation-project"
            assert delivery_action_evidence_list_body["record_count"] == 1
            assert (
                delivery_action_evidence_list_body["latest_record"]["evidence_record_id"]
                == delivery_action_evidence_body["evidence_record_id"]
            )
            assert "delivery_action_evidence_is_operator_supplied" in delivery_action_evidence_list_body["acceptance_gates"]
            assert "delivery_action_evidence_only_no_external_execution" in delivery_action_evidence_list_body["boundaries"]

            delivery_remediation_map = await client.get(
                "/api/v1/commercial-operations/production-closed-loop/delivery-remediation-map?platform=douyin&force_metric_due=true",
                headers=headers,
            )
            assert delivery_remediation_map.status_code == 200
            delivery_remediation_map_body = delivery_remediation_map.json()
            assert delivery_remediation_map_body["workspace_id"] == "workspace-operation-project"
            assert delivery_remediation_map_body["metadata"]["phase"] == "70Z"
            assert (
                delivery_remediation_map_body["metadata"]["contract"]
                == "production_closed_loop_delivery_remediation_map"
            )
            assert delivery_remediation_map_body["metadata"]["source_contract"] == "production_closed_loop_delivery_action_packages"
            assert (
                delivery_remediation_map_body["metadata"]["evidence_source_contract"]
                == "production_closed_loop_delivery_action_evidence_list"
            )
            assert delivery_remediation_map_body["metadata"]["server_side_external_execution"] is False
            assert delivery_remediation_map_body["metadata"]["actual_publish_performed"] is False
            assert delivery_remediation_map_body["remediation_count"] >= 1
            assert delivery_remediation_map_body["immediate_remediation_count"] >= 1
            assert "delivery_remediation_map_is_derived_from_current_gate_contracts" in delivery_remediation_map_body["acceptance_gates"]
            assert "delivery_remediation_map_only_no_external_execution" in delivery_remediation_map_body["boundaries"]
            remediation_by_gate = {item["gate_key"]: item for item in delivery_remediation_map_body["remediations"]}
            provider_remediation = remediation_by_gate["configure_real_openclaw_publish_provider"]
            assert provider_remediation["target_console"] == "technical_operator_console"
            assert provider_remediation["primary_endpoint"] == "/openclaw/provider-diagnostics"
            assert provider_remediation["external_execution_allowed"] is False
            assert provider_remediation["automation_allowed"] is False
            assert provider_remediation["can_be_started_from_customer_machine"] is True
            assert "scripts/check_openclaw_provider.py" in provider_remediation["runbook_references"]
            assert provider_remediation["current_evidence_status"] == "blocked"
            assert provider_remediation["latest_evidence_record_id"] == delivery_action_evidence_body["evidence_record_id"]
            next_cycle_remediation = remediation_by_gate["approve_analysis_and_next_cycle_decision"]
            assert operation_id in next_cycle_remediation["related_operation_ids"]
            assert next_cycle_remediation["primary_endpoint"].endswith(f"/{operation_id}/optimization-decisions")
            assert next_cycle_remediation["requires_operator_confirmation"] is True
            assert "metric analysis package" in next_cycle_remediation["expected_evidence"]
            assert "operator_confirmation_required_before_mutation" in next_cycle_remediation["guardrails"]

            remediation_work_order = await client.post(
                "/api/v1/commercial-operations/production-closed-loop/delivery-remediation-map/work-orders",
                headers=headers,
                json={
                    "remediation_key": provider_remediation["remediation_key"],
                    "work_order_status": "in_progress",
                    "assignee": "technical-operator",
                    "operator_confirmed": True,
                    "work_summary": "Technical operator is preparing a real OpenClaw provider configuration.",
                    "operator_notes": "Recorded from the delivery remediation map.",
                    "metadata": {"source": "api_test_delivery_remediation_work_order"},
                },
            )
            assert remediation_work_order.status_code == 201
            remediation_work_order_body = remediation_work_order.json()
            assert remediation_work_order_body["workspace_id"] == "workspace-operation-project"
            assert remediation_work_order_body["operation_id"] == operation_id
            assert remediation_work_order_body["remediation_key"] == provider_remediation["remediation_key"]
            assert remediation_work_order_body["gate_key"] == "configure_real_openclaw_publish_provider"
            assert remediation_work_order_body["work_order_status"] == "in_progress"
            assert remediation_work_order_body["assignee"] == "technical-operator"
            assert remediation_work_order_body["operator_confirmed"] is True
            assert remediation_work_order_body["target_console"] == "technical_operator_console"
            assert remediation_work_order_body["primary_endpoint"] == "/openclaw/provider-diagnostics"
            assert remediation_work_order_body["completion_gate"] == provider_remediation["completion_gate"]
            assert remediation_work_order_body["metadata"]["phase"] == "71A"
            assert remediation_work_order_body["metadata"]["contract"] == "production_closed_loop_delivery_remediation_work_order"
            assert remediation_work_order_body["metadata"]["source_contract"] == "production_closed_loop_delivery_remediation_map"
            assert remediation_work_order_body["metadata"]["server_side_external_execution"] is False
            assert remediation_work_order_body["metadata"]["actual_publish_performed"] is False
            assert "delivery_remediation_map_contract_matched" in remediation_work_order_body["boundary_checks"]
            assert "delivery_remediation_work_order_only_no_external_execution" in remediation_work_order_body["boundaries"]

            remediation_work_orders = await client.get(
                "/api/v1/commercial-operations/production-closed-loop/delivery-remediation-map/work-orders?gate_key=configure_real_openclaw_publish_provider",
                headers=headers,
            )
            assert remediation_work_orders.status_code == 200
            remediation_work_orders_body = remediation_work_orders.json()
            assert remediation_work_orders_body["workspace_id"] == "workspace-operation-project"
            assert remediation_work_orders_body["work_order_count"] == 1
            assert (
                remediation_work_orders_body["latest_record"]["work_order_id"]
                == remediation_work_order_body["work_order_id"]
            )
            assert "remediation_work_order_is_operator_supplied" in remediation_work_orders_body["acceptance_gates"]
            assert "delivery_remediation_work_order_only_no_external_execution" in remediation_work_orders_body["boundaries"]

            remediation_work_order_coverage = await client.get(
                "/api/v1/commercial-operations/production-closed-loop/delivery-remediation-map/work-order-coverage?platform=douyin&force_metric_due=true",
                headers=headers,
            )
            assert remediation_work_order_coverage.status_code == 200
            remediation_work_order_coverage_body = remediation_work_order_coverage.json()
            assert remediation_work_order_coverage_body["workspace_id"] == "workspace-operation-project"
            assert remediation_work_order_coverage_body["coverage_status"] == "remediation_ownership_required"
            assert remediation_work_order_coverage_body["remediation_count"] == delivery_remediation_map_body["remediation_count"]
            assert remediation_work_order_coverage_body["work_ordered_count"] == 1
            assert remediation_work_order_coverage_body["unassigned_count"] == delivery_remediation_map_body["remediation_count"] - 1
            assert remediation_work_order_coverage_body["in_progress_count"] == 1
            assert remediation_work_order_coverage_body["completed_count"] == 0
            assert remediation_work_order_coverage_body["metadata"]["phase"] == "71B"
            assert (
                remediation_work_order_coverage_body["metadata"]["contract"]
                == "production_closed_loop_delivery_remediation_work_order_coverage"
            )
            assert remediation_work_order_coverage_body["metadata"]["server_side_external_execution"] is False
            provider_coverage = next(
                item
                for item in remediation_work_order_coverage_body["items"]
                if item["gate_key"] == "configure_real_openclaw_publish_provider"
            )
            assert provider_coverage["coverage_status"] == "in_progress"
            assert provider_coverage["latest_work_order_status"] == "in_progress"
            assert provider_coverage["latest_work_order_assignee"] == "technical-operator"
            assert provider_coverage["latest_work_order_operator_confirmed"] is True
            assert provider_coverage["work_order_count"] == 1
            assert "every_open_remediation_has_operator_work_order" in remediation_work_order_coverage_body["acceptance_gates"]
            assert "delivery_remediation_work_order_coverage_only_no_external_execution" in remediation_work_order_coverage_body["boundaries"]

            delivery_audit_blocker_work_order_assignment = await client.post(
                "/api/v1/commercial-operations/production-closed-loop/delivery-audit/blocker-clearance-plan/assign-work-orders",
                headers=headers,
                json={
                    "assignee": "operations-owner",
                    "operator_confirmed": True,
                    "platform": "douyin",
                    "force_metric_due": True,
                    "work_summary": "Assign audit blocker delivery remediation items to the operations owner.",
                    "operator_notes": "Recorded from the audit blocker assignment control.",
                    "metadata": {"source": "api_test_delivery_audit_blocker_assignment"},
                },
            )
            assert delivery_audit_blocker_work_order_assignment.status_code == 201
            delivery_audit_blocker_work_order_assignment_body = delivery_audit_blocker_work_order_assignment.json()
            assert delivery_audit_blocker_work_order_assignment_body["workspace_id"] == "workspace-operation-project"
            assert (
                delivery_audit_blocker_work_order_assignment_body["assignment_status"]
                == "delivery_audit_blocker_work_orders_assigned"
            )
            assert delivery_audit_blocker_work_order_assignment_body["assignee"] == "operations-owner"
            assert (
                delivery_audit_blocker_work_order_assignment_body["created_count"]
                == remediation_work_order_coverage_body["unassigned_count"]
            )
            assert delivery_audit_blocker_work_order_assignment_body["coverage_after"]["unassigned_count"] == 0
            assert (
                delivery_audit_blocker_work_order_assignment_body["coverage_after"]["work_ordered_count"]
                == delivery_audit_blocker_work_order_assignment_body["coverage_after"]["remediation_count"]
            )
            assert delivery_audit_blocker_work_order_assignment_body["clearance_plan_before"]["metadata"]["phase"] == "71G"
            assert delivery_audit_blocker_work_order_assignment_body["clearance_plan_after"]["metadata"]["phase"] == "71G"
            assert delivery_audit_blocker_work_order_assignment_body["metadata"]["phase"] == "71H"
            assert (
                delivery_audit_blocker_work_order_assignment_body["metadata"]["contract"]
                == "production_closed_loop_delivery_audit_blocker_work_order_assignment"
            )
            assert delivery_audit_blocker_work_order_assignment_body["metadata"]["server_side_external_execution"] is False
            assert (
                "operator_confirmation_required_before_blocker_work_order_assignment"
                in delivery_audit_blocker_work_order_assignment_body["acceptance_gates"]
            )
            assert (
                "delivery_audit_blocker_work_order_assignment_only_no_external_execution"
                in delivery_audit_blocker_work_order_assignment_body["boundaries"]
            )
            assert all(
                record["work_order_status"] == "assigned"
                for record in delivery_audit_blocker_work_order_assignment_body["records"]
            )

            remediation_work_order_assignment = await client.post(
                "/api/v1/commercial-operations/production-closed-loop/delivery-remediation-map/work-order-coverage/assign-missing",
                headers=headers,
                json={
                    "assignee": "operations-owner",
                    "operator_confirmed": True,
                    "platform": "douyin",
                    "force_metric_due": True,
                    "work_summary": "Assign remaining delivery remediation items to the operations owner.",
                    "operator_notes": "Recorded from the coverage assignment control.",
                    "metadata": {"source": "api_test_delivery_remediation_assignment"},
                },
            )
            assert remediation_work_order_assignment.status_code == 201
            remediation_work_order_assignment_body = remediation_work_order_assignment.json()
            assert remediation_work_order_assignment_body["workspace_id"] == "workspace-operation-project"
            assert remediation_work_order_assignment_body["assignment_status"] == "no_missing_remediation_work_orders"
            assert remediation_work_order_assignment_body["assignee"] == "operations-owner"
            assert remediation_work_order_assignment_body["created_count"] == 0
            assert remediation_work_order_assignment_body["skipped_count"] == 0
            assert remediation_work_order_assignment_body["coverage_after"]["unassigned_count"] == 0
            assert (
                remediation_work_order_assignment_body["coverage_after"]["work_ordered_count"]
                == remediation_work_order_assignment_body["coverage_after"]["remediation_count"]
            )
            assert remediation_work_order_assignment_body["coverage_after"]["metadata"]["phase"] == "71B"
            assert remediation_work_order_assignment_body["metadata"]["phase"] == "71C"
            assert (
                remediation_work_order_assignment_body["metadata"]["contract"]
                == "production_closed_loop_delivery_remediation_work_order_assignment"
            )
            assert remediation_work_order_assignment_body["metadata"]["server_side_external_execution"] is False
            assert "operator_confirmation_required_before_assignment" in remediation_work_order_assignment_body["acceptance_gates"]
            assert "delivery_remediation_work_order_assignment_only_no_external_execution" in remediation_work_order_assignment_body["boundaries"]
            assert all(record["work_order_status"] == "assigned" for record in remediation_work_order_assignment_body["records"])

            remediation_work_order_execution_prep = await client.get(
                "/api/v1/commercial-operations/production-closed-loop/delivery-remediation-map/work-order-execution-prep?platform=douyin&force_metric_due=true",
                headers=headers,
            )
            assert remediation_work_order_execution_prep.status_code == 200
            remediation_work_order_execution_prep_body = remediation_work_order_execution_prep.json()
            assert remediation_work_order_execution_prep_body["workspace_id"] == "workspace-operation-project"
            assert remediation_work_order_execution_prep_body["prep_status"] == "execution_prep_ready_for_operator_review"
            assert remediation_work_order_execution_prep_body["coverage_status"] == "remediation_work_orders_in_progress"
            assert remediation_work_order_execution_prep_body["prep_count"] == remediation_work_order_execution_prep_body["remediation_count"]
            assert remediation_work_order_execution_prep_body["ready_count"] == remediation_work_order_execution_prep_body["remediation_count"]
            assert remediation_work_order_execution_prep_body["waiting_assignment_count"] == 0
            assert remediation_work_order_execution_prep_body["metadata"]["phase"] == "71D"
            assert (
                remediation_work_order_execution_prep_body["metadata"]["contract"]
                == "production_closed_loop_delivery_remediation_work_order_execution_prep"
            )
            assert remediation_work_order_execution_prep_body["metadata"]["server_side_external_execution"] is False
            assert "assigned_work_order_required_before_execution_review" in remediation_work_order_execution_prep_body["acceptance_gates"]
            assert "delivery_remediation_work_order_execution_prep_only_no_external_execution" in remediation_work_order_execution_prep_body["boundaries"]
            provider_execution_prep = next(
                item
                for item in remediation_work_order_execution_prep_body["items"]
                if item["gate_key"] == "configure_real_openclaw_publish_provider"
            )
            assert provider_execution_prep["prep_status"] == "ready_for_operator_execution_review"
            assert provider_execution_prep["target_console"] == "technical_operator_console"
            assert provider_execution_prep["target_endpoint"] == "/openclaw/provider-diagnostics"
            assert provider_execution_prep["latest_work_order_id"] == remediation_work_order_body["work_order_id"]
            assert provider_execution_prep["latest_work_order"]["assignee"] == "technical-operator"
            assert provider_execution_prep["latest_work_order_operator_confirmed"] is True
            assert provider_execution_prep["requires_customer_machine"] is True
            assert provider_execution_prep["external_execution_allowed"] is False
            assert provider_execution_prep["server_side_external_execution"] is False
            assert provider_execution_prep["execution_payload_template"]["operator_confirmed"] is False
            assert "provider smoke pass" in provider_execution_prep["evidence_requirements"]
            assert "does_not_execute_target_endpoint" in provider_execution_prep["boundaries"]

            remediation_work_order_completion = await client.post(
                "/api/v1/commercial-operations/production-closed-loop/delivery-remediation-map/work-order-execution-prep/complete",
                headers=headers,
                json={
                    "work_order_id": provider_execution_prep["latest_work_order_id"],
                    "operator_confirmed": True,
                    "completed_by": "technical-operator",
                    "platform": "douyin",
                    "force_metric_due": True,
                    "evidence_links": [{"title": "Provider smoke pass", "url": "file:///evidence/provider-smoke.json"}],
                    "completion_summary": "Real OpenClaw provider was configured and smoke evidence was attached.",
                    "operator_notes": "Recorded from the remediation execution-prep completion control.",
                    "metadata": {"source": "api_test_delivery_remediation_completion"},
                },
            )
            assert remediation_work_order_completion.status_code == 201
            remediation_work_order_completion_body = remediation_work_order_completion.json()
            assert remediation_work_order_completion_body["workspace_id"] == "workspace-operation-project"
            assert (
                remediation_work_order_completion_body["completion_status"]
                == "remediation_work_order_completed_pending_readiness_refresh"
            )
            assert remediation_work_order_completion_body["readiness_refresh_required"] is True
            assert (
                remediation_work_order_completion_body["readiness_refresh_next_action"]
                == "refresh_readiness_after_work_order:configure_real_openclaw_publish_provider"
            )
            assert remediation_work_order_completion_body["metadata"]["phase"] == "71E"
            assert (
                remediation_work_order_completion_body["metadata"]["contract"]
                == "production_closed_loop_delivery_remediation_work_order_completion"
            )
            assert remediation_work_order_completion_body["metadata"]["server_side_external_execution"] is False
            assert "completed_work_order_requires_readiness_refresh" in remediation_work_order_completion_body["acceptance_gates"]
            assert "delivery_remediation_work_order_completion_only_no_external_execution" in remediation_work_order_completion_body["boundaries"]
            completed_record = remediation_work_order_completion_body["completed_record"]
            assert completed_record["work_order_status"] == "completed"
            assert completed_record["gate_key"] == "configure_real_openclaw_publish_provider"
            assert completed_record["assignee"] == "technical-operator"
            assert completed_record["operator_confirmed"] is True
            assert completed_record["metadata"]["completion_phase"] == "71E"
            assert completed_record["metadata"]["previous_work_order_id"] == provider_execution_prep["latest_work_order_id"]
            assert completed_record["metadata"]["server_side_external_execution"] is False
            assert remediation_work_order_completion_body["coverage_after"]["completed_count"] == 1
            assert remediation_work_order_completion_body["coverage_after"]["unassigned_count"] == 0
            completed_provider_coverage = next(
                item
                for item in remediation_work_order_completion_body["coverage_after"]["items"]
                if item["gate_key"] == "configure_real_openclaw_publish_provider"
            )
            assert completed_provider_coverage["coverage_status"] == "completed_pending_readiness_refresh"
            completed_provider_prep = next(
                item
                for item in remediation_work_order_completion_body["execution_prep_after"]["items"]
                if item["gate_key"] == "configure_real_openclaw_publish_provider"
            )
            assert completed_provider_prep["prep_status"] == "completed_pending_readiness_refresh"
            assert completed_provider_prep["latest_work_order_id"] == completed_record["work_order_id"]
            assert completed_provider_prep["latest_work_order"]["work_order_status"] == "completed"
            assert "does_not_execute_target_endpoint" in completed_provider_prep["boundaries"]

            remediation_work_order_readiness_refresh = await client.post(
                "/api/v1/commercial-operations/production-closed-loop/delivery-remediation-map/work-order-completion/readiness-refresh",
                headers=headers,
                json={
                    "operation_id": operation_id,
                    "gate_key": "configure_real_openclaw_publish_provider",
                    "operator_confirmed": True,
                    "platform": "douyin",
                    "force_metric_due": True,
                    "refresh_notes": "Refresh readiness after provider remediation completion evidence.",
                    "metadata": {"source": "api_test_delivery_remediation_readiness_refresh"},
                },
            )
            assert remediation_work_order_readiness_refresh.status_code == 200
            remediation_work_order_readiness_refresh_body = remediation_work_order_readiness_refresh.json()
            assert remediation_work_order_readiness_refresh_body["workspace_id"] == "workspace-operation-project"
            assert remediation_work_order_readiness_refresh_body["operation_id"] == operation_id
            assert (
                remediation_work_order_readiness_refresh_body["refresh_status"]
                == "completed_remediation_work_order_readiness_refreshed"
            )
            assert remediation_work_order_readiness_refresh_body["completed_work_order_count"] == 1
            assert remediation_work_order_readiness_refresh_body["readiness_refresh_required"] is False
            assert remediation_work_order_readiness_refresh_body["operator_confirmed"] is True
            assert remediation_work_order_readiness_refresh_body["readiness_status"] == "ready_for_metric_feedback"
            assert remediation_work_order_readiness_refresh_body["next_action_key"] == "create_or_review_optimization_decision"
            assert remediation_work_order_readiness_refresh_body["metadata"]["phase"] == "71F"
            assert (
                remediation_work_order_readiness_refresh_body["metadata"]["contract"]
                == "production_closed_loop_delivery_remediation_work_order_readiness_refresh"
            )
            assert remediation_work_order_readiness_refresh_body["metadata"]["server_side_external_execution"] is False
            assert "completed_remediation_work_order_required_before_refresh" in remediation_work_order_readiness_refresh_body["acceptance_gates"]
            assert (
                "delivery_remediation_work_order_readiness_refresh_only_no_external_execution"
                in remediation_work_order_readiness_refresh_body["boundaries"]
            )
            assert (
                remediation_work_order_readiness_refresh_body["refresh_record"]["metadata"]["contract"]
                == "production_closed_loop_delivery_remediation_work_order_readiness_refresh"
            )
            assert completed_record["work_order_id"] in remediation_work_order_readiness_refresh_body["refresh_record"]["completed_work_order_ids"]
            assert (
                remediation_work_order_readiness_refresh_body["readiness"]["metadata"]["contract"]
                == "production_closed_loop_e2e_readiness"
            )
            assert (
                remediation_work_order_readiness_refresh_body["next_action"]["metadata"]["contract"]
                == "production_closed_loop_next_action"
            )
            refreshed_provider_coverage = next(
                item
                for item in remediation_work_order_readiness_refresh_body["coverage_after"]["items"]
                if item["gate_key"] == "configure_real_openclaw_publish_provider"
            )
            assert refreshed_provider_coverage["coverage_status"] == "completed_readiness_refreshed"
            assert refreshed_provider_coverage["latest_readiness_refresh_status"] == "completed_remediation_work_order_readiness_refreshed"
            refreshed_provider_prep = next(
                item
                for item in remediation_work_order_readiness_refresh_body["execution_prep_after"]["items"]
                if item["gate_key"] == "configure_real_openclaw_publish_provider"
            )
            assert refreshed_provider_prep["prep_status"] == "completed_readiness_refreshed"
            assert refreshed_provider_prep["latest_readiness_refresh_status"] == "completed_remediation_work_order_readiness_refreshed"

            delivery_audit_blocker_clearance_plan = await client.get(
                "/api/v1/commercial-operations/production-closed-loop/delivery-audit/blocker-clearance-plan?platform=douyin&force_metric_due=true",
                headers=headers,
            )
            assert delivery_audit_blocker_clearance_plan.status_code == 200
            delivery_audit_blocker_clearance_plan_body = delivery_audit_blocker_clearance_plan.json()
            assert delivery_audit_blocker_clearance_plan_body["workspace_id"] == "workspace-operation-project"
            assert delivery_audit_blocker_clearance_plan_body["metadata"]["phase"] == "71G"
            assert (
                delivery_audit_blocker_clearance_plan_body["metadata"]["contract"]
                == "production_closed_loop_delivery_audit_blocker_clearance_plan"
            )
            assert delivery_audit_blocker_clearance_plan_body["metadata"]["server_side_external_execution"] is False
            assert "production_config_errors_mapped_to_clearance_items" in delivery_audit_blocker_clearance_plan_body["acceptance_gates"]
            assert "delivery_audit_blocker_clearance_plan_only_no_external_execution" in delivery_audit_blocker_clearance_plan_body["boundaries"]
            provider_clearance_item = next(
                item
                for item in delivery_audit_blocker_clearance_plan_body["items"]
                if item["gate_key"] == "configure_real_openclaw_publish_provider"
            )
            assert provider_clearance_item["external_dependency_required"] is True
            assert provider_clearance_item["can_be_resolved_by_ui"] is False
            assert provider_clearance_item["prep_status"] == "completed_readiness_refreshed"
            assert provider_clearance_item["latest_readiness_refresh_status"] == "completed_remediation_work_order_readiness_refreshed"
            assert "scripts/check_openclaw_provider.py" in provider_clearance_item["runbook_references"]

            delivery_audit_blocker_runbooks = await client.get(
                "/api/v1/commercial-operations/production-closed-loop/delivery-audit/blocker-runbook-packages?platform=douyin&force_metric_due=true",
                headers=headers,
            )
            assert delivery_audit_blocker_runbooks.status_code == 200
            delivery_audit_blocker_runbooks_body = delivery_audit_blocker_runbooks.json()
            assert delivery_audit_blocker_runbooks_body["workspace_id"] == "workspace-operation-project"
            assert delivery_audit_blocker_runbooks_body["metadata"]["phase"] == "71I"
            assert (
                delivery_audit_blocker_runbooks_body["metadata"]["contract"]
                == "production_closed_loop_delivery_audit_blocker_runbook_handoff"
            )
            assert delivery_audit_blocker_runbooks_body["metadata"]["server_side_external_execution"] is False
            assert "delivery_audit_blockers_have_operator_runbook_handoff" in delivery_audit_blocker_runbooks_body["acceptance_gates"]
            assert (
                "delivery_audit_blocker_runbook_handoff_only_no_external_execution"
                in delivery_audit_blocker_runbooks_body["boundaries"]
            )
            provider_runbook = next(
                item
                for item in delivery_audit_blocker_runbooks_body["packages"]
                if item["gate_key"] == "configure_real_openclaw_publish_provider"
            )
            assert provider_runbook["external_dependency_required"] is True
            assert "WORKER_CLIENT_OPENCLAW_PROVIDER" in provider_runbook["required_inputs"]
            assert "python scripts/check_openclaw_provider.py" in provider_runbook["verification_commands"]
            assert "does_not_store_or_print_secrets" in provider_runbook["boundaries"]

            delivery_audit_blocker_runbook_evidence = await client.post(
                "/api/v1/commercial-operations/production-closed-loop/delivery-audit/blocker-runbook-packages/evidence-records",
                headers=headers,
                json={
                    "package_key": provider_runbook["package_key"],
                    "gate_key": provider_runbook["gate_key"],
                    "evidence_status": "blocked",
                    "operator_confirmed": False,
                    "platform": "douyin",
                    "force_metric_due": True,
                    "evidence_summary": "Provider configuration still needs external operator work.",
                    "operator_notes": "Recorded from the runbook evidence control.",
                    "metadata": {"source": "api_test_delivery_audit_blocker_runbook_evidence"},
                },
            )
            assert delivery_audit_blocker_runbook_evidence.status_code == 201
            delivery_audit_blocker_runbook_evidence_body = delivery_audit_blocker_runbook_evidence.json()
            assert delivery_audit_blocker_runbook_evidence_body["workspace_id"] == "workspace-operation-project"
            assert delivery_audit_blocker_runbook_evidence_body["metadata"]["phase"] == "71J"
            assert (
                delivery_audit_blocker_runbook_evidence_body["metadata"]["contract"]
                == "production_closed_loop_delivery_audit_blocker_runbook_evidence"
            )
            assert delivery_audit_blocker_runbook_evidence_body["metadata"]["server_side_external_execution"] is False
            assert delivery_audit_blocker_runbook_evidence_body["package_key"] == provider_runbook["package_key"]
            assert delivery_audit_blocker_runbook_evidence_body["gate_key"] == "configure_real_openclaw_publish_provider"
            assert delivery_audit_blocker_runbook_evidence_body["evidence_status"] == "blocked"
            assert delivery_audit_blocker_runbook_evidence_body["operator_confirmed"] is False
            assert "WORKER_CLIENT_OPENCLAW_PROVIDER" in delivery_audit_blocker_runbook_evidence_body["required_inputs"]
            assert "python scripts/check_openclaw_provider.py" in delivery_audit_blocker_runbook_evidence_body["verification_commands"]
            assert "does_not_store_or_print_secrets" in delivery_audit_blocker_runbook_evidence_body["boundaries"]

            delivery_audit_blocker_runbook_evidence_list = await client.get(
                "/api/v1/commercial-operations/production-closed-loop/delivery-audit/blocker-runbook-packages/evidence-records?gate_key=configure_real_openclaw_publish_provider",
                headers=headers,
            )
            assert delivery_audit_blocker_runbook_evidence_list.status_code == 200
            delivery_audit_blocker_runbook_evidence_list_body = delivery_audit_blocker_runbook_evidence_list.json()
            assert delivery_audit_blocker_runbook_evidence_list_body["workspace_id"] == "workspace-operation-project"
            assert delivery_audit_blocker_runbook_evidence_list_body["record_count"] == 1
            assert delivery_audit_blocker_runbook_evidence_list_body["latest_record"]["evidence_record_id"] == delivery_audit_blocker_runbook_evidence_body["evidence_record_id"]
            assert delivery_audit_blocker_runbook_evidence_list_body["metadata"]["phase"] == "71J"
            assert (
                delivery_audit_blocker_runbook_evidence_list_body["metadata"]["contract"]
                == "production_closed_loop_delivery_audit_blocker_runbook_evidence_list"
            )
            assert "runbook_evidence_is_operator_supplied" in delivery_audit_blocker_runbook_evidence_list_body["acceptance_gates"]
            assert (
                "delivery_audit_blocker_runbook_evidence_only_no_external_execution"
                in delivery_audit_blocker_runbook_evidence_list_body["boundaries"]
            )

            delivery_audit_blocker_runbook_evidence_coverage = await client.get(
                "/api/v1/commercial-operations/production-closed-loop/delivery-audit/blocker-runbook-packages/evidence-coverage?platform=douyin&force_metric_due=true",
                headers=headers,
            )
            assert delivery_audit_blocker_runbook_evidence_coverage.status_code == 200
            delivery_audit_blocker_runbook_evidence_coverage_body = delivery_audit_blocker_runbook_evidence_coverage.json()
            assert delivery_audit_blocker_runbook_evidence_coverage_body["workspace_id"] == "workspace-operation-project"
            assert delivery_audit_blocker_runbook_evidence_coverage_body["metadata"]["phase"] == "71K"
            assert (
                delivery_audit_blocker_runbook_evidence_coverage_body["metadata"]["contract"]
                == "production_closed_loop_delivery_audit_blocker_runbook_evidence_coverage"
            )
            assert delivery_audit_blocker_runbook_evidence_coverage_body["metadata"]["server_side_external_execution"] is False
            assert delivery_audit_blocker_runbook_evidence_coverage_body["blocked_count"] >= 1
            assert delivery_audit_blocker_runbook_evidence_coverage_body["evidenced_count"] >= 1
            assert delivery_audit_blocker_runbook_evidence_coverage_body["missing_evidence_count"] >= 0
            assert "every_runbook_package_has_operator_evidence" in delivery_audit_blocker_runbook_evidence_coverage_body["acceptance_gates"]
            assert (
                "delivery_audit_blocker_runbook_evidence_coverage_only_no_external_execution"
                in delivery_audit_blocker_runbook_evidence_coverage_body["boundaries"]
            )
            provider_coverage = next(
                item
                for item in delivery_audit_blocker_runbook_evidence_coverage_body["items"]
                if item["gate_key"] == "configure_real_openclaw_publish_provider"
            )
            assert provider_coverage["coverage_status"] == "runbook_evidence_blocked"
            assert provider_coverage["latest_evidence_status"] == "blocked"
            assert provider_coverage["evidence_record_count"] == 1
            assert provider_coverage["latest_evidence_record_id"] == delivery_audit_blocker_runbook_evidence_body["evidence_record_id"]
            assert "python scripts/check_openclaw_provider.py" in provider_coverage["verification_commands"]
            assert "does_not_store_or_print_secrets" in provider_coverage["boundaries"]
            assert delivery_audit_blocker_runbook_evidence_coverage_body["evidence_records"]["record_count"] == 1

            delivery_audit_next_action_plan = await client.get(
                "/api/v1/commercial-operations/production-closed-loop/delivery-audit/next-action-plan?platform=douyin&force_metric_due=true",
                headers=headers,
            )
            assert delivery_audit_next_action_plan.status_code == 200
            delivery_audit_next_action_plan_body = delivery_audit_next_action_plan.json()
            assert delivery_audit_next_action_plan_body["workspace_id"] == "workspace-operation-project"
            assert delivery_audit_next_action_plan_body["metadata"]["phase"] == "71O"
            assert (
                delivery_audit_next_action_plan_body["metadata"]["contract"]
                == "production_closed_loop_delivery_audit_next_action_plan"
            )
            assert delivery_audit_next_action_plan_body["metadata"]["server_side_external_execution"] is False
            assert delivery_audit_next_action_plan_body["runbook_evidence_coverage_ready"] is False
            assert delivery_audit_next_action_plan_body["next_action_count"] >= 1
            delivery_audit_next_action_keys = {
                action["action_key"]
                for action in delivery_audit_next_action_plan_body["next_actions"]
            }
            assert "resolve_runbook_evidence_coverage" in delivery_audit_next_action_keys
            assert "configure_real_openclaw_provider" in delivery_audit_next_action_keys
            assert (
                "operator_visible_audit_next_actions_required_before_100_percent_claim"
                in delivery_audit_next_action_plan_body["acceptance_gates"]
            )
            assert (
                "delivery_audit_next_action_plan_only_no_external_execution"
                in delivery_audit_next_action_plan_body["boundaries"]
            )
            resolve_runbook_action = next(
                action
                for action in delivery_audit_next_action_plan_body["next_actions"]
                if action["action_key"] == "resolve_runbook_evidence_coverage"
            )
            assert resolve_runbook_action["owner"] == "delivery_operator"
            assert resolve_runbook_action["required_endpoint"].endswith("/evidence-records")
            assert resolve_runbook_action["can_be_resolved_by_ui"] is True

            delivery_audit_operator_queue = await client.get(
                "/api/v1/commercial-operations/production-closed-loop/delivery-audit/next-action-plan/operator-queue?platform=douyin&force_metric_due=true",
                headers=headers,
            )
            assert delivery_audit_operator_queue.status_code == 200
            delivery_audit_operator_queue_body = delivery_audit_operator_queue.json()
            assert delivery_audit_operator_queue_body["workspace_id"] == "workspace-operation-project"
            assert delivery_audit_operator_queue_body["metadata"]["phase"] == "71P"
            assert (
                delivery_audit_operator_queue_body["metadata"]["contract"]
                == "production_closed_loop_delivery_audit_operator_queue"
            )
            assert delivery_audit_operator_queue_body["metadata"]["server_side_external_execution"] is False
            assert delivery_audit_operator_queue_body["source_plan"]["metadata"]["phase"] == "71O"
            assert delivery_audit_operator_queue_body["action_count"] == delivery_audit_next_action_plan_body["next_action_count"]
            assert delivery_audit_operator_queue_body["owner_count"] >= 1
            assert delivery_audit_operator_queue_body["first_item"]["action_key"] == "configure_real_openclaw_provider"
            assert delivery_audit_operator_queue_body["first_item"]["resolution_mode"] == "external_provider_configuration"
            assert delivery_audit_operator_queue_body["first_item"]["blocked_by_external_dependency"] is True
            assert "operator_queue_visible_before_100_percent_claim" in delivery_audit_operator_queue_body["acceptance_gates"]
            assert "delivery_audit_operator_queue_only_no_external_execution" in delivery_audit_operator_queue_body["boundaries"]
            delivery_audit_queue_items = [
                item
                for group in delivery_audit_operator_queue_body["owner_groups"]
                for item in group["items"]
            ]
            runbook_queue_item = next(
                item for item in delivery_audit_queue_items if item["action_key"] == "resolve_runbook_evidence_coverage"
            )
            assert runbook_queue_item["resolution_mode"] == "record_runbook_evidence"
            assert runbook_queue_item["endpoint_method"] == "POST"
            assert runbook_queue_item["can_be_resolved_by_ui"] is True
            assert runbook_queue_item["record_count"] == 0

            delivery_audit_operator_queue_record = await client.post(
                "/api/v1/commercial-operations/production-closed-loop/delivery-audit/next-action-plan/operator-queue/records",
                headers=headers,
                json={
                    "queue_key": runbook_queue_item["queue_key"],
                    "action_key": runbook_queue_item["action_key"],
                    "owner": runbook_queue_item["owner"],
                    "record_status": "in_progress",
                    "operator_confirmed": False,
                    "platform": "douyin",
                    "force_metric_due": True,
                    "evidence_summary": "Operator has taken ownership of the runbook evidence coverage queue item.",
                    "operator_notes": "Recorded from the operator queue status control.",
                    "metadata": {"source": "api_test_delivery_audit_operator_queue_record"},
                },
            )
            assert delivery_audit_operator_queue_record.status_code == 201
            delivery_audit_operator_queue_record_body = delivery_audit_operator_queue_record.json()
            assert delivery_audit_operator_queue_record_body["workspace_id"] == "workspace-operation-project"
            assert delivery_audit_operator_queue_record_body["metadata"]["phase"] == "71Q"
            assert (
                delivery_audit_operator_queue_record_body["metadata"]["contract"]
                == "production_closed_loop_delivery_audit_operator_queue_record"
            )
            assert delivery_audit_operator_queue_record_body["metadata"]["server_side_external_execution"] is False
            assert delivery_audit_operator_queue_record_body["queue_key"] == runbook_queue_item["queue_key"]
            assert delivery_audit_operator_queue_record_body["action_key"] == "resolve_runbook_evidence_coverage"
            assert delivery_audit_operator_queue_record_body["record_status"] == "in_progress"
            assert delivery_audit_operator_queue_record_body["operator_confirmed"] is False
            assert delivery_audit_operator_queue_record_body["resolution_mode"] == "record_runbook_evidence"
            assert "does_not_execute_target_endpoint" in delivery_audit_operator_queue_record_body["boundaries"]

            delivery_audit_operator_queue_record_list = await client.get(
                "/api/v1/commercial-operations/production-closed-loop/delivery-audit/next-action-plan/operator-queue/records?action_key=resolve_runbook_evidence_coverage",
                headers=headers,
            )
            assert delivery_audit_operator_queue_record_list.status_code == 200
            delivery_audit_operator_queue_record_list_body = delivery_audit_operator_queue_record_list.json()
            assert delivery_audit_operator_queue_record_list_body["workspace_id"] == "workspace-operation-project"
            assert delivery_audit_operator_queue_record_list_body["record_count"] == 1
            assert delivery_audit_operator_queue_record_list_body["status_counts"]["in_progress"] == 1
            assert (
                delivery_audit_operator_queue_record_list_body["latest_record"]["record_id"]
                == delivery_audit_operator_queue_record_body["record_id"]
            )
            assert delivery_audit_operator_queue_record_list_body["metadata"]["phase"] == "71Q"
            assert (
                delivery_audit_operator_queue_record_list_body["metadata"]["contract"]
                == "production_closed_loop_delivery_audit_operator_queue_record_list"
            )
            assert "operator_queue_records_are_operator_supplied" in delivery_audit_operator_queue_record_list_body["acceptance_gates"]
            assert (
                "delivery_audit_operator_queue_records_only_no_external_execution"
                in delivery_audit_operator_queue_record_list_body["boundaries"]
            )

            delivery_audit_operator_queue_after_record = await client.get(
                "/api/v1/commercial-operations/production-closed-loop/delivery-audit/next-action-plan/operator-queue?platform=douyin&force_metric_due=true",
                headers=headers,
            )
            assert delivery_audit_operator_queue_after_record.status_code == 200
            delivery_audit_operator_queue_after_record_body = delivery_audit_operator_queue_after_record.json()
            delivery_audit_queue_items_after_record = [
                item
                for group in delivery_audit_operator_queue_after_record_body["owner_groups"]
                for item in group["items"]
            ]
            runbook_queue_item_after_record = next(
                item for item in delivery_audit_queue_items_after_record if item["action_key"] == "resolve_runbook_evidence_coverage"
            )
            assert runbook_queue_item_after_record["record_count"] == 1
            assert runbook_queue_item_after_record["latest_record_status"] == "in_progress"
            assert (
                runbook_queue_item_after_record["latest_record_id"]
                == delivery_audit_operator_queue_record_body["record_id"]
            )

            openclaw_provider_handoff = await client.get(
                "/api/v1/commercial-operations/production-closed-loop/delivery-audit/openclaw-provider-handoff",
                headers=headers,
            )
            assert openclaw_provider_handoff.status_code == 200
            openclaw_provider_handoff_body = openclaw_provider_handoff.json()
            assert openclaw_provider_handoff_body["workspace_id"] == "workspace-operation-project"
            assert openclaw_provider_handoff_body["metadata"]["phase"] == "71R"
            assert (
                openclaw_provider_handoff_body["metadata"]["contract"]
                == "production_closed_loop_delivery_audit_openclaw_provider_handoff"
            )
            assert openclaw_provider_handoff_body["metadata"]["server_side_external_execution"] is False
            assert openclaw_provider_handoff_body["metadata"]["secret_values_redacted"] is True
            assert openclaw_provider_handoff_body["required_config_count"] >= 5
            assert "WORKER_CLIENT_OPENCLAW_PROVIDER" in {
                item["config_key"] for item in openclaw_provider_handoff_body["config_items"]
            }
            api_key_handoff = next(
                item
                for item in openclaw_provider_handoff_body["config_items"]
                if item["config_key"] == "WORKER_CLIENT_OPENCLAW_API_KEY"
            )
            assert api_key_handoff["secret"] is True
            assert api_key_handoff["current_state"] in {"<set>", "<empty>", "<placeholder>", "<too-short>"}
            assert "python scripts/check_openclaw_provider.py" in " ".join(openclaw_provider_handoff_body["verification_commands"])
            assert "does_not_mutate_environment" in openclaw_provider_handoff_body["boundaries"]
            assert "does_not_restart_services" in openclaw_provider_handoff_body["boundaries"]

            premature_runbook_readiness_refresh = await client.post(
                "/api/v1/commercial-operations/production-closed-loop/delivery-audit/blocker-runbook-packages/evidence-coverage/readiness-refresh",
                headers=headers,
                json={
                    "platform": "douyin",
                    "force_metric_due": True,
                    "operator_confirmed": True,
                    "refresh_notes": "Should be rejected while runbook evidence coverage is incomplete.",
                    "metadata": {"source": "api_test_delivery_audit_blocker_runbook_evidence_readiness_refresh_rejected"},
                },
            )
            assert premature_runbook_readiness_refresh.status_code == 400

            for runbook_package in delivery_audit_blocker_runbooks_body["packages"]:
                resolved_runbook_evidence = await client.post(
                    "/api/v1/commercial-operations/production-closed-loop/delivery-audit/blocker-runbook-packages/evidence-records",
                    headers=headers,
                    json={
                        "package_key": runbook_package["package_key"],
                        "gate_key": runbook_package["gate_key"],
                        "evidence_status": "resolved",
                        "operator_confirmed": True,
                        "platform": "douyin",
                        "force_metric_due": True,
                        "evidence_summary": f"Resolved evidence supplied for {runbook_package['package_key']}.",
                        "operator_notes": "Recorded from the runbook evidence readiness refresh test.",
                        "metadata": {"source": "api_test_delivery_audit_blocker_runbook_evidence_resolved"},
                    },
                )
                assert resolved_runbook_evidence.status_code == 201
                assert resolved_runbook_evidence.json()["evidence_status"] == "resolved"

            resolved_runbook_evidence_coverage = await client.get(
                "/api/v1/commercial-operations/production-closed-loop/delivery-audit/blocker-runbook-packages/evidence-coverage?platform=douyin&force_metric_due=true",
                headers=headers,
            )
            assert resolved_runbook_evidence_coverage.status_code == 200
            resolved_runbook_evidence_coverage_body = resolved_runbook_evidence_coverage.json()
            assert resolved_runbook_evidence_coverage_body["metadata"]["phase"] == "71K"
            assert resolved_runbook_evidence_coverage_body["package_count"] == len(delivery_audit_blocker_runbooks_body["packages"])
            assert resolved_runbook_evidence_coverage_body["resolved_count"] == resolved_runbook_evidence_coverage_body["package_count"]
            assert resolved_runbook_evidence_coverage_body["missing_evidence_count"] == 0
            assert resolved_runbook_evidence_coverage_body["blocked_count"] == 0

            resolved_delivery_audit_next_action_plan = await client.get(
                "/api/v1/commercial-operations/production-closed-loop/delivery-audit/next-action-plan?platform=douyin&force_metric_due=true",
                headers=headers,
            )
            assert resolved_delivery_audit_next_action_plan.status_code == 200
            resolved_delivery_audit_next_action_plan_body = resolved_delivery_audit_next_action_plan.json()
            assert resolved_delivery_audit_next_action_plan_body["runbook_evidence_coverage_ready"] is True
            assert resolved_delivery_audit_next_action_plan_body["runbook_evidence_readiness_refresh_required"] is True
            assert {
                action["action_key"]
                for action in resolved_delivery_audit_next_action_plan_body["next_actions"]
            } >= {"refresh_runbook_evidence_readiness"}

            runbook_evidence_readiness_refresh = await client.post(
                "/api/v1/commercial-operations/production-closed-loop/delivery-audit/blocker-runbook-packages/evidence-coverage/readiness-refresh",
                headers=headers,
                json={
                    "platform": "douyin",
                    "force_metric_due": True,
                    "operator_confirmed": True,
                    "refresh_notes": "All runbook evidence is resolved; refresh readiness snapshot.",
                    "metadata": {"source": "api_test_delivery_audit_blocker_runbook_evidence_readiness_refresh"},
                },
            )
            assert runbook_evidence_readiness_refresh.status_code == 200
            runbook_evidence_readiness_refresh_body = runbook_evidence_readiness_refresh.json()
            assert runbook_evidence_readiness_refresh_body["workspace_id"] == "workspace-operation-project"
            assert runbook_evidence_readiness_refresh_body["metadata"]["phase"] == "71L"
            assert (
                runbook_evidence_readiness_refresh_body["metadata"]["contract"]
                == "production_closed_loop_delivery_audit_blocker_runbook_evidence_readiness_refresh"
            )
            assert runbook_evidence_readiness_refresh_body["operator_confirmed"] is True
            assert runbook_evidence_readiness_refresh_body["coverage_after"]["resolved_count"] == runbook_evidence_readiness_refresh_body["coverage_after"]["package_count"]
            assert "all_runbook_evidence_resolved_before_refresh" in runbook_evidence_readiness_refresh_body["acceptance_gates"]
            assert (
                "delivery_audit_blocker_runbook_evidence_readiness_refresh_only_no_external_execution"
                in runbook_evidence_readiness_refresh_body["boundaries"]
            )
            assert runbook_evidence_readiness_refresh_body["metadata"]["server_side_external_execution"] is False
            assert runbook_evidence_readiness_refresh_body["metadata"]["actual_publish_performed"] is False

            production_next_action = await client.get(
                f"/api/v1/commercial-operations/{operation_id}/production-closed-loop/next-action?platform=douyin&force_metric_due=true",
                headers=headers,
            )
            assert production_next_action.status_code == 200
            next_action_body = production_next_action.json()
            assert next_action_body["operation_id"] == operation_id
            assert next_action_body["workspace_id"] == "workspace-operation-project"
            assert next_action_body["readiness_status"] == "ready_for_metric_feedback"
            assert next_action_body["current_stage_key"] == "analysis_improvement"
            assert next_action_body["metadata"]["contract"] == "production_closed_loop_next_action"
            assert next_action_body["metadata"]["source_readiness_contract"] == "production_closed_loop_e2e_readiness"
            assert next_action_body["metadata"]["server_side_external_execution"] is False
            assert next_action_body["selected_action_key"] == "create_or_review_optimization_decision"
            assert next_action_body["selected_action"]["stage_key"] == "analysis_improvement"
            assert next_action_body["selected_action"]["method"] == "POST"
            assert next_action_body["selected_action"]["endpoint"].endswith("/optimization-decisions")
            assert next_action_body["selected_action"]["requires_operator_approval"] is True
            assert "metric analysis package" in next_action_body["selected_action"]["evidence_requirements"]
            assert "next_action_contract_must_match_current_readiness_stage" in next_action_body["acceptance_gates"]
            assert "does_not_execute_customer_machine_actions_from_server" in next_action_body["boundaries"]

            production_action_audit = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/production-closed-loop/next-action/audit-records?platform=douyin&force_metric_due=true",
                headers=headers,
                json={
                    "action_key": next_action_body["selected_action_key"],
                    "stage_key": next_action_body["selected_action"]["stage_key"],
                    "action_status": "confirmed",
                    "operator_confirmed": True,
                    "target_method": next_action_body["selected_action"]["method"],
                    "target_endpoint": next_action_body["selected_action"]["endpoint"],
                    "submitted_payload": {"metadata": {"source": "api_test_controlled_action_audit"}},
                    "execution_summary": "Operator confirmed the next-action contract in the API test.",
                    "boundary_checks": ["no_server_side_external_execution", "operator_approval_boundary_preserved"],
                    "metadata": {"test": "phase_68z1"},
                },
            )
            assert production_action_audit.status_code == 201
            action_audit_body = production_action_audit.json()
            assert action_audit_body["operation_id"] == operation_id
            assert action_audit_body["workspace_id"] == "workspace-operation-project"
            assert action_audit_body["action_key"] == "create_or_review_optimization_decision"
            assert action_audit_body["action_status"] == "confirmed"
            assert action_audit_body["validation_status"] == "accepted"
            assert action_audit_body["operator_confirmed"] is True
            assert action_audit_body["target_endpoint"].endswith("/optimization-decisions")
            assert action_audit_body["contract_snapshot"]["selected_action_key"] == next_action_body["selected_action_key"]
            assert action_audit_body["metadata"]["contract"] == "production_closed_loop_next_action_audit"
            assert action_audit_body["metadata"]["server_side_external_execution"] is False
            assert "server_side_external_execution_false" in action_audit_body["boundary_checks"]

            production_action_audits = await client.get(
                f"/api/v1/commercial-operations/{operation_id}/production-closed-loop/next-action/audit-records",
                headers=headers,
            )
            assert production_action_audits.status_code == 200
            action_audits_body = production_action_audits.json()
            assert action_audits_body["operation_id"] == operation_id
            assert action_audits_body["audit_count"] >= 2
            assert action_audits_body["latest_record"]["audit_id"] == action_audit_body["audit_id"]
            assert action_audits_body["counts_by_status"]["confirmed"] >= 2
            assert action_audit_body["audit_id"] in {item["audit_id"] for item in action_audits_body["records"]}
            assert publish_status_action_audit_body["audit_id"] in {
                item["audit_id"] for item in action_audits_body["records"]
            }
            assert action_audits_body["operator_checklist"][0]["step_key"] == "confirm"
            assert [item["status"] for item in action_audits_body["operator_checklist"]] == [
                "done",
                "next",
                "blocked",
                "blocked",
            ]
            assert action_audits_body["primary_step"]["step_key"] == "bind"
            assert action_audits_body["metadata"]["primary_step_contract"] == "production_closed_loop_action_audit_primary_step"
            assert action_audits_body["primary_step_staleness"]["step_key"] == "bind"
            assert action_audits_body["primary_step_staleness"]["status"] == "fresh"
            assert action_audits_body["primary_step_staleness"]["escalation_recommended"] is False
            assert (
                action_audits_body["metadata"]["primary_step_staleness_contract"]
                == "production_closed_loop_action_audit_primary_step_staleness"
            )
            assert (
                action_audits_body["metadata"]["operator_checklist_contract"]
                == "production_closed_loop_action_audit_operator_checklist"
            )
            assert action_audits_body["metadata"]["contract"] == "production_closed_loop_next_action_audit"
            assert "does_not_execute_target_endpoint" in action_audits_body["boundaries"]

            stale_waiting_since = (datetime.now(UTC) - timedelta(hours=5)).isoformat()
            async with session_factory() as direct_session:
                operation = await direct_session.get(CommercialOperation, UUID(operation_id))
                assert operation is not None
                operation_metadata = dict(operation.operation_metadata or {})
                audit_history = [
                    dict(item)
                    for item in operation_metadata.get("production_closed_loop_action_audits", [])
                    if isinstance(item, dict)
                ]
                for item in audit_history:
                    if item.get("audit_id") == action_audit_body["audit_id"]:
                        item["created_at"] = stale_waiting_since
                        operation_metadata["production_closed_loop_action_audit_latest"] = item
                        break
                operation_metadata["production_closed_loop_action_audits"] = audit_history
                operation.operation_metadata = operation_metadata
                await direct_session.commit()

            stale_action_audits = await client.get(
                f"/api/v1/commercial-operations/{operation_id}/production-closed-loop/next-action/audit-records",
                headers=headers,
            )
            assert stale_action_audits.status_code == 200
            stale_action_audits_body = stale_action_audits.json()
            assert stale_action_audits_body["primary_step"]["step_key"] == "bind"
            assert stale_action_audits_body["primary_step_staleness"]["step_key"] == "bind"
            assert stale_action_audits_body["primary_step_staleness"]["status"] == "stale"
            assert stale_action_audits_body["primary_step_staleness"]["waiting_seconds"] >= 14400
            assert stale_action_audits_body["primary_step_staleness"]["escalation_recommended"] is True

            stale_operation_list = await client.get("/api/v1/commercial-operations", headers=headers)
            assert stale_operation_list.status_code == 200
            stale_operation_item = next(
                item for item in stale_operation_list.json()["items"] if item["id"] == operation_id
            )
            assert stale_operation_item["production_closed_loop_primary_step_key"] == "bind"
            assert stale_operation_item["production_closed_loop_staleness_status"] == "stale"
            assert stale_operation_item["production_closed_loop_waiting_seconds"] >= 14400
            assert stale_operation_item["production_closed_loop_escalation_recommended"] is True
            assert (
                stale_operation_item["production_closed_loop_action_audit_summary"]["primary_step_staleness_contract"]
                == "production_closed_loop_action_audit_primary_step_staleness"
            )

            intervention_queue = await client.get(
                "/api/v1/commercial-operations/production-closed-loop/intervention-queue",
                headers=headers,
            )
            assert intervention_queue.status_code == 200
            intervention_queue_body = intervention_queue.json()
            assert intervention_queue_body["workspace_id"] == "workspace-operation-project"
            assert intervention_queue_body["queue_status"] == "requires_operator_intervention"
            assert intervention_queue_body["queue_count"] >= 1
            assert intervention_queue_body["stale_count"] >= 1
            assert intervention_queue_body["metadata"]["contract"] == "production_closed_loop_intervention_queue"
            assert intervention_queue_body["metadata"]["server_side_external_execution"] is False
            assert (
                intervention_queue_body["queue_summary"]["contract"]
                == "production_closed_loop_intervention_queue_summary"
            )
            assert intervention_queue_body["queue_summary"]["phase"] == "69S"
            assert intervention_queue_body["acknowledgement_sla_status_counts"]["unassigned"] >= 1
            assert intervention_queue_body["reminder_dispatch_status_counts"]["none"] >= 1
            assert intervention_queue_body["reminder_cooldown_status_counts"]["not_dispatched"] >= 1
            assert intervention_queue_body["acknowledgement_overdue_count"] >= 1
            assert intervention_queue_body["reminder_follow_up_count"] >= 1
            assert (
                intervention_queue_body["recommended_action"]["contract"]
                == "production_closed_loop_intervention_queue_recommended_action"
            )
            assert intervention_queue_body["recommended_action"]["action_key"] == "acknowledge_intervention_queue_item"
            assert intervention_queue_body["recommended_action"]["operation_id"] == operation_id
            assert intervention_queue_body["recommended_action"]["server_side_external_execution"] is False
            assert "does_not_run_openclaw_or_playwright_on_server" in intervention_queue_body["boundaries"]
            stale_queue_item = next(
                item for item in intervention_queue_body["items"] if item["operation_id"] == operation_id
            )
            assert stale_queue_item["staleness_status"] == "stale"
            assert stale_queue_item["primary_step_key"] == "bind"
            assert stale_queue_item["waiting_seconds"] >= 14400
            assert stale_queue_item["priority_score"] >= 2000
            assert stale_queue_item["recommended_action_key"] == "bind_production_closed_loop_action_result"
            assert stale_queue_item["operation"]["production_closed_loop_primary_step_key"] == "bind"
            assert (
                stale_queue_item["action_audit_summary"]["primary_step_staleness_contract"]
                == "production_closed_loop_action_audit_primary_step_staleness"
            )

            intervention_agent_skill = await client.get(
                f"/api/v1/commercial-operations/{operation_id}/agent-skill-orchestration",
                headers=headers,
            )
            assert intervention_agent_skill.status_code == 200
            intervention_agent_skill_body = intervention_agent_skill.json()
            assert (
                intervention_agent_skill_body["production_intervention_queue"]["contract"]
                == "production_closed_loop_intervention_main_agent_input"
            )
            assert intervention_agent_skill_body["production_intervention_queue"]["operation_in_queue"] is True
            assert (
                intervention_agent_skill_body["production_intervention_queue"]["recommended_action"]["contract"]
                == "production_closed_loop_intervention_queue_recommended_action"
            )
            assert intervention_agent_skill_body["routing_decision"]["recommended_track"] == "production_intervention"
            assert intervention_agent_skill_body["routing_decision"]["production_intervention_required"] is True
            assert (
                intervention_agent_skill_body["routing_decision"]["production_intervention_recommended_action"]["action_key"]
                == "acknowledge_intervention_queue_item"
            )
            assert (
                intervention_agent_skill_body["routing_decision"]["next_executable_contract"]["track"]
                == "production_intervention"
            )
            assert (
                intervention_agent_skill_body["production_delivery_plan"]["contract"]
                == "production_closed_loop_delivery_plan_main_agent_input"
            )
            assert (
                intervention_agent_skill_body["production_delivery_plan"]["source_contract"]
                == "production_closed_loop_delivery_plan"
            )
            assert intervention_agent_skill_body["routing_decision"]["production_delivery_recommended_gate"]["gate_key"]
            assert (
                intervention_agent_skill_body["routing_decision"]["next_executable_contract"]["parameters"][
                    "production_delivery_recommended_gate"
                ]["gate_key"]
                == intervention_agent_skill_body["routing_decision"]["production_delivery_recommended_gate"]["gate_key"]
            )
            assert any(
                item.startswith("production_delivery_gate=")
                for item in intervention_agent_skill_body["routing_decision"]["evidence"]
            )
            assert any(
                decision["decision_key"] == "production_intervention_recommended_action"
                for decision in intervention_agent_skill_body["decisions"]
            )
            assert any(
                decision["decision_key"] == "production_delivery_plan_recommended_gate"
                for decision in intervention_agent_skill_body["decisions"]
            )
            assert "does_not_run_openclaw_or_playwright_on_server" in intervention_agent_skill_body["production_intervention_queue"]["boundaries"]
            assert "does_not_run_openclaw_or_playwright_on_server" in intervention_agent_skill_body["production_delivery_plan"]["boundaries"]

            intervention_acknowledgement = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/production-closed-loop/intervention-queue/acknowledgements",
                headers=headers,
                json={
                    "acknowledgement_status": "assigned",
                    "assignee": "server-maintainer",
                    "operator_confirmed": True,
                    "acknowledgement_notes": "Maintainer accepted ownership of the stale queue item.",
                    "metadata": {"test": "phase_69o"},
                },
            )
            assert intervention_acknowledgement.status_code == 201
            intervention_acknowledgement_body = intervention_acknowledgement.json()
            assert intervention_acknowledgement_body["operation_id"] == operation_id
            assert intervention_acknowledgement_body["acknowledgement_status"] == "assigned"
            assert intervention_acknowledgement_body["assignee"] == "server-maintainer"
            assert intervention_acknowledgement_body["primary_step_key"] == "bind"
            assert intervention_acknowledgement_body["staleness_status"] == "stale"
            assert intervention_acknowledgement_body["waiting_seconds"] >= 14400
            assert intervention_acknowledgement_body["metadata"]["contract"] == "production_closed_loop_intervention_acknowledgement"
            assert intervention_acknowledgement_body["metadata"]["server_side_external_execution"] is False
            assert "does_not_run_openclaw_or_playwright_on_server" in intervention_acknowledgement_body["boundaries"]

            intervention_acknowledgement_list = await client.get(
                f"/api/v1/commercial-operations/{operation_id}/production-closed-loop/intervention-queue/acknowledgements",
                headers=headers,
            )
            assert intervention_acknowledgement_list.status_code == 200
            intervention_acknowledgement_list_body = intervention_acknowledgement_list.json()
            assert intervention_acknowledgement_list_body["acknowledgement_count"] == 1
            assert (
                intervention_acknowledgement_list_body["latest_record"]["acknowledgement_id"]
                == intervention_acknowledgement_body["acknowledgement_id"]
            )
            assert (
                intervention_acknowledgement_list_body["metadata"]["contract"]
                == "production_closed_loop_intervention_acknowledgement_list"
            )

            assigned_intervention_queue = await client.get(
                "/api/v1/commercial-operations/production-closed-loop/intervention-queue",
                headers=headers,
            )
            assert assigned_intervention_queue.status_code == 200
            assigned_queue_item = next(
                item for item in assigned_intervention_queue.json()["items"] if item["operation_id"] == operation_id
            )
            assert assigned_queue_item["acknowledgement_status"] == "assigned"
            assert assigned_queue_item["acknowledgement_assignee"] == "server-maintainer"
            assert (
                assigned_queue_item["latest_intervention_acknowledgement"]["acknowledgement_id"]
                == intervention_acknowledgement_body["acknowledgement_id"]
            )
            assert assigned_queue_item["acknowledgement_sla"]["status"] == "within_sla"
            assert assigned_queue_item["acknowledgement_sla"]["reminder_recommended"] is False

            overdue_acknowledgement_since = (datetime.now(UTC) - timedelta(hours=5)).isoformat()
            async with session_factory() as direct_session:
                operation = await direct_session.get(CommercialOperation, UUID(operation_id))
                assert operation is not None
                operation_metadata = dict(operation.operation_metadata or {})
                acknowledgement_history = [
                    dict(item)
                    for item in operation_metadata.get("production_closed_loop_intervention_acknowledgements", [])
                    if isinstance(item, dict)
                ]
                for item in acknowledgement_history:
                    if item.get("acknowledgement_id") == intervention_acknowledgement_body["acknowledgement_id"]:
                        item["created_at"] = overdue_acknowledgement_since
                        operation_metadata["production_closed_loop_intervention_acknowledgement_latest"] = item
                        break
                operation_metadata["production_closed_loop_intervention_acknowledgements"] = acknowledgement_history
                operation.operation_metadata = operation_metadata
                await direct_session.commit()

            overdue_intervention_queue = await client.get(
                "/api/v1/commercial-operations/production-closed-loop/intervention-queue",
                headers=headers,
            )
            assert overdue_intervention_queue.status_code == 200
            overdue_queue_item = next(
                item for item in overdue_intervention_queue.json()["items"] if item["operation_id"] == operation_id
            )
            assert overdue_queue_item["acknowledgement_sla"]["status"] == "overdue"
            assert overdue_queue_item["acknowledgement_sla"]["waiting_seconds"] >= 14400
            assert overdue_queue_item["acknowledgement_sla"]["reminder_recommended"] is True
            assert (
                overdue_queue_item["acknowledgement_sla"]["contract"]
                == "production_closed_loop_intervention_acknowledgement_sla"
            )

            reminder_dispatch = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/production-closed-loop/intervention-queue/reminder-dispatches",
                headers=headers,
                json={
                    "reminder_status": "ready_for_review",
                    "reminder_channel": "internal",
                    "reminder_recipient": "server-maintainer",
                    "reminder_message": "Reminder dispatch record for overdue intervention.",
                    "operator_confirmed": True,
                    "dispatch_notes": "No external message sent by the server.",
                    "metadata": {"test": "phase_69q"},
                },
            )
            assert reminder_dispatch.status_code == 201
            reminder_dispatch_body = reminder_dispatch.json()
            assert reminder_dispatch_body["operation_id"] == operation_id
            assert reminder_dispatch_body["reminder_status"] == "ready_for_review"
            assert reminder_dispatch_body["reminder_channel"] == "internal"
            assert reminder_dispatch_body["reminder_recipient"] == "server-maintainer"
            assert reminder_dispatch_body["primary_step_key"] == "bind"
            assert reminder_dispatch_body["acknowledgement_status"] == "assigned"
            assert reminder_dispatch_body["acknowledgement_assignee"] == "server-maintainer"
            assert reminder_dispatch_body["acknowledgement_sla"]["status"] == "overdue"
            assert reminder_dispatch_body["metadata"]["contract"] == "production_closed_loop_intervention_reminder_dispatch"
            assert reminder_dispatch_body["metadata"]["server_side_external_execution"] is False
            assert reminder_dispatch_body["metadata"]["message_sent_by_server"] is False
            assert "record_only_no_message_sent" in reminder_dispatch_body["boundaries"]
            assert "does_not_run_openclaw_or_playwright_on_server" in reminder_dispatch_body["boundaries"]

            reminder_dispatch_list = await client.get(
                f"/api/v1/commercial-operations/{operation_id}/production-closed-loop/intervention-queue/reminder-dispatches",
                headers=headers,
            )
            assert reminder_dispatch_list.status_code == 200
            reminder_dispatch_list_body = reminder_dispatch_list.json()
            assert reminder_dispatch_list_body["reminder_dispatch_count"] == 1
            assert (
                reminder_dispatch_list_body["latest_record"]["reminder_dispatch_id"]
                == reminder_dispatch_body["reminder_dispatch_id"]
            )
            assert (
                reminder_dispatch_list_body["metadata"]["contract"]
                == "production_closed_loop_intervention_reminder_dispatch_list"
            )

            reminded_intervention_queue = await client.get(
                "/api/v1/commercial-operations/production-closed-loop/intervention-queue",
                headers=headers,
            )
            assert reminded_intervention_queue.status_code == 200
            reminded_intervention_queue_body = reminded_intervention_queue.json()
            assert reminded_intervention_queue_body["reminder_dispatch_status_counts"]["ready_for_review"] >= 1
            assert reminded_intervention_queue_body["reminder_cooldown_status_counts"]["cooling_down"] >= 1
            assert reminded_intervention_queue_body["reminder_follow_up_count"] == 0
            assert reminded_intervention_queue_body["recommended_action"]["action_key"] == "wait_for_reminder_cooldown"
            assert (
                reminded_intervention_queue_body["queue_summary"]["recommended_action"]["contract"]
                == "production_closed_loop_intervention_queue_recommended_action"
            )
            reminded_queue_item = next(
                item for item in reminded_intervention_queue_body["items"] if item["operation_id"] == operation_id
            )
            assert reminded_queue_item["reminder_dispatch_status"] == "ready_for_review"
            assert reminded_queue_item["reminder_dispatch_channel"] == "internal"
            assert (
                reminded_queue_item["latest_intervention_reminder_dispatch"]["reminder_dispatch_id"]
                == reminder_dispatch_body["reminder_dispatch_id"]
            )
            assert (
                reminded_queue_item["reminder_dispatch_cooldown"]["contract"]
                == "production_closed_loop_intervention_reminder_dispatch_cooldown"
            )
            assert reminded_queue_item["reminder_dispatch_cooldown"]["status"] == "cooling_down"
            assert reminded_queue_item["reminder_dispatch_cooldown"]["next_reminder_allowed"] is False
            assert reminded_queue_item["reminder_dispatch_cooldown"]["follow_up_recommended"] is False
            assert reminded_queue_item["reminder_follow_up_recommended"] is False
            assert reminded_queue_item["reminder_next_allowed_at"] is not None

            duplicate_reminder_dispatch = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/production-closed-loop/intervention-queue/reminder-dispatches",
                headers=headers,
                json={
                    "reminder_status": "ready_for_review",
                    "reminder_channel": "internal",
                    "reminder_recipient": "server-maintainer",
                    "reminder_message": "Duplicate reminder dispatch record.",
                    "operator_confirmed": True,
                    "dispatch_notes": "This should be blocked by reminder cooldown.",
                    "metadata": {"test": "phase_69r_duplicate"},
                },
            )
            assert duplicate_reminder_dispatch.status_code == 400
            assert "cooldown" in duplicate_reminder_dispatch.text.lower()

            routed_reminder_dispatch = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/production-closed-loop/intervention-queue/reminder-dispatches",
                headers=headers,
                json={
                    "reminder_status": "routed_to_operator",
                    "reminder_channel": "internal",
                    "reminder_recipient": "server-maintainer",
                    "reminder_message": "Reminder routed to the responsible operator.",
                    "operator_confirmed": True,
                    "dispatch_notes": "Lifecycle progression is allowed inside cooldown; no message sent by server.",
                    "metadata": {"test": "phase_69r_progression"},
                },
            )
            assert routed_reminder_dispatch.status_code == 201
            routed_reminder_dispatch_body = routed_reminder_dispatch.json()
            assert routed_reminder_dispatch_body["reminder_status"] == "routed_to_operator"
            assert (
                routed_reminder_dispatch_body["reminder_dispatch_cooldown_before"]["status"]
                == "cooling_down"
            )
            assert routed_reminder_dispatch_body["metadata"]["contract"] == "production_closed_loop_intervention_reminder_dispatch"

            result_record_id = str(uuid4())
            production_action_result_binding = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/production-closed-loop/next-action/audit-records/{action_audit_body['audit_id']}/result-binding",
                headers=headers,
                json={
                    "binding_status": "result_recorded",
                    "result_record_type": "OptimizationDecision",
                    "result_record_id": result_record_id,
                    "result_status": "draft_or_ready_for_review",
                    "result_endpoint": f"{next_action_body['selected_action']['endpoint']}/{result_record_id}",
                    "evidence_summary": "Operator linked the returned optimization decision ID.",
                    "operator_confirmed": True,
                    "binding_notes": "Metadata-only binding after the guarded target endpoint completed.",
                    "metadata": {"test": "phase_68z2"},
                },
            )
            assert production_action_result_binding.status_code == 201
            result_binding_body = production_action_result_binding.json()
            assert result_binding_body["operation_id"] == operation_id
            assert result_binding_body["audit_id"] == action_audit_body["audit_id"]
            assert result_binding_body["binding_status"] == "result_recorded"
            assert result_binding_body["result_record_type"] == "OptimizationDecision"
            assert result_binding_body["result_record_id"] == result_record_id
            assert result_binding_body["metadata"]["contract"] == "production_closed_loop_action_result_binding"
            assert result_binding_body["metadata"]["server_side_external_execution"] is False
            assert result_binding_body["audit_record"]["result_binding_status"] == "result_recorded"
            assert "does_not_execute_target_endpoint" in result_binding_body["boundaries"]

            result_bound_action_audits = await client.get(
                f"/api/v1/commercial-operations/{operation_id}/production-closed-loop/next-action/audit-records",
                headers=headers,
            )
            assert result_bound_action_audits.status_code == 200
            result_bound_audits_body = result_bound_action_audits.json()
            assert result_bound_audits_body["latest_record"]["result_binding_status"] == "result_recorded"
            assert result_bound_audits_body["latest_record"]["result_record_id"] == result_record_id
            assert result_bound_audits_body["evidence_coverage"]["records_with_result_binding"] >= 2
            assert [item["status"] for item in result_bound_audits_body["operator_checklist"]] == [
                "done",
                "done",
                "next",
                "blocked",
            ]
            assert result_bound_audits_body["primary_step"]["step_key"] == "validate"
            assert result_bound_audits_body["primary_step_staleness"]["step_key"] == "validate"
            assert result_bound_audits_body["primary_step_staleness"]["status"] == "fresh"
            assert result_bound_audits_body["metadata"]["result_binding_contract"] == "production_closed_loop_action_result_binding"

            production_action_record_validation = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/production-closed-loop/next-action/audit-records/{action_audit_body['audit_id']}/result-binding/record-validation",
                headers=headers,
                json={
                    "operator_confirmed": True,
                    "validation_notes": "Validate the bound OptimizationDecision ID before readiness refresh.",
                    "metadata": {"test": "phase_68z4"},
                },
            )
            assert production_action_record_validation.status_code == 200
            record_validation_body = production_action_record_validation.json()
            assert record_validation_body["operation_id"] == operation_id
            assert record_validation_body["audit_id"] == action_audit_body["audit_id"]
            assert record_validation_body["validation_status"] == "record_missing"
            assert record_validation_body["result_record_type"] == "OptimizationDecision"
            assert record_validation_body["result_record_id"] == result_record_id
            assert record_validation_body["record_exists"] is False
            assert record_validation_body["metadata"]["contract"] == "production_closed_loop_action_result_record_validation"
            assert record_validation_body["metadata"]["server_side_external_execution"] is False
            assert record_validation_body["audit_record"]["result_record_validation_status"] == "record_missing"
            assert "OptimizationDecision" in record_validation_body["supported_record_types"]
            assert "does_not_mutate_the_bound_business_record" in record_validation_body["boundaries"]

            record_validated_action_audits = await client.get(
                f"/api/v1/commercial-operations/{operation_id}/production-closed-loop/next-action/audit-records",
                headers=headers,
            )
            assert record_validated_action_audits.status_code == 200
            record_validated_action_audits_body = record_validated_action_audits.json()
            assert record_validated_action_audits_body["latest_record"]["result_record_validation_status"] == "record_missing"
            assert record_validated_action_audits_body["evidence_coverage"]["records_with_result_record_validation"] >= 2
            assert [item["status"] for item in record_validated_action_audits_body["operator_checklist"]] == [
                "done",
                "done",
                "blocked",
                "blocked",
            ]
            assert record_validated_action_audits_body["primary_step"] is None
            assert record_validated_action_audits_body["primary_step_staleness"]["status"] == "none"
            assert (
                record_validated_action_audits_body["metadata"]["result_record_validation_contract"]
                == "production_closed_loop_action_result_record_validation"
            )

            production_action_readiness_refresh = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/production-closed-loop/next-action/audit-records/{action_audit_body['audit_id']}/result-binding/readiness-refresh",
                headers=headers,
                json={
                    "platform": "douyin",
                    "force_metric_due": True,
                    "operator_confirmed": True,
                    "refresh_notes": "Refresh after linking the optimization decision result id.",
                    "metadata": {"test": "phase_68z3"},
                },
            )
            assert production_action_readiness_refresh.status_code == 200
            readiness_refresh_body = production_action_readiness_refresh.json()
            assert readiness_refresh_body["operation_id"] == operation_id
            assert readiness_refresh_body["audit_id"] == action_audit_body["audit_id"]
            assert readiness_refresh_body["refresh_status"] == "record_validation_blocked"
            assert readiness_refresh_body["underlying_refresh_status"] == "same_stage_requires_project_record_completion"
            assert readiness_refresh_body["record_validation_gate_status"] == "record_validation_blocked"
            assert readiness_refresh_body["record_validation_required"] is True
            assert readiness_refresh_body["record_validation_passed"] is False
            assert readiness_refresh_body["result_record_validation_status"] == "record_missing"
            assert "bound result record does not exist" in " ".join(
                readiness_refresh_body["record_validation_blocking_reasons"]
            )
            assert readiness_refresh_body["audit_stage_key"] == "analysis_improvement"
            assert readiness_refresh_body["current_stage_key"] == "analysis_improvement"
            assert readiness_refresh_body["stage_completed_after_binding"] is False
            assert readiness_refresh_body["next_action_key"] == "create_or_review_optimization_decision"
            assert readiness_refresh_body["metadata"]["contract"] == "production_closed_loop_action_result_readiness_refresh"
            assert readiness_refresh_body["metadata"]["server_side_external_execution"] is False
            assert readiness_refresh_body["readiness"]["metadata"]["contract"] == "production_closed_loop_e2e_readiness"
            assert readiness_refresh_body["next_action"]["metadata"]["contract"] == "production_closed_loop_next_action"
            assert readiness_refresh_body["metadata"]["phase"] == "68Z5"
            assert readiness_refresh_body["metadata"]["gate_contract"] == "production_closed_loop_action_result_record_validation_gate"
            assert readiness_refresh_body["audit_record"]["readiness_refresh_status"] == "record_validation_blocked"
            assert "does_not_execute_target_endpoint_or_next_action" in readiness_refresh_body["boundaries"]
            assert "verified_result_record_required_before_progress_refresh" in readiness_refresh_body["boundaries"]

            refreshed_action_audits = await client.get(
                f"/api/v1/commercial-operations/{operation_id}/production-closed-loop/next-action/audit-records",
                headers=headers,
            )
            assert refreshed_action_audits.status_code == 200
            refreshed_action_audits_body = refreshed_action_audits.json()
            assert refreshed_action_audits_body["latest_record"]["readiness_refresh_status"] == "record_validation_blocked"
            assert refreshed_action_audits_body["evidence_coverage"]["records_with_readiness_refresh"] == 1
            assert [item["status"] for item in refreshed_action_audits_body["operator_checklist"]] == [
                "done",
                "done",
                "blocked",
                "blocked",
            ]
            assert refreshed_action_audits_body["primary_step"] is None
            assert refreshed_action_audits_body["metadata"]["readiness_refresh_contract"] == "production_closed_loop_action_result_readiness_refresh"

            verified_content_draft_id = uuid4()
            verified_deliverable_id = uuid4()
            verified_execution_request_id = uuid4()
            verified_execution_run_id = uuid4()
            verified_result_id = uuid4()
            verified_observation_id = uuid4()
            verified_decision_id = uuid4()
            verified_chain_now = datetime.now(UTC)
            async with session_factory() as direct_session:
                direct_session.add_all(
                    [
                        CommercialOperationContentDraft(
                            id=verified_content_draft_id,
                            workspace_id="workspace-operation-project",
                            operation_id=UUID(operation_id),
                            step_key="analysis_improvement",
                            channel="douyin",
                            content_format="post",
                            title="Approved next-cycle content draft",
                            draft_status="approved",
                            content_body="Use metric feedback to prepare a reviewed next-cycle short-video iteration.",
                            summary="Approved support record for the Phase 68Z6 verified decision chain.",
                            source_materials=[],
                            asset_requests=[],
                            content_metadata={"test": "phase_68z6_verified_record_chain"},
                            created_by="operator-1",
                            updated_by="operator-1",
                            approved_by="operator-1",
                            approved_at=verified_chain_now,
                        ),
                        CommercialOperationDeliverable(
                            id=verified_deliverable_id,
                            workspace_id="workspace-operation-project",
                            operation_id=UUID(operation_id),
                            content_draft_id=verified_content_draft_id,
                            output_artifact_id=None,
                            step_key="analysis_improvement",
                            channel="douyin",
                            deliverable_type="content_package",
                            title="Packaged next-cycle deliverable",
                            deliverable_status="packaged",
                            summary="Packaged support record for the Phase 68Z6 verified decision chain.",
                            asset_request_ids=[],
                            quality_checks=["reviewed_chain_fixture"],
                            package_payload={"source": "phase_68z6_verified_record_chain"},
                            deliverable_metadata={"test": "phase_68z6_verified_record_chain"},
                            created_by="operator-1",
                            updated_by="operator-1",
                            approved_by="operator-1",
                            packaged_by="operator-1",
                            approved_at=verified_chain_now,
                            packaged_at=verified_chain_now,
                        ),
                        CommercialOperationExecutionRequest(
                            id=verified_execution_request_id,
                            workspace_id="workspace-operation-project",
                            operation_id=UUID(operation_id),
                            deliverable_id=verified_deliverable_id,
                            output_artifact_id=None,
                            step_key="analysis_improvement",
                            channel="douyin",
                            execution_type="manual_handoff",
                            execution_mode="metadata_only",
                            title="Prepared next-cycle execution request",
                            request_status="prepared",
                            runbook=[],
                            readiness_checks=["reviewed_chain_fixture"],
                            expected_outputs=["operator_reviewed_optimization_decision"],
                            evidence_snapshot_ids=[],
                            operator_checklist=[],
                            handoff_payload={"source": "phase_68z6_verified_record_chain"},
                            execution_metadata={"test": "phase_68z6_verified_record_chain"},
                            requested_by="operator-1",
                            updated_by="operator-1",
                            approved_by="operator-1",
                            prepared_by="operator-1",
                            approved_at=verified_chain_now,
                            prepared_at=verified_chain_now,
                        ),
                        CommercialOperationExecutionRun(
                            id=verified_execution_run_id,
                            workspace_id="workspace-operation-project",
                            operation_id=UUID(operation_id),
                            execution_request_id=verified_execution_request_id,
                            deliverable_id=verified_deliverable_id,
                            output_artifact_id=None,
                            step_key="analysis_improvement",
                            channel="douyin",
                            execution_type="manual_handoff",
                            execution_mode="metadata_only",
                            title="Succeeded next-cycle execution run",
                            run_status="succeeded",
                            input_payload={"source": "phase_68z6_verified_record_chain"},
                            runbook_snapshot=[],
                            readiness_checks=["reviewed_chain_fixture"],
                            expected_outputs=["operator_reviewed_optimization_decision"],
                            evidence_snapshot_ids=[],
                            operator_checklist_snapshot=[],
                            runtime_payload={},
                            result_payload={"summary": "Fixture run succeeded for the verified decision chain."},
                            recovery_plan={},
                            run_metadata={"test": "phase_68z6_verified_record_chain"},
                            queued_by="operator-1",
                            started_by="operator-1",
                            completed_by="operator-1",
                            queued_at=verified_chain_now,
                            started_at=verified_chain_now,
                            completed_at=verified_chain_now,
                        ),
                        CommercialOperationResult(
                            id=verified_result_id,
                            workspace_id="workspace-operation-project",
                            operation_id=UUID(operation_id),
                            execution_run_id=verified_execution_run_id,
                            execution_request_id=verified_execution_request_id,
                            deliverable_id=verified_deliverable_id,
                            output_artifact_id=None,
                            step_key="analysis_improvement",
                            channel="douyin",
                            result_type="operator_report",
                            title="Approved next-cycle result report",
                            result_status="approved",
                            summary="Approved result support record for the Phase 68Z6 verified decision chain.",
                            outcome_summary="Metric feedback is ready for optimization decision review.",
                            observed_metrics=[],
                            commercial_signals=["reviewed_chain_fixture"],
                            evidence_links=[],
                            follow_up_actions=["approve optimization decision"],
                            result_payload={"source": "phase_68z6_verified_record_chain"},
                            recommendation_payload={},
                            result_metadata={"test": "phase_68z6_verified_record_chain"},
                            created_by="operator-1",
                            updated_by="operator-1",
                            approved_by="operator-1",
                            approved_at=verified_chain_now,
                        ),
                        CommercialOperationMonitoringObservation(
                            id=verified_observation_id,
                            workspace_id="workspace-operation-project",
                            operation_id=UUID(operation_id),
                            result_id=verified_result_id,
                            execution_run_id=verified_execution_run_id,
                            execution_request_id=verified_execution_request_id,
                            deliverable_id=verified_deliverable_id,
                            output_artifact_id=None,
                            step_key="analysis_improvement",
                            channel="douyin",
                            observation_type="manual_snapshot",
                            title="Approved next-cycle monitoring observation",
                            observation_status="approved",
                            metric_snapshots=[],
                            qualitative_signals=["reviewed_chain_fixture"],
                            evidence_links=[],
                            anomaly_flags=[],
                            recommended_actions=["approve optimization decision"],
                            observation_payload={"source": "phase_68z6_verified_record_chain"},
                            observation_metadata={"test": "phase_68z6_verified_record_chain"},
                            created_by="operator-1",
                            updated_by="operator-1",
                            approved_by="operator-1",
                            approved_at=verified_chain_now,
                        ),
                        CommercialOperationOptimizationDecision(
                            id=verified_decision_id,
                            workspace_id="workspace-operation-project",
                            operation_id=UUID(operation_id),
                            observation_id=verified_observation_id,
                            result_id=verified_result_id,
                            execution_run_id=verified_execution_run_id,
                            execution_request_id=verified_execution_request_id,
                            deliverable_id=verified_deliverable_id,
                            output_artifact_id=None,
                            step_key="analysis_improvement",
                            channel="douyin",
                            decision_type="iterate",
                            title="Verified optimization decision for next cycle",
                            decision_status="draft",
                            priority="normal",
                            rationale="Use approved metric feedback to prepare the next operating iteration.",
                            objective_updates=["Keep the weekend booking objective and improve video hook density."],
                            content_actions=["Prepare a new reviewed short-video iteration."],
                            asset_actions=["Reuse the selected scene and improve the standing singer first frame."],
                            audience_actions=["Keep Douyin KTV weekend audience targeting."],
                            execution_actions=["Return to customer-machine publish handoff after approval."],
                            risk_controls=["Human approval remains required before production or publishing."],
                            decision_payload={"source": "phase_68z6_verified_record_gate_pass"},
                            decision_metadata={"test": "phase_68z6"},
                            created_by="operator-1",
                            updated_by="operator-1",
                        ),
                    ]
                )
                await direct_session.commit()

            verified_result_binding = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/production-closed-loop/next-action/audit-records/{action_audit_body['audit_id']}/result-binding",
                headers=headers,
                json={
                    "binding_status": "result_recorded",
                    "result_record_type": "OptimizationDecision",
                    "result_record_id": str(verified_decision_id),
                    "result_status": "draft_or_ready_for_review",
                    "result_endpoint": f"{next_action_body['selected_action']['endpoint']}/{verified_decision_id}",
                    "evidence_summary": "Operator linked the real optimization decision record created by the target endpoint.",
                    "operator_confirmed": True,
                    "binding_notes": "Phase 68Z6 verifies the positive record-validation pass path.",
                    "metadata": {"test": "phase_68z6"},
                },
            )
            assert verified_result_binding.status_code == 201
            verified_result_binding_body = verified_result_binding.json()
            assert verified_result_binding_body["result_record_id"] == str(verified_decision_id)
            assert verified_result_binding_body["audit_record"]["result_binding_status"] == "result_recorded"

            verified_record_validation = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/production-closed-loop/next-action/audit-records/{action_audit_body['audit_id']}/result-binding/record-validation",
                headers=headers,
                json={
                    "operator_confirmed": True,
                    "validation_notes": "Validate the real OptimizationDecision before readiness refresh.",
                    "metadata": {"test": "phase_68z6"},
                },
            )
            assert verified_record_validation.status_code == 200
            verified_record_validation_body = verified_record_validation.json()
            assert verified_record_validation_body["validation_status"] == "record_verified"
            assert verified_record_validation_body["result_record_id"] == str(verified_decision_id)
            assert verified_record_validation_body["record_exists"] is True
            assert verified_record_validation_body["workspace_matches"] is True
            assert verified_record_validation_body["operation_matches"] is True
            assert verified_record_validation_body["status_matches"] is True
            assert verified_record_validation_body["status_field"] == "decision_status"
            assert verified_record_validation_body["record_status"] == "draft"
            assert verified_record_validation_body["expected_statuses"] == ["draft", "ready_for_review"]
            assert verified_record_validation_body["record_summary"]["record_type"] == "OptimizationDecision"
            assert verified_record_validation_body["record_summary"]["title"] == "Verified optimization decision for next cycle"
            assert verified_record_validation_body["audit_record"]["result_record_validation_status"] == "record_verified"

            verified_validated_action_audits = await client.get(
                f"/api/v1/commercial-operations/{operation_id}/production-closed-loop/next-action/audit-records",
                headers=headers,
            )
            assert verified_validated_action_audits.status_code == 200
            verified_validated_action_audits_body = verified_validated_action_audits.json()
            assert verified_validated_action_audits_body["latest_record"]["result_record_validation_status"] == "record_verified"
            assert [item["status"] for item in verified_validated_action_audits_body["operator_checklist"]] == [
                "done",
                "done",
                "done",
                "next",
            ]
            assert verified_validated_action_audits_body["primary_step"]["step_key"] == "refresh"
            assert verified_validated_action_audits_body["primary_step_staleness"]["step_key"] == "refresh"
            assert verified_validated_action_audits_body["primary_step_staleness"]["status"] == "fresh"

            verified_readiness_refresh = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/production-closed-loop/next-action/audit-records/{action_audit_body['audit_id']}/result-binding/readiness-refresh",
                headers=headers,
                json={
                    "platform": "douyin",
                    "force_metric_due": True,
                    "operator_confirmed": True,
                    "refresh_notes": "Refresh after validating the real optimization decision record.",
                    "metadata": {"test": "phase_68z6"},
                },
            )
            assert verified_readiness_refresh.status_code == 200
            verified_readiness_refresh_body = verified_readiness_refresh.json()
            assert verified_readiness_refresh_body["refresh_status"] == verified_readiness_refresh_body["underlying_refresh_status"]
            assert verified_readiness_refresh_body["underlying_refresh_status"] == "same_stage_requires_project_record_completion"
            assert verified_readiness_refresh_body["record_validation_gate_status"] == "record_validation_passed"
            assert verified_readiness_refresh_body["record_validation_required"] is False
            assert verified_readiness_refresh_body["record_validation_passed"] is True
            assert verified_readiness_refresh_body["record_validation_blocking_reasons"] == []
            assert verified_readiness_refresh_body["result_record_validation_status"] == "record_verified"
            assert verified_readiness_refresh_body["result_record_validation"]["record_summary"]["id"] == str(verified_decision_id)
            assert verified_readiness_refresh_body["stage_completed_after_binding"] is False
            assert verified_readiness_refresh_body["next_action_key"] == "mark_optimization_decision_ready"
            assert verified_readiness_refresh_body["next_action"]["selected_action"]["endpoint"].endswith(
                f"/optimization-decisions/{verified_decision_id}/ready"
            )
            assert verified_readiness_refresh_body["next_action"]["selected_action"]["expected_result"][
                "decision_status"
            ] == "ready_for_review"
            assert verified_readiness_refresh_body["metadata"]["phase"] == "68Z5"
            assert verified_readiness_refresh_body["metadata"]["gate_contract"] == "production_closed_loop_action_result_record_validation_gate"
            assert verified_readiness_refresh_body["audit_record"]["readiness_refresh_status"] == "same_stage_requires_project_record_completion"
            assert "verified_result_record_required_before_progress_refresh" in verified_readiness_refresh_body["boundaries"]

            verified_refreshed_action_audits = await client.get(
                f"/api/v1/commercial-operations/{operation_id}/production-closed-loop/next-action/audit-records",
                headers=headers,
            )
            assert verified_refreshed_action_audits.status_code == 200
            verified_refreshed_action_audits_body = verified_refreshed_action_audits.json()
            assert verified_refreshed_action_audits_body["latest_record"]["result_record_id"] == str(verified_decision_id)
            assert verified_refreshed_action_audits_body["latest_record"]["result_record_validation_status"] == "record_verified"
            assert (
                verified_refreshed_action_audits_body["latest_record"]["readiness_refresh_status"]
                == "same_stage_requires_project_record_completion"
            )
            assert verified_refreshed_action_audits_body["evidence_coverage"]["records_with_result_binding"] >= 2
            assert verified_refreshed_action_audits_body["evidence_coverage"]["records_with_result_record_validation"] >= 2
            assert verified_refreshed_action_audits_body["evidence_coverage"]["records_with_readiness_refresh"] == 1
            assert [item["status"] for item in verified_refreshed_action_audits_body["operator_checklist"]] == [
                "done",
                "done",
                "done",
                "done",
            ]
            assert verified_refreshed_action_audits_body["primary_step"] is None
            assert verified_refreshed_action_audits_body["primary_step_staleness"]["status"] == "none"

            ready_next_action = verified_readiness_refresh_body["next_action"]["selected_action"]
            ready_action_audit = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/production-closed-loop/next-action/audit-records?platform=douyin&force_metric_due=true",
                headers=headers,
                json={
                    "action_key": ready_next_action["action_key"],
                    "stage_key": ready_next_action["stage_key"],
                    "action_status": "confirmed",
                    "operator_confirmed": True,
                    "target_method": ready_next_action["method"],
                    "target_endpoint": ready_next_action["endpoint"],
                    "submitted_payload": {"metadata": {"source": "phase_68z7_ready_action_audit"}},
                    "execution_summary": "Operator confirmed the optimization decision ready action.",
                    "boundary_checks": ["no_server_side_external_execution", "operator_approval_boundary_preserved"],
                    "metadata": {"test": "phase_68z7_ready"},
                },
            )
            assert ready_action_audit.status_code == 201
            ready_action_audit_body = ready_action_audit.json()
            assert ready_action_audit_body["action_key"] == "mark_optimization_decision_ready"
            assert ready_action_audit_body["contract_snapshot"]["action"]["expected_result"]["record_type"] == "OptimizationDecision"
            assert (
                ready_action_audit_body["contract_snapshot"]["action"]["expected_result"]["decision_status"]
                == "ready_for_review"
            )

            ready_decision = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/optimization-decisions/{verified_decision_id}/ready",
                headers=headers,
                json={"reviewer_notes": "Decision reviewed and ready for approval."},
            )
            assert ready_decision.status_code == 200
            assert ready_decision.json()["decision_status"] == "ready_for_review"

            ready_result_binding = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/production-closed-loop/next-action/audit-records/{ready_action_audit_body['audit_id']}/result-binding",
                headers=headers,
                json={
                    "binding_status": "result_recorded",
                    "result_record_type": "OptimizationDecision",
                    "result_record_id": str(verified_decision_id),
                    "result_status": "ready_for_review",
                    "result_endpoint": ready_next_action["endpoint"],
                    "evidence_summary": "Operator linked the ready optimization decision record.",
                    "operator_confirmed": True,
                    "binding_notes": "Phase 68Z7 records the ready-for-review transition.",
                    "metadata": {"test": "phase_68z7_ready"},
                },
            )
            assert ready_result_binding.status_code == 201
            ready_record_validation = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/production-closed-loop/next-action/audit-records/{ready_action_audit_body['audit_id']}/result-binding/record-validation",
                headers=headers,
                json={
                    "operator_confirmed": True,
                    "validation_notes": "Validate the ready_for_review OptimizationDecision before approval.",
                    "metadata": {"test": "phase_68z7_ready"},
                },
            )
            assert ready_record_validation.status_code == 200
            ready_record_validation_body = ready_record_validation.json()
            assert ready_record_validation_body["validation_status"] == "record_verified"
            assert ready_record_validation_body["record_status"] == "ready_for_review"
            assert ready_record_validation_body["expected_statuses"] == ["ready_for_review"]

            ready_readiness_refresh = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/production-closed-loop/next-action/audit-records/{ready_action_audit_body['audit_id']}/result-binding/readiness-refresh",
                headers=headers,
                json={
                    "platform": "douyin",
                    "force_metric_due": True,
                    "operator_confirmed": True,
                    "refresh_notes": "Refresh after marking the optimization decision ready.",
                    "metadata": {"test": "phase_68z7_ready"},
                },
            )
            assert ready_readiness_refresh.status_code == 200
            ready_readiness_refresh_body = ready_readiness_refresh.json()
            assert ready_readiness_refresh_body["record_validation_gate_status"] == "record_validation_passed"
            assert ready_readiness_refresh_body["record_validation_required"] is False
            assert ready_readiness_refresh_body["refresh_status"] == "same_stage_requires_project_record_completion"
            assert ready_readiness_refresh_body["next_action_key"] == "approve_optimization_decision"
            assert ready_readiness_refresh_body["next_action"]["selected_action"]["endpoint"].endswith(
                f"/optimization-decisions/{verified_decision_id}/approve"
            )

            approve_next_action = ready_readiness_refresh_body["next_action"]["selected_action"]
            approve_action_audit = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/production-closed-loop/next-action/audit-records?platform=douyin&force_metric_due=true",
                headers=headers,
                json={
                    "action_key": approve_next_action["action_key"],
                    "stage_key": approve_next_action["stage_key"],
                    "action_status": "confirmed",
                    "operator_confirmed": True,
                    "target_method": approve_next_action["method"],
                    "target_endpoint": approve_next_action["endpoint"],
                    "submitted_payload": {"metadata": {"source": "phase_68z7_approve_action_audit"}},
                    "execution_summary": "Operator confirmed the optimization decision approval action.",
                    "boundary_checks": ["no_server_side_external_execution", "operator_approval_boundary_preserved"],
                    "metadata": {"test": "phase_68z7_approve"},
                },
            )
            assert approve_action_audit.status_code == 201
            approve_action_audit_body = approve_action_audit.json()
            assert approve_action_audit_body["action_key"] == "approve_optimization_decision"
            assert (
                approve_action_audit_body["contract_snapshot"]["action"]["expected_result"]["decision_status"]
                == "approved"
            )

            approved_decision = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/optimization-decisions/{verified_decision_id}/approve",
                headers=headers,
                json={"reviewer_notes": "Approved for the next operation cycle."},
            )
            assert approved_decision.status_code == 200
            assert approved_decision.json()["decision_status"] == "approved"
            assert approved_decision.json()["approved_by"] == "operator-1"

            approved_result_binding = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/production-closed-loop/next-action/audit-records/{approve_action_audit_body['audit_id']}/result-binding",
                headers=headers,
                json={
                    "binding_status": "result_recorded",
                    "result_record_type": "OptimizationDecision",
                    "result_record_id": str(verified_decision_id),
                    "result_status": "approved",
                    "result_endpoint": approve_next_action["endpoint"],
                    "evidence_summary": "Operator linked the approved optimization decision record.",
                    "operator_confirmed": True,
                    "binding_notes": "Phase 68Z7 records the approved decision transition.",
                    "metadata": {"test": "phase_68z7_approve"},
                },
            )
            assert approved_result_binding.status_code == 201
            approved_record_validation = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/production-closed-loop/next-action/audit-records/{approve_action_audit_body['audit_id']}/result-binding/record-validation",
                headers=headers,
                json={
                    "operator_confirmed": True,
                    "validation_notes": "Validate the approved OptimizationDecision before final readiness refresh.",
                    "metadata": {"test": "phase_68z7_approve"},
                },
            )
            assert approved_record_validation.status_code == 200
            approved_record_validation_body = approved_record_validation.json()
            assert approved_record_validation_body["validation_status"] == "record_verified"
            assert approved_record_validation_body["record_status"] == "approved"
            assert approved_record_validation_body["expected_statuses"] == ["approved"]

            approved_readiness_refresh = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/production-closed-loop/next-action/audit-records/{approve_action_audit_body['audit_id']}/result-binding/readiness-refresh",
                headers=headers,
                json={
                    "platform": "douyin",
                    "force_metric_due": True,
                    "operator_confirmed": True,
                    "refresh_notes": "Refresh after approving the optimization decision.",
                    "metadata": {"test": "phase_68z7_approve"},
                },
            )
            assert approved_readiness_refresh.status_code == 200
            approved_readiness_refresh_body = approved_readiness_refresh.json()
            assert approved_readiness_refresh_body["refresh_status"] == "stage_completed"
            assert approved_readiness_refresh_body["underlying_refresh_status"] == "stage_completed"
            assert approved_readiness_refresh_body["record_validation_gate_status"] == "record_validation_passed"
            assert approved_readiness_refresh_body["record_validation_required"] is False
            assert approved_readiness_refresh_body["record_validation_passed"] is True
            assert approved_readiness_refresh_body["stage_completed_after_binding"] is True
            assert approved_readiness_refresh_body["current_stage_key"] is None
            assert approved_readiness_refresh_body["readiness"]["ready_for_next_cycle"] is True
            assert approved_readiness_refresh_body["readiness"]["readiness_status"] == "ready_for_next_cycle"
            assert approved_readiness_refresh_body["next_action_key"] == "prepare_next_approved_operation_cycle"
            next_cycle_action = approved_readiness_refresh_body["next_action"]["selected_action"]
            assert next_cycle_action["method"] == "POST"
            assert next_cycle_action["endpoint"].endswith("/production-closed-loop/next-cycle-draft")
            assert next_cycle_action["payload_template"]["source_decision_id"] == str(verified_decision_id)
            assert next_cycle_action["expected_result"]["record_type"] == "OperationPlan"
            assert next_cycle_action["expected_result"]["plan_status"] == "ready_for_review"
            assert next_cycle_action["expected_result"]["production_task_status"] == "ready_for_review"

            unconfirmed_next_cycle = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/production-closed-loop/next-cycle-draft?platform=douyin&force_metric_due=true",
                headers=headers,
                json={"operator_confirmed": False, "source_decision_id": str(verified_decision_id)},
            )
            assert unconfirmed_next_cycle.status_code == 400
            assert "operator_confirmed" in unconfirmed_next_cycle.text

            next_cycle_draft = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/production-closed-loop/next-cycle-draft?platform=douyin&force_metric_due=true",
                headers=headers,
                json={
                    "operator_confirmed": True,
                    "source_decision_id": str(verified_decision_id),
                    "create_tasks": True,
                    "operator_note": "Prepare Phase 68Z8 next-cycle plan and tasks.",
                    "metadata": {"test": "phase_68z8"},
                },
            )
            assert next_cycle_draft.status_code == 201
            next_cycle_draft_body = next_cycle_draft.json()
            assert next_cycle_draft_body["draft_status"] == "created"
            assert next_cycle_draft_body["source_decision_id"] == str(verified_decision_id)
            assert next_cycle_draft_body["operation_plan"]["plan_status"] == "ready_for_review"
            assert (
                next_cycle_draft_body["operation_plan"]["metadata"]["production_closed_loop_next_cycle"][
                    "source_decision_id"
                ]
                == str(verified_decision_id)
            )
            assert {task["task_status"] for task in next_cycle_draft_body["production_tasks"]} == {
                "ready_for_review"
            }
            assert {task["task_type"] for task in next_cycle_draft_body["production_tasks"]} == {
                "copy",
                "image",
                "media",
            }
            assert next_cycle_draft_body["readiness_status_before"] == "ready_for_next_cycle"
            assert next_cycle_draft_body["next_action_key_before"] == "prepare_next_approved_operation_cycle"
            assert next_cycle_draft_body["metadata"]["phase"] == "68Z8"
            assert "does_not_approve_operation_plan_or_tasks" in next_cycle_draft_body["boundaries"]

            reused_next_cycle_draft = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/production-closed-loop/next-cycle-draft?platform=douyin&force_metric_due=true",
                headers=headers,
                json={
                    "operator_confirmed": True,
                    "source_decision_id": str(verified_decision_id),
                    "create_tasks": True,
                    "metadata": {"test": "phase_68z8_reuse"},
                },
            )
            assert reused_next_cycle_draft.status_code == 201
            reused_next_cycle_body = reused_next_cycle_draft.json()
            assert reused_next_cycle_body["draft_status"] == "reused"
            assert reused_next_cycle_body["operation_plan"]["id"] == next_cycle_draft_body["operation_plan"]["id"]
            assert {
                task["id"] for task in reused_next_cycle_body["production_tasks"]
            } == {task["id"] for task in next_cycle_draft_body["production_tasks"]}

            unconfirmed_readiness_refresh = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/production-closed-loop/next-action/audit-records/{action_audit_body['audit_id']}/result-binding/readiness-refresh",
                headers=headers,
                json={"operator_confirmed": False},
            )
            assert unconfirmed_readiness_refresh.status_code == 400
            assert "operator_confirmed" in unconfirmed_readiness_refresh.text

            unconfirmed_record_validation = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/production-closed-loop/next-action/audit-records/{action_audit_body['audit_id']}/result-binding/record-validation",
                headers=headers,
                json={"operator_confirmed": False},
            )
            assert unconfirmed_record_validation.status_code == 400
            assert "operator_confirmed" in unconfirmed_record_validation.text

            unconfirmed_result_binding = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/production-closed-loop/next-action/audit-records/{action_audit_body['audit_id']}/result-binding",
                headers=headers,
                json={
                    "binding_status": "result_recorded",
                    "result_record_type": "OptimizationDecision",
                    "result_record_id": str(uuid4()),
                    "operator_confirmed": False,
                },
            )
            assert unconfirmed_result_binding.status_code == 400
            assert "operator_confirmed" in unconfirmed_result_binding.text

            unconfirmed_submission = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/production-closed-loop/next-action/audit-records?platform=douyin&force_metric_due=true",
                headers=headers,
                json={
                    "action_key": approved_readiness_refresh_body["next_action_key"],
                    "action_status": "submitted",
                    "operator_confirmed": False,
                },
            )
            assert unconfirmed_submission.status_code == 400
            assert "operator_confirmed" in unconfirmed_submission.text

            sensitive_audit = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/production-closed-loop/next-action/audit-records?platform=douyin&force_metric_due=true",
                headers=headers,
                json={
                    "action_key": approved_readiness_refresh_body["next_action_key"],
                    "action_status": "reviewed",
                    "submitted_payload": {"access_token": "do-not-store"},
                },
            )
            assert sensitive_audit.status_code == 400
            assert "sensitive" in sensitive_audit.text

            approved_plans = await client.get(
                f"/api/v1/commercial-operations/{operation_id}/operation-plans?status=approved",
                headers=headers,
            )
            assert approved_plans.status_code == 200
            assert [item["id"] for item in approved_plans.json()["items"]] == [plan_id]

            published_packages = await client.get(
                f"/api/v1/commercial-operations/{operation_id}/publish-packages?status=published",
                headers=headers,
            )
            assert published_packages.status_code == 200
            assert [item["id"] for item in published_packages.json()["items"]] == [package_id]

            approved_snapshots = await client.get(
                f"/api/v1/commercial-operations/{operation_id}/platform-metric-snapshots?status=approved",
                headers=headers,
            )
            assert approved_snapshots.status_code == 200
            assert [item["id"] for item in approved_snapshots.json()["items"]] == [snapshot_id]
    finally:
        await engine.dispose()
