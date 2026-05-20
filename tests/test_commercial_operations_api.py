"""Commercial operations API tests."""

from __future__ import annotations

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
    CommercialOperationApproval,
    CommercialOperationAssetRequest,
    CommercialOperationContentDraft,
    CommercialOperationDryRun,
    CommercialOperationLink,
)


@pytest.mark.asyncio
async def test_commercial_operations_api_flow() -> None:
    _ = (
        CommercialOperation,
        CommercialOperationApproval,
        CommercialOperationAssetRequest,
        CommercialOperationContentDraft,
        CommercialOperationDryRun,
        CommercialOperationLink,
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
    headers = {"X-Workspace-Id": "workspace-commercial-api", "X-User-Id": "user-commercial-api"}

    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            missing_header = await client.post(
                "/api/v1/commercial-operations",
                json={"title": "Missing", "objective": "missing workspace"},
            )
            assert missing_header.status_code == 400

            created = await client.post(
                "/api/v1/commercial-operations",
                headers=headers,
                json={
                    "title": "Lead generation operation",
                    "objective": "Increase qualified leads in 30 days.",
                    "target_audience": "B2B buyers",
                    "channels": ["website", "newsletter"],
                    "success_metrics": ["qualified_leads", "review_pass_rate"],
                    "constraints": ["human approval required"],
                    "knowledge_collection": "ai_knowledge_base",
                    "priority": "high",
                    "risk_level": "medium",
                    "budget_amount": "1200.50",
                },
            )
            assert created.status_code == 201
            body = created.json()
            operation_id = body["id"]
            assert body["workspace_id"] == "workspace-commercial-api"
            assert body["status"] == "draft"
            assert [step["step_key"] for step in body["plan_outline"]] == [
                "intake",
                "knowledge_research",
                "content_production",
                "human_review",
                "execution_dry_run",
                "monitor_recover",
            ]

            plan = await client.post(f"/api/v1/commercial-operations/{operation_id}/plan-draft", headers=headers)
            assert plan.status_code == 200
            assert plan.json()["operation_id"] == operation_id
            assert len(plan.json()["plan_outline"]) == 6

            fetched = await client.get(f"/api/v1/commercial-operations/{operation_id}", headers=headers)
            assert fetched.status_code == 200
            assert fetched.json()["status"] == "planning"

            hidden = await client.get(
                f"/api/v1/commercial-operations/{operation_id}",
                headers={"X-Workspace-Id": "other-workspace"},
            )
            assert hidden.status_code == 404

            updated = await client.patch(
                f"/api/v1/commercial-operations/{operation_id}",
                headers=headers,
                json={"status": "ready", "risk_level": "high", "constraints": ["review", "dry-run"]},
            )
            assert updated.status_code == 200
            assert updated.json()["status"] == "ready"
            assert updated.json()["risk_level"] == "high"
            assert updated.json()["constraints"] == ["review", "dry-run"]

            listed = await client.get("/api/v1/commercial-operations?status=ready", headers=headers)
            assert listed.status_code == 200
            assert [item["id"] for item in listed.json()["items"]] == [operation_id]

            content_draft = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/content-drafts",
                headers=headers,
                json={
                    "step_key": "content_production",
                    "channel": "newsletter",
                    "content_format": "email",
                    "title": "Newsletter lead generation draft",
                    "summary": "Introduce the offer and invite qualified leads to book a demo.",
                    "call_to_action": "Book a demo",
                    "source_materials": ["ai_knowledge_base"],
                    "asset_requests": [{"title": "Hero visual placeholder", "type": "image"}],
                    "metadata": {"phase": "61E"},
                },
            )
            assert content_draft.status_code == 201
            content_body = content_draft.json()
            content_draft_id = content_body["id"]
            assert content_body["workspace_id"] == "workspace-commercial-api"
            assert content_body["operation_id"] == operation_id
            assert content_body["step_key"] == "content_production"
            assert content_body["channel"] == "newsletter"
            assert content_body["content_format"] == "email"
            assert content_body["draft_status"] == "draft"
            assert content_body["created_by"] == "user-commercial-api"
            assert "does not publish" in content_body["content_body"]
            assert content_body["asset_requests"][0]["execution_boundary"] == "no ComfyUI job is created in this phase"

            content_drafts = await client.get(
                f"/api/v1/commercial-operations/{operation_id}/content-drafts",
                headers=headers,
            )
            assert content_drafts.status_code == 200
            assert [item["id"] for item in content_drafts.json()["items"]] == [content_draft_id]

            hidden_content_drafts = await client.get(
                f"/api/v1/commercial-operations/{operation_id}/content-drafts",
                headers={"X-Workspace-Id": "other-workspace"},
            )
            assert hidden_content_drafts.status_code == 404

            patched_content_draft = await client.patch(
                f"/api/v1/commercial-operations/{operation_id}/content-drafts/{content_draft_id}",
                headers=headers,
                json={"content_body": "Reviewed draft body. Still not published.", "summary": "Reviewed draft."},
            )
            assert patched_content_draft.status_code == 200
            assert patched_content_draft.json()["content_body"] == "Reviewed draft body. Still not published."
            assert patched_content_draft.json()["updated_by"] == "user-commercial-api"

            ready_content_draft = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/content-drafts/{content_draft_id}/ready",
                headers=headers,
                json={"reviewer_notes": "Ready for review."},
            )
            assert ready_content_draft.status_code == 200
            assert ready_content_draft.json()["draft_status"] == "ready_for_review"

            approved_content_draft = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/content-drafts/{content_draft_id}/approve",
                headers=headers,
                json={"reviewer_notes": "Approved as draft only."},
            )
            assert approved_content_draft.status_code == 200
            assert approved_content_draft.json()["draft_status"] == "approved"
            assert approved_content_draft.json()["approved_by"] == "user-commercial-api"

            fetched_after_content_draft = await client.get(
                f"/api/v1/commercial-operations/{operation_id}",
                headers=headers,
            )
            assert fetched_after_content_draft.status_code == 200
            content_step = [
                step
                for step in fetched_after_content_draft.json()["plan_outline"]
                if step["step_key"] == "content_production"
            ][0]
            assert content_step["content_draft_id"] == content_draft_id
            assert content_step["content_draft_status"] == "approved"
            assert content_step["content_draft_channel"] == "newsletter"

            asset_request = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/asset-requests",
                headers=headers,
                json={
                    "step_key": "content_production",
                    "content_draft_id": content_draft_id,
                    "channel": "newsletter",
                    "asset_type": "image",
                    "title": "Newsletter hero image request",
                    "purpose": "Header visual for the approved newsletter draft.",
                    "dimensions": "16:9",
                    "style_constraints": "Clean product-led composition; no brand-inconsistent colors.",
                    "generation_prompt": "Create a professional B2B hero visual for lead generation.",
                    "negative_prompt": "No logos, no unreadable text.",
                    "source_materials": ["ai_knowledge_base"],
                    "readiness_checks": ["approved content draft", "no ComfyUI job"],
                    "metadata": {"phase": "61F"},
                },
            )
            assert asset_request.status_code == 201
            asset_body = asset_request.json()
            asset_request_id = asset_body["id"]
            assert asset_body["workspace_id"] == "workspace-commercial-api"
            assert asset_body["operation_id"] == operation_id
            assert asset_body["content_draft_id"] == content_draft_id
            assert asset_body["request_status"] == "draft"
            assert asset_body["requested_by"] == "user-commercial-api"
            assert asset_body["handoff_payload"]["execution_boundary"] == "no ComfyUI job is created in this phase"
            assert asset_body["handoff_payload"]["next_runtime"] == "future_comfyui_handoff"

            asset_requests = await client.get(
                f"/api/v1/commercial-operations/{operation_id}/asset-requests",
                headers=headers,
            )
            assert asset_requests.status_code == 200
            assert [item["id"] for item in asset_requests.json()["items"]] == [asset_request_id]

            hidden_asset_requests = await client.get(
                f"/api/v1/commercial-operations/{operation_id}/asset-requests",
                headers={"X-Workspace-Id": "other-workspace"},
            )
            assert hidden_asset_requests.status_code == 404

            patched_asset_request = await client.patch(
                f"/api/v1/commercial-operations/{operation_id}/asset-requests/{asset_request_id}",
                headers=headers,
                json={"generation_prompt": "Updated prompt for later generation.", "dimensions": "1200x628"},
            )
            assert patched_asset_request.status_code == 200
            assert patched_asset_request.json()["generation_prompt"] == "Updated prompt for later generation."
            assert patched_asset_request.json()["updated_by"] == "user-commercial-api"

            ready_asset_request = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/asset-requests/{asset_request_id}/ready",
                headers=headers,
                json={"reviewer_notes": "Ready for review."},
            )
            assert ready_asset_request.status_code == 200
            assert ready_asset_request.json()["request_status"] == "ready_for_review"

            approved_asset_request = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/asset-requests/{asset_request_id}/approve",
                headers=headers,
                json={"reviewer_notes": "Approved as request only."},
            )
            assert approved_asset_request.status_code == 200
            assert approved_asset_request.json()["request_status"] == "approved"
            assert approved_asset_request.json()["approved_by"] == "user-commercial-api"

            prepared_asset_request = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/asset-requests/{asset_request_id}/prepare",
                headers=headers,
                json={"result_summary": "Prepared for future ComfyUI handoff; no job started."},
            )
            assert prepared_asset_request.status_code == 200
            assert prepared_asset_request.json()["request_status"] == "prepared"
            assert prepared_asset_request.json()["prepared_by"] == "user-commercial-api"

            fetched_after_asset_request = await client.get(
                f"/api/v1/commercial-operations/{operation_id}",
                headers=headers,
            )
            assert fetched_after_asset_request.status_code == 200
            asset_step = [
                step
                for step in fetched_after_asset_request.json()["plan_outline"]
                if step["step_key"] == "content_production"
            ][0]
            assert asset_step["asset_request_id"] == asset_request_id
            assert asset_step["asset_request_status"] == "prepared"
            assert asset_step["asset_request_type"] == "image"

            reject_after_prepared_asset_request = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/asset-requests/{asset_request_id}/reject",
                headers=headers,
                json={"reviewer_notes": "Too late to reject."},
            )
            assert reject_after_prepared_asset_request.status_code == 400

            archived_asset_request = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/asset-requests/{asset_request_id}/archive",
                headers=headers,
                json={"reviewer_notes": "Archived after preparation."},
            )
            assert archived_asset_request.status_code == 200
            assert archived_asset_request.json()["request_status"] == "archived"

            patch_archived_asset_request = await client.patch(
                f"/api/v1/commercial-operations/{operation_id}/asset-requests/{asset_request_id}",
                headers=headers,
                json={"purpose": "Should not change."},
            )
            assert patch_archived_asset_request.status_code == 400

            failing_asset_request = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/asset-requests",
                headers=headers,
                json={
                    "step_key": "content_production",
                    "channel": "newsletter",
                    "asset_type": "design",
                    "title": "Fallback design request",
                },
            )
            assert failing_asset_request.status_code == 201
            failing_asset_request_id = failing_asset_request.json()["id"]
            assert (
                await client.post(
                    f"/api/v1/commercial-operations/{operation_id}/asset-requests/{failing_asset_request_id}/ready",
                    headers=headers,
                    json={},
                )
            ).status_code == 200
            assert (
                await client.post(
                    f"/api/v1/commercial-operations/{operation_id}/asset-requests/{failing_asset_request_id}/approve",
                    headers=headers,
                    json={},
                )
            ).status_code == 200
            failed_asset_request = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/asset-requests/{failing_asset_request_id}/fail",
                headers=headers,
                json={"failure_reason": "Missing required source material."},
            )
            assert failed_asset_request.status_code == 200
            assert failed_asset_request.json()["request_status"] == "failed"
            assert failed_asset_request.json()["failure_reason"] == "Missing required source material."

            invalid_asset_request = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/asset-requests",
                headers=headers,
                json={
                    "step_key": "missing_step",
                    "channel": "newsletter",
                    "asset_type": "image",
                    "title": "Invalid asset step",
                },
            )
            assert invalid_asset_request.status_code == 400

            reject_after_approval_content_draft = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/content-drafts/{content_draft_id}/reject",
                headers=headers,
                json={"reviewer_notes": "Too late to reject."},
            )
            assert reject_after_approval_content_draft.status_code == 400

            archived_content_draft = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/content-drafts/{content_draft_id}/archive",
                headers=headers,
                json={"reviewer_notes": "Archived after handoff."},
            )
            assert archived_content_draft.status_code == 200
            assert archived_content_draft.json()["draft_status"] == "archived"

            patch_archived_content_draft = await client.patch(
                f"/api/v1/commercial-operations/{operation_id}/content-drafts/{content_draft_id}",
                headers=headers,
                json={"summary": "Should not change."},
            )
            assert patch_archived_content_draft.status_code == 400

            invalid_content_draft = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/content-drafts",
                headers=headers,
                json={
                    "step_key": "missing_step",
                    "channel": "newsletter",
                    "title": "Invalid content step",
                },
            )
            assert invalid_content_draft.status_code == 400

            approval = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/approvals",
                headers=headers,
                json={
                    "step_key": "human_review",
                    "title": "Review before execution",
                    "requested_action": "Approve the plan before any dry-run or external account action.",
                    "risk_level": "high",
                    "metadata": {"gate": "human_review"},
                },
            )
            assert approval.status_code == 201
            approval_body = approval.json()
            approval_id = approval_body["id"]
            assert approval_body["workspace_id"] == "workspace-commercial-api"
            assert approval_body["operation_id"] == operation_id
            assert approval_body["approval_status"] == "pending"
            assert approval_body["requested_by"] == "user-commercial-api"

            approvals = await client.get(f"/api/v1/commercial-operations/{operation_id}/approvals", headers=headers)
            assert approvals.status_code == 200
            assert [item["id"] for item in approvals.json()["items"]] == [approval_id]

            hidden_approvals = await client.get(
                f"/api/v1/commercial-operations/{operation_id}/approvals",
                headers={"X-Workspace-Id": "other-workspace"},
            )
            assert hidden_approvals.status_code == 404

            approved = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/approvals/{approval_id}/approve",
                headers=headers,
                json={"reviewer_notes": "Approved for dry-run only."},
            )
            assert approved.status_code == 200
            assert approved.json()["approval_status"] == "approved"
            assert approved.json()["reviewer_user_id"] == "user-commercial-api"

            fetched_after_approval = await client.get(f"/api/v1/commercial-operations/{operation_id}", headers=headers)
            assert fetched_after_approval.status_code == 200
            human_review_step = [
                step
                for step in fetched_after_approval.json()["plan_outline"]
                if step["step_key"] == "human_review"
            ][0]
            assert human_review_step["approval_id"] == approval_id
            assert human_review_step["approval_status"] == "approved"

            dry_run = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/dry-runs",
                headers=headers,
                json={
                    "approval_id": approval_id,
                    "step_key": "execution_dry_run",
                    "title": "Execution dry-run preparation",
                    "execution_mode": "metadata_only",
                    "execution_target": "newsletter",
                    "input_summary": "Prepare a safe dry-run payload for approved campaign execution.",
                    "expected_outputs": ["payload preview", "operator handoff"],
                    "readiness_checks": ["approval gate", "no external publish"],
                    "metadata": {"dry_run": "operator"},
                },
            )
            assert dry_run.status_code == 201
            dry_run_body = dry_run.json()
            dry_run_id = dry_run_body["id"]
            assert dry_run_body["workspace_id"] == "workspace-commercial-api"
            assert dry_run_body["approval_id"] == approval_id
            assert dry_run_body["step_key"] == "execution_dry_run"
            assert dry_run_body["dry_run_status"] == "created"
            assert dry_run_body["execution_mode"] == "metadata_only"
            assert dry_run_body["execution_target"] == "newsletter"
            assert dry_run_body["runbook"][0]["approval_status"] == "approved"

            dry_runs = await client.get(f"/api/v1/commercial-operations/{operation_id}/dry-runs", headers=headers)
            assert dry_runs.status_code == 200
            assert [item["id"] for item in dry_runs.json()["items"]] == [dry_run_id]

            hidden_dry_runs = await client.get(
                f"/api/v1/commercial-operations/{operation_id}/dry-runs",
                headers={"X-Workspace-Id": "other-workspace"},
            )
            assert hidden_dry_runs.status_code == 404

            completed_dry_run = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/dry-runs/{dry_run_id}/complete",
                headers=headers,
                json={"result_summary": "Payload is ready for operator review; no external action was executed."},
            )
            assert completed_dry_run.status_code == 200
            assert completed_dry_run.json()["dry_run_status"] == "completed"
            assert completed_dry_run.json()["completed_by"] == "user-commercial-api"

            fetched_after_dry_run = await client.get(f"/api/v1/commercial-operations/{operation_id}", headers=headers)
            assert fetched_after_dry_run.status_code == 200
            dry_run_step = [
                step
                for step in fetched_after_dry_run.json()["plan_outline"]
                if step["step_key"] == "execution_dry_run"
            ][0]
            assert dry_run_step["dry_run_id"] == dry_run_id
            assert dry_run_step["dry_run_status"] == "completed"

            fail_after_complete = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/dry-runs/{dry_run_id}/fail",
                headers=headers,
                json={"failure_reason": "Too late to fail."},
            )
            assert fail_after_complete.status_code == 400

            reject_after_approval = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/approvals/{approval_id}/reject",
                headers=headers,
                json={"reviewer_notes": "Too late to reject."},
            )
            assert reject_after_approval.status_code == 400

            cancelled = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/approvals/{approval_id}/cancel",
                headers=headers,
                json={"reviewer_notes": "Cancelled before execution."},
            )
            assert cancelled.status_code == 200
            assert cancelled.json()["approval_status"] == "cancelled"

            dry_run_after_cancelled_approval = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/dry-runs",
                headers=headers,
                json={
                    "approval_id": approval_id,
                    "step_key": "execution_dry_run",
                    "title": "Blocked dry-run",
                },
            )
            assert dry_run_after_cancelled_approval.status_code == 400

            invalid_approval = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/approvals",
                headers=headers,
                json={
                    "step_key": "missing_step",
                    "title": "Invalid step",
                    "risk_level": "medium",
                },
            )
            assert invalid_approval.status_code == 400

            link = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/links",
                headers=headers,
                json={
                    "link_type": "conversation",
                    "target_type": "conversation_thread",
                    "target_id": "thread-123",
                    "title": "Intake conversation",
                    "summary": "Initial operator goal intake.",
                    "source_name": "admin_dashboard",
                    "metadata": {"handoff": "operator"},
                },
            )
            assert link.status_code == 201
            link_body = link.json()
            assert link_body["workspace_id"] == "workspace-commercial-api"
            assert link_body["operation_id"] == operation_id
            assert link_body["link_type"] == "conversation"
            assert link_body["target_id"] == "thread-123"

            links = await client.get(f"/api/v1/commercial-operations/{operation_id}/links", headers=headers)
            assert links.status_code == 200
            assert [item["id"] for item in links.json()["items"]] == [link_body["id"]]

            hidden_links = await client.get(
                f"/api/v1/commercial-operations/{operation_id}/links",
                headers={"X-Workspace-Id": "other-workspace"},
            )
            assert hidden_links.status_code == 404

            deleted = await client.delete(
                f"/api/v1/commercial-operations/{operation_id}/links/{link_body['id']}",
                headers=headers,
            )
            assert deleted.status_code == 200
            assert deleted.json()["id"] == link_body["id"]

            links_after_delete = await client.get(f"/api/v1/commercial-operations/{operation_id}/links", headers=headers)
            assert links_after_delete.status_code == 200
            assert links_after_delete.json()["items"] == []

            invalid = await client.post(
                "/api/v1/commercial-operations",
                headers=headers,
                json={
                    "title": "Bad dates",
                    "objective": "Invalid date range",
                    "start_at": "2026-06-02T00:00:00Z",
                    "end_at": "2026-06-01T00:00:00Z",
                },
            )
            assert invalid.status_code == 422
    finally:
        await engine.dispose()
