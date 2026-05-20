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
    CommercialOperationComfyUIHandoff,
    CommercialOperationContentDraft,
    CommercialOperationDeliverable,
    CommercialOperationDryRun,
    CommercialOperationEvidenceSnapshot,
    CommercialOperationExecutionRequest,
    CommercialOperationExecutionRun,
    CommercialOperationLink,
    CommercialOperationMonitoringObservation,
    CommercialOperationResult,
    CommercialOperationOptimizationDecision,
    Document,
    DocumentChunk,
)


@pytest.mark.asyncio
async def test_commercial_operations_api_flow() -> None:
    _ = (
        CommercialOperation,
        CommercialOperationApproval,
        CommercialOperationAssetRequest,
        CommercialOperationComfyUIHandoff,
        CommercialOperationContentDraft,
        CommercialOperationDeliverable,
        CommercialOperationDryRun,
        CommercialOperationEvidenceSnapshot,
        CommercialOperationExecutionRequest,
        CommercialOperationExecutionRun,
        CommercialOperationLink,
        CommercialOperationMonitoringObservation,
        CommercialOperationResult,
        CommercialOperationOptimizationDecision,
        Document,
        DocumentChunk,
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

            async with session_factory() as db_session:
                content_rag_document = Document(
                    workspace_id="workspace-commercial-api",
                    user_id="user-commercial-api",
                    source_id="commercial-content-source",
                    source_name="Commercial content playbook",
                    source_type="text",
                    collection_name="ai_knowledge_base",
                    chunk_count=1,
                    document_metadata={"phase": "61O"},
                )
                db_session.add(content_rag_document)
                await db_session.flush()
                db_session.add(
                    DocumentChunk(
                        document_id=content_rag_document.id,
                        collection_name="ai_knowledge_base",
                        chunk_index=0,
                        text=(
                            "Buyer education content draft: emphasize audience pain, helpful next step, "
                            "manual approval boundary, and operator review before any publishing."
                        ),
                        qdrant_point_id="commercial-content-rag-chunk-1",
                        chunk_metadata={"section": "content_draft"},
                    )
                )
                await db_session.commit()
                content_rag_document_id = str(content_rag_document.id)

            generated_content_draft = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/content-drafts/generate-rag",
                headers=headers,
                json={
                    "step_key": "content_production",
                    "channel": "newsletter",
                    "content_format": "email",
                    "title": "Generated RAG newsletter draft",
                    "query": "buyer education content draft",
                    "knowledge_collection": "ai_knowledge_base",
                    "search_mode": "keyword",
                    "final_top_k": 3,
                    "call_to_action": "Book a demo",
                    "asset_requests": [{"title": "Generated proof visual", "type": "asset_placeholder"}],
                    "metadata": {"phase": "61O"},
                },
            )
            assert generated_content_draft.status_code == 201
            generated_content_body = generated_content_draft.json()
            assert generated_content_body["draft_status"] == "draft"
            assert generated_content_body["title"] == "Generated RAG newsletter draft"
            assert "RAG evidence used" in generated_content_body["content_body"]
            assert "no publishing" in generated_content_body["content_body"]
            assert f"document:{content_rag_document_id}" in generated_content_body["source_materials"]
            assert "source:commercial-content-source" in generated_content_body["source_materials"]
            assert generated_content_body["asset_requests"][0]["execution_boundary"] == "no ComfyUI job is created in this phase"
            assert generated_content_body["metadata"]["generation_mode"] == "rag_content_draft"
            assert generated_content_body["metadata"]["search_mode"] == "keyword"
            assert generated_content_body["metadata"]["rag_result_count"] == 1
            assert "no automatic approval" in generated_content_body["metadata"]["forbidden_actions"]

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

            comfyui_handoff = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/comfyui-handoffs",
                headers=headers,
                json={
                    "asset_request_id": asset_request_id,
                    "title": "Newsletter hero ComfyUI handoff",
                    "workflow_name": "future_comfyui_handoff",
                    "prompt_payload": {"prompt": "metadata only", "asset_request_id": asset_request_id},
                    "workflow_payload": {
                        "adapter": "unsafe_live_adapter",
                        "execution_mode": "live",
                        "workflow_name": "unsafe_live_workflow",
                    },
                    "readiness_checks": ["approved asset request", "no ComfyUI job submitted"],
                    "metadata": {"phase": "61Q"},
                },
            )
            assert comfyui_handoff.status_code == 201
            comfyui_handoff_body = comfyui_handoff.json()
            comfyui_handoff_id = comfyui_handoff_body["id"]
            assert comfyui_handoff_body["handoff_status"] == "draft"
            assert comfyui_handoff_body["asset_request_id"] == asset_request_id
            assert comfyui_handoff_body["requested_by"] == "user-commercial-api"
            assert "no ComfyUI job is submitted" in comfyui_handoff_body["handoff_payload"]["execution_boundary"]
            assert comfyui_handoff_body["handoff_payload"]["next_runtime"] == "future_guarded_comfyui_adapter"
            assert "no approval bypass" in comfyui_handoff_body["handoff_payload"]["forbidden_actions"]
            assert comfyui_handoff_body["workflow_payload"]["adapter"] == "future_guarded_comfyui_adapter"
            assert comfyui_handoff_body["workflow_payload"]["execution_mode"] == "metadata_only"
            assert comfyui_handoff_body["workflow_payload"]["workflow_name"] == "future_comfyui_handoff"

            comfyui_handoffs = await client.get(
                f"/api/v1/commercial-operations/{operation_id}/comfyui-handoffs",
                headers=headers,
            )
            assert comfyui_handoffs.status_code == 200
            assert [item["id"] for item in comfyui_handoffs.json()["items"]] == [comfyui_handoff_id]

            hidden_comfyui_handoffs = await client.get(
                f"/api/v1/commercial-operations/{operation_id}/comfyui-handoffs",
                headers={"X-Workspace-Id": "other-workspace"},
            )
            assert hidden_comfyui_handoffs.status_code == 404

            patched_comfyui_handoff = await client.patch(
                f"/api/v1/commercial-operations/{operation_id}/comfyui-handoffs/{comfyui_handoff_id}",
                headers=headers,
                json={
                    "title": "Updated ComfyUI handoff",
                    "workflow_name": "future_comfyui_handoff_v2",
                    "workflow_payload": {"execution_mode": "live"},
                },
            )
            assert patched_comfyui_handoff.status_code == 200
            assert patched_comfyui_handoff.json()["title"] == "Updated ComfyUI handoff"
            assert patched_comfyui_handoff.json()["updated_by"] == "user-commercial-api"
            assert patched_comfyui_handoff.json()["handoff_status"] == "draft"
            assert patched_comfyui_handoff.json()["workflow_payload"]["execution_mode"] == "metadata_only"
            assert patched_comfyui_handoff.json()["workflow_payload"]["workflow_name"] == "future_comfyui_handoff_v2"

            ready_comfyui_handoff = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/comfyui-handoffs/{comfyui_handoff_id}/ready",
                headers=headers,
                json={"reviewer_notes": "Ready for guarded adapter review."},
            )
            assert ready_comfyui_handoff.status_code == 200
            assert ready_comfyui_handoff.json()["handoff_status"] == "ready_for_review"

            approved_comfyui_handoff = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/comfyui-handoffs/{comfyui_handoff_id}/approve",
                headers=headers,
                json={"reviewer_notes": "Approved as metadata-only handoff."},
            )
            assert approved_comfyui_handoff.status_code == 200
            assert approved_comfyui_handoff.json()["handoff_status"] == "approved"
            assert approved_comfyui_handoff.json()["approved_by"] == "user-commercial-api"

            prepared_comfyui_handoff = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/comfyui-handoffs/{comfyui_handoff_id}/prepare",
                headers=headers,
                json={"result_summary": "Prepared for future guarded ComfyUI adapter; no job submitted."},
            )
            assert prepared_comfyui_handoff.status_code == 200
            assert prepared_comfyui_handoff.json()["handoff_status"] == "prepared"
            assert prepared_comfyui_handoff.json()["prepared_by"] == "user-commercial-api"

            fetched_after_comfyui_handoff = await client.get(
                f"/api/v1/commercial-operations/{operation_id}",
                headers=headers,
            )
            assert fetched_after_comfyui_handoff.status_code == 200
            comfyui_step = [
                step
                for step in fetched_after_comfyui_handoff.json()["plan_outline"]
                if step["step_key"] == "content_production"
            ][0]
            assert comfyui_step["comfyui_handoff_id"] == comfyui_handoff_id
            assert comfyui_step["comfyui_handoff_status"] == "prepared"
            assert comfyui_step["comfyui_handoff_asset_request_id"] == asset_request_id
            assert comfyui_step["comfyui_handoff_workflow_name"] == "future_comfyui_handoff_v2"

            async with session_factory() as db_session:
                asset_rag_document = Document(
                    workspace_id="workspace-commercial-api",
                    user_id="user-commercial-api",
                    source_id="commercial-asset-source",
                    source_name="Commercial asset playbook",
                    source_type="text",
                    collection_name="ai_knowledge_base",
                    chunk_count=1,
                    document_metadata={"phase": "61P"},
                )
                db_session.add(asset_rag_document)
                await db_session.flush()
                db_session.add(
                    DocumentChunk(
                        document_id=asset_rag_document.id,
                        collection_name="ai_knowledge_base",
                        chunk_index=0,
                        text=(
                            "Visual trust asset brief: show buyer education, product workflow clarity, "
                            "and manual review boundary for the channel."
                        ),
                        qdrant_point_id="commercial-asset-rag-chunk-1",
                        chunk_metadata={"section": "asset_brief"},
                    )
                )
                await db_session.commit()
                asset_rag_document_id = str(asset_rag_document.id)

            generated_asset_request = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/asset-requests/generate-rag",
                headers=headers,
                json={
                    "step_key": "content_production",
                    "content_draft_id": content_draft_id,
                    "channel": "newsletter",
                    "asset_type": "image",
                    "title": "Generated RAG hero asset request",
                    "query": "visual trust asset brief",
                    "knowledge_collection": "ai_knowledge_base",
                    "search_mode": "keyword",
                    "final_top_k": 3,
                    "dimensions": "1200x628",
                    "metadata": {"phase": "61P"},
                },
            )
            assert generated_asset_request.status_code == 201
            generated_asset_body = generated_asset_request.json()
            assert generated_asset_body["request_status"] == "draft"
            assert generated_asset_body["content_draft_id"] == content_draft_id
            assert "Source evidence" in generated_asset_body["generation_prompt"]
            assert "no ComfyUI job" in generated_asset_body["generation_prompt"]
            assert f"document:{asset_rag_document_id}" in generated_asset_body["source_materials"]
            assert "source:commercial-asset-source" in generated_asset_body["source_materials"]
            assert "no ComfyUI job was created" in generated_asset_body["readiness_checks"]
            assert generated_asset_body["handoff_payload"]["execution_boundary"] == "no ComfyUI job is created in this phase"
            assert generated_asset_body["metadata"]["generation_mode"] == "rag_asset_brief"
            assert generated_asset_body["metadata"]["search_mode"] == "keyword"
            assert generated_asset_body["metadata"]["rag_result_count"] == 1
            assert "no automatic approval" in generated_asset_body["metadata"]["forbidden_actions"]

            deliverable = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/deliverables",
                headers=headers,
                json={
                    "step_key": "content_production",
                    "content_draft_id": content_draft_id,
                    "asset_request_ids": [asset_request_id],
                    "deliverable_type": "email",
                    "title": "Newsletter commercial deliverable",
                    "summary": "Approved newsletter packaged for operator handoff.",
                    "delivery_notes": "Keep as Output Library artifact only; do not publish.",
                    "quality_checks": ["approved copy", "prepared hero image", "no external execution"],
                    "metadata": {"phase": "61G"},
                },
            )
            assert deliverable.status_code == 201
            deliverable_body = deliverable.json()
            deliverable_id = deliverable_body["id"]
            output_artifact_id = deliverable_body["output_artifact_id"]
            assert deliverable_body["workspace_id"] == "workspace-commercial-api"
            assert deliverable_body["operation_id"] == operation_id
            assert deliverable_body["content_draft_id"] == content_draft_id
            assert deliverable_body["asset_request_ids"] == [asset_request_id]
            assert deliverable_body["deliverable_status"] == "draft"
            assert deliverable_body["created_by"] == "user-commercial-api"
            assert output_artifact_id
            assert deliverable_body["package_payload"]["output_artifact_id"] == output_artifact_id
            assert "metadata-only" in deliverable_body["package_payload"]["execution_boundary"]

            deliverables = await client.get(
                f"/api/v1/commercial-operations/{operation_id}/deliverables",
                headers=headers,
            )
            assert deliverables.status_code == 200
            assert [item["id"] for item in deliverables.json()["items"]] == [deliverable_id]

            hidden_deliverables = await client.get(
                f"/api/v1/commercial-operations/{operation_id}/deliverables",
                headers={"X-Workspace-Id": "other-workspace"},
            )
            assert hidden_deliverables.status_code == 404

            patched_deliverable = await client.patch(
                f"/api/v1/commercial-operations/{operation_id}/deliverables/{deliverable_id}",
                headers=headers,
                json={"summary": "Updated operator handoff summary.", "quality_checks": ["approved copy"]},
            )
            assert patched_deliverable.status_code == 200
            assert patched_deliverable.json()["summary"] == "Updated operator handoff summary."
            assert patched_deliverable.json()["updated_by"] == "user-commercial-api"

            ready_deliverable = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/deliverables/{deliverable_id}/ready",
                headers=headers,
                json={"reviewer_notes": "Ready for review."},
            )
            assert ready_deliverable.status_code == 200
            assert ready_deliverable.json()["deliverable_status"] == "ready_for_review"

            approved_deliverable = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/deliverables/{deliverable_id}/approve",
                headers=headers,
                json={"reviewer_notes": "Approved as handoff artifact only."},
            )
            assert approved_deliverable.status_code == 200
            assert approved_deliverable.json()["deliverable_status"] == "approved"
            assert approved_deliverable.json()["approved_by"] == "user-commercial-api"

            packaged_deliverable = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/deliverables/{deliverable_id}/package",
                headers=headers,
                json={"result_summary": "Packaged for Output Library handoff; no publishing executed."},
            )
            assert packaged_deliverable.status_code == 200
            assert packaged_deliverable.json()["deliverable_status"] == "packaged"
            assert packaged_deliverable.json()["packaged_by"] == "user-commercial-api"
            assert packaged_deliverable.json()["package_payload"]["next_runtime"] == "future_monitored_execution_request"

            output_artifact = await client.get(
                f"/api/v1/output-artifacts/{output_artifact_id}",
                headers=headers,
            )
            assert output_artifact.status_code == 200
            output_artifact_body = output_artifact.json()
            assert output_artifact_body["source_type"] == "commercial_operation"
            assert output_artifact_body["artifact_type"] == "markdown"
            assert output_artifact_body["artifact_stage"] == "packaged"
            assert output_artifact_body["metadata"]["commercial_deliverable_id"] == deliverable_id
            assert "does not publish" in output_artifact_body["content"]

            fetched_after_deliverable = await client.get(
                f"/api/v1/commercial-operations/{operation_id}",
                headers=headers,
            )
            assert fetched_after_deliverable.status_code == 200
            deliverable_step = [
                step
                for step in fetched_after_deliverable.json()["plan_outline"]
                if step["step_key"] == "content_production"
            ][0]
            assert deliverable_step["deliverable_id"] == deliverable_id
            assert deliverable_step["deliverable_status"] == "packaged"
            assert deliverable_step["deliverable_output_artifact_id"] == output_artifact_id

            evidence_snapshot = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/evidence-snapshots",
                headers=headers,
                json={
                    "deliverable_id": deliverable_id,
                    "evidence_type": "rag_snapshot",
                    "title": "Newsletter evidence snapshot",
                    "knowledge_collection": "ai_knowledge_base",
                    "query": "Which knowledge sources support this newsletter handoff?",
                    "evidence_summary": "Source notes support the target audience, offer, and review boundary.",
                    "relevance_notes": "Operator confirmed the evidence before execution handoff.",
                    "source_document_ids": ["doc-001", "doc-002"],
                    "source_links": [{"title": "Approved draft", "target": content_draft_id}],
                    "evidence_items": [{"title": "Customer pain point"}, {"title": "Offer proof"}],
                    "coverage_checks": ["source reviewed", "relevance confirmed", "no live retrieval"],
                    "metadata": {"phase": "61M"},
                },
            )
            assert evidence_snapshot.status_code == 201
            evidence_snapshot_body = evidence_snapshot.json()
            evidence_snapshot_id = evidence_snapshot_body["id"]
            assert evidence_snapshot_body["workspace_id"] == "workspace-commercial-api"
            assert evidence_snapshot_body["operation_id"] == operation_id
            assert evidence_snapshot_body["deliverable_id"] == deliverable_id
            assert evidence_snapshot_body["content_draft_id"] == content_draft_id
            assert evidence_snapshot_body["output_artifact_id"] == output_artifact_id
            assert evidence_snapshot_body["snapshot_status"] == "draft"
            assert evidence_snapshot_body["created_by"] == "user-commercial-api"
            assert evidence_snapshot_body["snapshot_payload"]["non_goals"][0] == "does not run live RAG retrieval"

            evidence_snapshots = await client.get(
                f"/api/v1/commercial-operations/{operation_id}/evidence-snapshots",
                headers=headers,
            )
            assert evidence_snapshots.status_code == 200
            assert [item["id"] for item in evidence_snapshots.json()["items"]] == [evidence_snapshot_id]

            hidden_evidence_snapshots = await client.get(
                f"/api/v1/commercial-operations/{operation_id}/evidence-snapshots",
                headers={"X-Workspace-Id": "other-workspace"},
            )
            assert hidden_evidence_snapshots.status_code == 404

            patched_evidence_snapshot = await client.patch(
                f"/api/v1/commercial-operations/{operation_id}/evidence-snapshots/{evidence_snapshot_id}",
                headers=headers,
                json={"evidence_summary": "Updated operator evidence summary.", "coverage_checks": ["reviewed"]},
            )
            assert patched_evidence_snapshot.status_code == 200
            assert patched_evidence_snapshot.json()["evidence_summary"] == "Updated operator evidence summary."
            assert patched_evidence_snapshot.json()["updated_by"] == "user-commercial-api"

            ready_evidence_snapshot = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/evidence-snapshots/{evidence_snapshot_id}/ready",
                headers=headers,
                json={"reviewer_notes": "Ready for evidence review."},
            )
            assert ready_evidence_snapshot.status_code == 200
            assert ready_evidence_snapshot.json()["snapshot_status"] == "ready_for_review"

            approved_evidence_snapshot = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/evidence-snapshots/{evidence_snapshot_id}/approve",
                headers=headers,
                json={"reviewer_notes": "Approved for execution handoff."},
            )
            assert approved_evidence_snapshot.status_code == 200
            assert approved_evidence_snapshot.json()["snapshot_status"] == "approved"
            assert approved_evidence_snapshot.json()["approved_by"] == "user-commercial-api"

            fetched_after_evidence_snapshot = await client.get(
                f"/api/v1/commercial-operations/{operation_id}",
                headers=headers,
            )
            assert fetched_after_evidence_snapshot.status_code == 200
            evidence_step = [
                step
                for step in fetched_after_evidence_snapshot.json()["plan_outline"]
                if step["step_key"] == "content_production"
            ][0]
            assert evidence_step["evidence_snapshot_id"] == evidence_snapshot_id
            assert evidence_step["evidence_snapshot_status"] == "approved"
            assert evidence_step["evidence_snapshot_item_count"] == 2

            async with session_factory() as db_session:
                rag_document = Document(
                    workspace_id="workspace-commercial-api",
                    user_id="user-commercial-api",
                    source_id="commercial-playbook-source",
                    source_name="Commercial playbook",
                    source_type="text",
                    collection_name="ai_knowledge_base",
                    chunk_count=1,
                    document_metadata={"phase": "61N"},
                )
                db_session.add(rag_document)
                await db_session.flush()
                db_session.add(
                    DocumentChunk(
                        document_id=rag_document.id,
                        collection_name="ai_knowledge_base",
                        chunk_index=0,
                        text=(
                            "Lead generation proof: the newsletter offer should reference customer pain points, "
                            "book-a-demo CTA, and the approved review boundary."
                        ),
                        qdrant_point_id="commercial-rag-chunk-1",
                        chunk_metadata={"section": "proof_points"},
                    )
                )
                await db_session.commit()
                rag_document_id = str(rag_document.id)

            generated_evidence_snapshot = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/evidence-snapshots/generate-rag",
                headers=headers,
                json={
                    "deliverable_id": deliverable_id,
                    "title": "Generated newsletter evidence snapshot",
                    "knowledge_collection": "ai_knowledge_base",
                    "query": "lead generation proof newsletter offer",
                    "search_mode": "keyword",
                    "final_top_k": 3,
                    "coverage_checks": ["rag search completed", "operator review required"],
                    "metadata": {"phase": "61N"},
                },
            )
            assert generated_evidence_snapshot.status_code == 201
            generated_evidence_snapshot_body = generated_evidence_snapshot.json()
            assert generated_evidence_snapshot_body["snapshot_status"] == "draft"
            assert generated_evidence_snapshot_body["query"] == "lead generation proof newsletter offer"
            assert generated_evidence_snapshot_body["source_document_ids"] == [rag_document_id]
            assert generated_evidence_snapshot_body["evidence_items"][0]["document_id"] == rag_document_id
            assert generated_evidence_snapshot_body["evidence_items"][0]["source_id"] == "commercial-playbook-source"
            assert generated_evidence_snapshot_body["snapshot_payload"]["generation_mode"] == "rag_search_snapshot"
            assert generated_evidence_snapshot_body["snapshot_payload"]["search_mode"] == "keyword"
            assert generated_evidence_snapshot_body["snapshot_payload"]["result_count"] == 1
            assert "does not ingest new knowledge files" in generated_evidence_snapshot_body["snapshot_payload"]["non_goals"]
            assert "no knowledge ingestion" in generated_evidence_snapshot_body["snapshot_payload"]["forbidden_actions"]

            execution_request = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/execution-requests",
                headers=headers,
                json={
                    "deliverable_id": deliverable_id,
                    "execution_type": "platform_post",
                    "execution_mode": "metadata_only",
                    "title": "Newsletter platform handoff request",
                    "execution_target": "newsletter_platform",
                    "input_summary": "Prepare a future newsletter send from the packaged artifact.",
                    "runbook": [
                        {"step": "Review packaged artifact"},
                        {"step": "Confirm target segment"},
                    ],
                    "readiness_checks": ["packaged deliverable", "operator approval"],
                    "expected_outputs": ["approved execution request", "traceable handoff payload"],
                    "evidence_snapshot_ids": [evidence_snapshot_id],
                    "operator_checklist": [
                        {"item": "Review approved evidence snapshot"},
                        {"item": "Confirm target account"},
                    ],
                    "metadata": {"phase": "61M"},
                },
            )
            assert execution_request.status_code == 201
            execution_request_body = execution_request.json()
            execution_request_id = execution_request_body["id"]
            assert execution_request_body["workspace_id"] == "workspace-commercial-api"
            assert execution_request_body["operation_id"] == operation_id
            assert execution_request_body["deliverable_id"] == deliverable_id
            assert execution_request_body["output_artifact_id"] == output_artifact_id
            assert execution_request_body["request_status"] == "draft"
            assert execution_request_body["requested_by"] == "user-commercial-api"
            assert execution_request_body["handoff_payload"]["execution_boundary"] == (
                "metadata-only execution request; no external runtime call"
            )
            assert execution_request_body["handoff_payload"]["next_runtime"] == "future_guarded_runtime_adapter"
            assert "no publishing" in execution_request_body["handoff_payload"]["forbidden_actions"]
            assert execution_request_body["runbook"][0]["execution_boundary"] == "metadata-only; no external runtime call"
            assert execution_request_body["evidence_snapshot_ids"] == [evidence_snapshot_id]
            assert execution_request_body["operator_checklist"][0]["item"] == "Review approved evidence snapshot"
            assert execution_request_body["handoff_payload"]["evidence_snapshot_ids"] == [evidence_snapshot_id]

            execution_requests = await client.get(
                f"/api/v1/commercial-operations/{operation_id}/execution-requests",
                headers=headers,
            )
            assert execution_requests.status_code == 200
            assert [item["id"] for item in execution_requests.json()["items"]] == [execution_request_id]

            hidden_execution_requests = await client.get(
                f"/api/v1/commercial-operations/{operation_id}/execution-requests",
                headers={"X-Workspace-Id": "other-workspace"},
            )
            assert hidden_execution_requests.status_code == 404

            patched_execution_request = await client.patch(
                f"/api/v1/commercial-operations/{operation_id}/execution-requests/{execution_request_id}",
                headers=headers,
                json={
                    "title": "Newsletter execution handoff request",
                    "execution_target": "newsletter_platform_primary",
                    "readiness_checks": ["packaged deliverable", "manual target confirmed"],
                },
            )
            assert patched_execution_request.status_code == 200
            assert patched_execution_request.json()["title"] == "Newsletter execution handoff request"
            assert patched_execution_request.json()["request_status"] == "draft"
            assert patched_execution_request.json()["updated_by"] == "user-commercial-api"

            ready_execution_request = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/execution-requests/{execution_request_id}/ready",
                headers=headers,
                json={"reviewer_notes": "Ready for execution review."},
            )
            assert ready_execution_request.status_code == 200
            assert ready_execution_request.json()["request_status"] == "ready_for_review"

            approved_execution_request = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/execution-requests/{execution_request_id}/approve",
                headers=headers,
                json={"reviewer_notes": "Approved as metadata-only handoff."},
            )
            assert approved_execution_request.status_code == 200
            assert approved_execution_request.json()["request_status"] == "approved"
            assert approved_execution_request.json()["approved_by"] == "user-commercial-api"

            prepared_execution_request = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/execution-requests/{execution_request_id}/prepare",
                headers=headers,
                json={"result_summary": "Prepared for future guarded runtime adapter; no execution occurred."},
            )
            assert prepared_execution_request.status_code == 200
            assert prepared_execution_request.json()["request_status"] == "prepared"
            assert prepared_execution_request.json()["prepared_by"] == "user-commercial-api"

            fetched_after_execution_request = await client.get(
                f"/api/v1/commercial-operations/{operation_id}",
                headers=headers,
            )
            assert fetched_after_execution_request.status_code == 200
            execution_step = [
                step
                for step in fetched_after_execution_request.json()["plan_outline"]
                if step["step_key"] == "content_production"
            ][0]
            assert execution_step["execution_request_id"] == execution_request_id
            assert execution_step["execution_request_status"] == "prepared"
            assert execution_step["execution_request_mode"] == "metadata_only"
            assert execution_step["execution_request_target"] == "newsletter_platform_primary"
            assert execution_step["execution_request_evidence_snapshot_count"] == 1

            execution_run = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/execution-runs",
                headers=headers,
                json={
                    "execution_request_id": execution_request_id,
                    "title": "Newsletter metadata run",
                    "execution_target": "newsletter_platform_primary",
                    "input_payload": {"segment": "qualified_leads"},
                    "max_retries": 1,
                    "operator_notes": "Created for monitored handoff.",
                    "metadata": {"phase": "61I"},
                },
            )
            assert execution_run.status_code == 201
            execution_run_body = execution_run.json()
            execution_run_id = execution_run_body["id"]
            assert execution_run_body["workspace_id"] == "workspace-commercial-api"
            assert execution_run_body["operation_id"] == operation_id
            assert execution_run_body["execution_request_id"] == execution_request_id
            assert execution_run_body["deliverable_id"] == deliverable_id
            assert execution_run_body["output_artifact_id"] == output_artifact_id
            assert execution_run_body["run_status"] == "queued"
            assert execution_run_body["queued_by"] == "user-commercial-api"
            assert execution_run_body["input_payload"] == {"segment": "qualified_leads"}
            assert execution_run_body["runtime_payload"]["execution_boundary"] == (
                "metadata-only execution run; no external runtime call"
            )
            assert execution_run_body["runtime_payload"]["next_runtime"] == "future_guarded_runtime_adapter"
            assert "no OpenClaw action" in execution_run_body["runtime_payload"]["forbidden_actions"]
            assert execution_run_body["recovery_plan"]["max_retries"] == 1
            assert execution_run_body["evidence_snapshot_ids"] == [evidence_snapshot_id]
            assert execution_run_body["operator_checklist_snapshot"][0]["item"] == "Review approved evidence snapshot"
            assert execution_run_body["runtime_payload"]["evidence_snapshot_ids"] == [evidence_snapshot_id]

            execution_runs = await client.get(
                f"/api/v1/commercial-operations/{operation_id}/execution-runs",
                headers=headers,
            )
            assert execution_runs.status_code == 200
            assert [item["id"] for item in execution_runs.json()["items"]] == [execution_run_id]

            hidden_execution_runs = await client.get(
                f"/api/v1/commercial-operations/{operation_id}/execution-runs",
                headers={"X-Workspace-Id": "other-workspace"},
            )
            assert hidden_execution_runs.status_code == 404

            patched_execution_run = await client.patch(
                f"/api/v1/commercial-operations/{operation_id}/execution-runs/{execution_run_id}",
                headers=headers,
                json={
                    "execution_target": "newsletter_platform_backup",
                    "input_payload": {"segment": "qualified_leads", "variant": "A"},
                    "operator_notes": "Updated before start.",
                },
            )
            assert patched_execution_run.status_code == 200
            assert patched_execution_run.json()["execution_target"] == "newsletter_platform_backup"
            assert patched_execution_run.json()["input_payload"]["variant"] == "A"

            started_execution_run = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/execution-runs/{execution_run_id}/start",
                headers=headers,
                json={"operator_notes": "Started as metadata-only run."},
            )
            assert started_execution_run.status_code == 200
            assert started_execution_run.json()["run_status"] == "running"
            assert started_execution_run.json()["started_by"] == "user-commercial-api"

            succeeded_execution_run = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/execution-runs/{execution_run_id}/succeed",
                headers=headers,
                json={
                    "result_summary": "Operator confirmed handoff result.",
                    "result_payload": {"published": False, "handoff_complete": True},
                },
            )
            assert succeeded_execution_run.status_code == 200
            assert succeeded_execution_run.json()["run_status"] == "succeeded"
            assert succeeded_execution_run.json()["completed_by"] == "user-commercial-api"
            assert succeeded_execution_run.json()["result_payload"]["handoff_complete"] is True

            fetched_after_execution_run = await client.get(
                f"/api/v1/commercial-operations/{operation_id}",
                headers=headers,
            )
            assert fetched_after_execution_run.status_code == 200
            execution_run_step = [
                step
                for step in fetched_after_execution_run.json()["plan_outline"]
                if step["step_key"] == "content_production"
            ][0]
            assert execution_run_step["execution_run_id"] == execution_run_id
            assert execution_run_step["execution_run_status"] == "succeeded"
            assert execution_run_step["execution_run_target"] == "newsletter_platform_backup"

            commercial_result = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/results",
                headers=headers,
                json={
                    "execution_run_id": execution_run_id,
                    "title": "Newsletter commercial result",
                    "result_type": "operator_report",
                    "summary": "Operator confirmed the handoff result.",
                    "outcome_summary": "Observed lead signal captured manually.",
                    "observed_metrics": [{"name": "qualified_leads", "value": "3"}],
                    "commercial_signals": ["manual lead reply", "needs next content iteration"],
                    "evidence_links": [{"title": "Operator screenshot", "target_id": "screenshot-1"}],
                    "follow_up_actions": ["update audience segment"],
                    "metadata": {"phase": "61J"},
                },
            )
            assert commercial_result.status_code == 201
            commercial_result_body = commercial_result.json()
            commercial_result_id = commercial_result_body["id"]
            assert commercial_result_body["workspace_id"] == "workspace-commercial-api"
            assert commercial_result_body["operation_id"] == operation_id
            assert commercial_result_body["execution_run_id"] == execution_run_id
            assert commercial_result_body["execution_request_id"] == execution_request_id
            assert commercial_result_body["deliverable_id"] == deliverable_id
            assert commercial_result_body["output_artifact_id"] == output_artifact_id
            assert commercial_result_body["result_status"] == "draft"
            assert commercial_result_body["created_by"] == "user-commercial-api"
            assert commercial_result_body["observed_metrics"][0]["attribution_boundary"] == (
                "operator-reported; no platform analytics ingestion"
            )
            assert commercial_result_body["evidence_links"][0]["evidence_boundary"] == (
                "reference only; not fetched or verified automatically"
            )
            assert "does not claim ROI attribution" in commercial_result_body["recommendation_payload"]["non_goals"]

            commercial_results = await client.get(
                f"/api/v1/commercial-operations/{operation_id}/results",
                headers=headers,
            )
            assert commercial_results.status_code == 200
            assert [item["id"] for item in commercial_results.json()["items"]] == [commercial_result_id]

            hidden_commercial_results = await client.get(
                f"/api/v1/commercial-operations/{operation_id}/results",
                headers={"X-Workspace-Id": "other-workspace"},
            )
            assert hidden_commercial_results.status_code == 404

            patched_commercial_result = await client.patch(
                f"/api/v1/commercial-operations/{operation_id}/results/{commercial_result_id}",
                headers=headers,
                json={
                    "summary": "Updated operator result summary.",
                    "commercial_signals": ["manual lead reply"],
                    "follow_up_actions": ["prepare next iteration"],
                },
            )
            assert patched_commercial_result.status_code == 200
            assert patched_commercial_result.json()["summary"] == "Updated operator result summary."
            assert patched_commercial_result.json()["updated_by"] == "user-commercial-api"

            ready_commercial_result = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/results/{commercial_result_id}/ready",
                headers=headers,
                json={"reviewer_notes": "Ready for result review."},
            )
            assert ready_commercial_result.status_code == 200
            assert ready_commercial_result.json()["result_status"] == "ready_for_review"

            approved_commercial_result = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/results/{commercial_result_id}/approve",
                headers=headers,
                json={"reviewer_notes": "Approved as observed result only."},
            )
            assert approved_commercial_result.status_code == 200
            assert approved_commercial_result.json()["result_status"] == "approved"
            assert approved_commercial_result.json()["approved_by"] == "user-commercial-api"
            assert approved_commercial_result.json()["recommendation_payload"]["result_status"] == "approved"

            fetched_after_commercial_result = await client.get(
                f"/api/v1/commercial-operations/{operation_id}",
                headers=headers,
            )
            assert fetched_after_commercial_result.status_code == 200
            commercial_result_step = [
                step
                for step in fetched_after_commercial_result.json()["plan_outline"]
                if step["step_key"] == "content_production"
            ][0]
            assert commercial_result_step["commercial_result_id"] == commercial_result_id
            assert commercial_result_step["commercial_result_status"] == "approved"
            assert commercial_result_step["commercial_result_type"] == "operator_report"

            monitoring_observation = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/monitoring-observations",
                headers=headers,
                json={
                    "result_id": commercial_result_id,
                    "title": "Newsletter monitoring observation",
                    "observation_type": "manual_snapshot",
                    "metric_snapshots": [{"name": "reply_signal", "value": "1"}],
                    "qualitative_signals": ["operator observed reply"],
                    "evidence_links": [{"title": "Platform note", "target_id": "note-1"}],
                    "anomaly_flags": ["no automated analytics"],
                    "recommended_actions": ["prepare next audience segment"],
                    "metadata": {"phase": "61K"},
                },
            )
            assert monitoring_observation.status_code == 201
            monitoring_observation_body = monitoring_observation.json()
            monitoring_observation_id = monitoring_observation_body["id"]
            assert monitoring_observation_body["workspace_id"] == "workspace-commercial-api"
            assert monitoring_observation_body["operation_id"] == operation_id
            assert monitoring_observation_body["result_id"] == commercial_result_id
            assert monitoring_observation_body["execution_run_id"] == execution_run_id
            assert monitoring_observation_body["execution_request_id"] == execution_request_id
            assert monitoring_observation_body["deliverable_id"] == deliverable_id
            assert monitoring_observation_body["output_artifact_id"] == output_artifact_id
            assert monitoring_observation_body["observation_status"] == "draft"
            assert monitoring_observation_body["created_by"] == "user-commercial-api"
            assert monitoring_observation_body["metric_snapshots"][0]["attribution_boundary"] == (
                "operator-reported; no platform analytics ingestion"
            )
            assert monitoring_observation_body["evidence_links"][0]["evidence_boundary"] == (
                "reference only; not fetched or verified automatically"
            )
            assert "does not ingest platform analytics automatically" in monitoring_observation_body["observation_payload"]["non_goals"]

            monitoring_observations = await client.get(
                f"/api/v1/commercial-operations/{operation_id}/monitoring-observations",
                headers=headers,
            )
            assert monitoring_observations.status_code == 200
            assert [item["id"] for item in monitoring_observations.json()["items"]] == [monitoring_observation_id]

            hidden_monitoring_observations = await client.get(
                f"/api/v1/commercial-operations/{operation_id}/monitoring-observations",
                headers={"X-Workspace-Id": "other-workspace"},
            )
            assert hidden_monitoring_observations.status_code == 404

            patched_monitoring_observation = await client.patch(
                f"/api/v1/commercial-operations/{operation_id}/monitoring-observations/{monitoring_observation_id}",
                headers=headers,
                json={
                    "metric_snapshots": [{"name": "reply_signal", "value": "2"}],
                    "recommended_actions": ["prepare next iteration"],
                },
            )
            assert patched_monitoring_observation.status_code == 200
            assert patched_monitoring_observation.json()["updated_by"] == "user-commercial-api"
            assert patched_monitoring_observation.json()["metric_snapshots"][0]["value"] == "2"

            ready_monitoring_observation = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/monitoring-observations/{monitoring_observation_id}/ready",
                headers=headers,
                json={"reviewer_notes": "Ready for monitoring review."},
            )
            assert ready_monitoring_observation.status_code == 200
            assert ready_monitoring_observation.json()["observation_status"] == "ready_for_review"

            approved_monitoring_observation = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/monitoring-observations/{monitoring_observation_id}/approve",
                headers=headers,
                json={"reviewer_notes": "Approved as observed monitoring only."},
            )
            assert approved_monitoring_observation.status_code == 200
            assert approved_monitoring_observation.json()["observation_status"] == "approved"
            assert approved_monitoring_observation.json()["approved_by"] == "user-commercial-api"
            assert approved_monitoring_observation.json()["observation_payload"]["observation_status"] == "approved"

            fetched_after_monitoring_observation = await client.get(
                f"/api/v1/commercial-operations/{operation_id}",
                headers=headers,
            )
            assert fetched_after_monitoring_observation.status_code == 200
            monitoring_step = [
                step
                for step in fetched_after_monitoring_observation.json()["plan_outline"]
                if step["step_key"] == "content_production"
            ][0]
            assert monitoring_step["monitoring_observation_id"] == monitoring_observation_id
            assert monitoring_step["monitoring_observation_status"] == "approved"
            assert monitoring_step["monitoring_observation_type"] == "manual_snapshot"

            optimization_decision = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/optimization-decisions",
                headers=headers,
                json={
                    "observation_id": monitoring_observation_id,
                    "decision_type": "iterate",
                    "title": "Newsletter optimization decision",
                    "priority": "high",
                    "rationale": "Manual monitoring indicates the next content angle should be tested.",
                    "objective_updates": ["focus on qualified reply signal"],
                    "content_actions": ["revise proof point"],
                    "asset_actions": ["refresh hero visual brief"],
                    "audience_actions": ["review next segment"],
                    "execution_actions": ["prepare next manual handoff"],
                    "risk_controls": ["human approval before runtime"],
                    "metadata": {"phase": "61L"},
                },
            )
            assert optimization_decision.status_code == 201
            optimization_decision_body = optimization_decision.json()
            optimization_decision_id = optimization_decision_body["id"]
            assert optimization_decision_body["workspace_id"] == "workspace-commercial-api"
            assert optimization_decision_body["operation_id"] == operation_id
            assert optimization_decision_body["observation_id"] == monitoring_observation_id
            assert optimization_decision_body["result_id"] == commercial_result_id
            assert optimization_decision_body["execution_run_id"] == execution_run_id
            assert optimization_decision_body["execution_request_id"] == execution_request_id
            assert optimization_decision_body["deliverable_id"] == deliverable_id
            assert optimization_decision_body["output_artifact_id"] == output_artifact_id
            assert optimization_decision_body["decision_status"] == "draft"
            assert optimization_decision_body["decision_type"] == "iterate"
            assert optimization_decision_body["priority"] == "high"
            assert optimization_decision_body["created_by"] == "user-commercial-api"
            assert "does not auto-optimize" in optimization_decision_body["decision_payload"]["non_goals"][0]

            optimization_decisions = await client.get(
                f"/api/v1/commercial-operations/{operation_id}/optimization-decisions",
                headers=headers,
            )
            assert optimization_decisions.status_code == 200
            assert [item["id"] for item in optimization_decisions.json()["items"]] == [optimization_decision_id]

            hidden_optimization_decisions = await client.get(
                f"/api/v1/commercial-operations/{operation_id}/optimization-decisions",
                headers={"X-Workspace-Id": "other-workspace"},
            )
            assert hidden_optimization_decisions.status_code == 404

            patched_optimization_decision = await client.patch(
                f"/api/v1/commercial-operations/{operation_id}/optimization-decisions/{optimization_decision_id}",
                headers=headers,
                json={
                    "priority": "normal",
                    "rationale": "Updated rationale for manual optimization.",
                    "content_actions": ["revise CTA", "tighten proof point"],
                },
            )
            assert patched_optimization_decision.status_code == 200
            assert patched_optimization_decision.json()["updated_by"] == "user-commercial-api"
            assert patched_optimization_decision.json()["priority"] == "normal"
            assert patched_optimization_decision.json()["content_actions"] == ["revise CTA", "tighten proof point"]

            ready_optimization_decision = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/optimization-decisions/{optimization_decision_id}/ready",
                headers=headers,
                json={"reviewer_notes": "Ready for optimization review."},
            )
            assert ready_optimization_decision.status_code == 200
            assert ready_optimization_decision.json()["decision_status"] == "ready_for_review"

            approved_optimization_decision = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/optimization-decisions/{optimization_decision_id}/approve",
                headers=headers,
                json={"reviewer_notes": "Approved as manual optimization decision only."},
            )
            assert approved_optimization_decision.status_code == 200
            assert approved_optimization_decision.json()["decision_status"] == "approved"
            assert approved_optimization_decision.json()["approved_by"] == "user-commercial-api"
            assert approved_optimization_decision.json()["decision_payload"]["decision_status"] == "approved"

            fetched_after_optimization_decision = await client.get(
                f"/api/v1/commercial-operations/{operation_id}",
                headers=headers,
            )
            assert fetched_after_optimization_decision.status_code == 200
            optimization_step = [
                step
                for step in fetched_after_optimization_decision.json()["plan_outline"]
                if step["step_key"] == "content_production"
            ][0]
            assert optimization_step["optimization_decision_id"] == optimization_decision_id
            assert optimization_step["optimization_decision_status"] == "approved"
            assert optimization_step["optimization_decision_type"] == "iterate"

            reject_approved_optimization_decision = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/optimization-decisions/{optimization_decision_id}/reject",
                headers=headers,
                json={"reviewer_notes": "Too late to reject."},
            )
            assert reject_approved_optimization_decision.status_code == 400

            archived_optimization_decision = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/optimization-decisions/{optimization_decision_id}/archive",
                headers=headers,
                json={"reviewer_notes": "Archived after approval."},
            )
            assert archived_optimization_decision.status_code == 200
            assert archived_optimization_decision.json()["decision_status"] == "archived"

            patch_archived_optimization_decision = await client.patch(
                f"/api/v1/commercial-operations/{operation_id}/optimization-decisions/{optimization_decision_id}",
                headers=headers,
                json={"title": "Should not change."},
            )
            assert patch_archived_optimization_decision.status_code == 400

            reject_approved_monitoring_observation = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/monitoring-observations/{monitoring_observation_id}/reject",
                headers=headers,
                json={"reviewer_notes": "Too late to reject."},
            )
            assert reject_approved_monitoring_observation.status_code == 400

            archived_monitoring_observation = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/monitoring-observations/{monitoring_observation_id}/archive",
                headers=headers,
                json={"reviewer_notes": "Archived after approval."},
            )
            assert archived_monitoring_observation.status_code == 200
            assert archived_monitoring_observation.json()["observation_status"] == "archived"

            patch_archived_monitoring_observation = await client.patch(
                f"/api/v1/commercial-operations/{operation_id}/monitoring-observations/{monitoring_observation_id}",
                headers=headers,
                json={"title": "Should not change."},
            )
            assert patch_archived_monitoring_observation.status_code == 400

            reject_approved_commercial_result = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/results/{commercial_result_id}/reject",
                headers=headers,
                json={"reviewer_notes": "Too late to reject."},
            )
            assert reject_approved_commercial_result.status_code == 400

            archived_commercial_result = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/results/{commercial_result_id}/archive",
                headers=headers,
                json={"reviewer_notes": "Archived after approval."},
            )
            assert archived_commercial_result.status_code == 200
            assert archived_commercial_result.json()["result_status"] == "archived"

            patch_archived_commercial_result = await client.patch(
                f"/api/v1/commercial-operations/{operation_id}/results/{commercial_result_id}",
                headers=headers,
                json={"summary": "Should not change."},
            )
            assert patch_archived_commercial_result.status_code == 400

            fail_after_succeeded_execution_run = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/execution-runs/{execution_run_id}/fail",
                headers=headers,
                json={"failure_reason": "Too late to fail after success."},
            )
            assert fail_after_succeeded_execution_run.status_code == 400

            archived_execution_run = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/execution-runs/{execution_run_id}/archive",
                headers=headers,
                json={"operator_notes": "Archived after success."},
            )
            assert archived_execution_run.status_code == 200
            assert archived_execution_run.json()["run_status"] == "archived"

            patch_archived_execution_run = await client.patch(
                f"/api/v1/commercial-operations/{operation_id}/execution-runs/{execution_run_id}",
                headers=headers,
                json={"title": "Should not change."},
            )
            assert patch_archived_execution_run.status_code == 400

            retry_execution_run = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/execution-runs",
                headers=headers,
                json={
                    "execution_request_id": execution_request_id,
                    "title": "Newsletter retryable metadata run",
                    "max_retries": 1,
                    "input_payload": {"segment": "retry"},
                },
            )
            assert retry_execution_run.status_code == 201
            retry_execution_run_id = retry_execution_run.json()["id"]

            started_retry_execution_run = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/execution-runs/{retry_execution_run_id}/start",
                headers=headers,
                json={},
            )
            assert started_retry_execution_run.status_code == 200
            failed_retry_execution_run = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/execution-runs/{retry_execution_run_id}/fail",
                headers=headers,
                json={"failure_reason": "Operator target unavailable.", "result_payload": {"retryable": True}},
            )
            assert failed_retry_execution_run.status_code == 200
            assert failed_retry_execution_run.json()["run_status"] == "failed"
            assert failed_retry_execution_run.json()["failure_reason"] == "Operator target unavailable."
            assert failed_retry_execution_run.json()["recovery_plan"]["can_retry"] is True

            retried_execution_run = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/execution-runs/{retry_execution_run_id}/retry",
                headers=headers,
                json={"operator_notes": "Retry after operator correction."},
            )
            assert retried_execution_run.status_code == 200
            assert retried_execution_run.json()["run_status"] == "retrying"
            assert retried_execution_run.json()["retry_count"] == 1

            restarted_execution_run = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/execution-runs/{retry_execution_run_id}/start",
                headers=headers,
                json={},
            )
            assert restarted_execution_run.status_code == 200
            assert restarted_execution_run.json()["run_status"] == "running"

            running_result = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/results",
                headers=headers,
                json={
                    "execution_run_id": retry_execution_run_id,
                    "title": "Invalid running result",
                },
            )
            assert running_result.status_code == 400

            cancelled_execution_run = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/execution-runs/{retry_execution_run_id}/cancel",
                headers=headers,
                json={"operator_notes": "Cancelled after retry start."},
            )
            assert cancelled_execution_run.status_code == 200
            assert cancelled_execution_run.json()["run_status"] == "cancelled"
            assert cancelled_execution_run.json()["cancelled_by"] == "user-commercial-api"

            fail_after_prepared_execution_request = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/execution-requests/{execution_request_id}/fail",
                headers=headers,
                json={"failure_reason": "Too late to fail after preparation."},
            )
            assert fail_after_prepared_execution_request.status_code == 400

            archived_execution_request = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/execution-requests/{execution_request_id}/archive",
                headers=headers,
                json={"reviewer_notes": "Archived after preparation."},
            )
            assert archived_execution_request.status_code == 200
            assert archived_execution_request.json()["request_status"] == "archived"

            patch_archived_execution_request = await client.patch(
                f"/api/v1/commercial-operations/{operation_id}/execution-requests/{execution_request_id}",
                headers=headers,
                json={"title": "Should not change."},
            )
            assert patch_archived_execution_request.status_code == 400

            invalid_execution_run = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/execution-runs",
                headers=headers,
                json={
                    "execution_request_id": execution_request_id,
                    "title": "Invalid run from archived request",
                },
            )
            assert invalid_execution_run.status_code == 400

            fail_after_packaged_deliverable = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/deliverables/{deliverable_id}/fail",
                headers=headers,
                json={"failure_reason": "Too late to fail."},
            )
            assert fail_after_packaged_deliverable.status_code == 400

            archived_deliverable = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/deliverables/{deliverable_id}/archive",
                headers=headers,
                json={"reviewer_notes": "Archived after packaging."},
            )
            assert archived_deliverable.status_code == 200
            assert archived_deliverable.json()["deliverable_status"] == "archived"

            invalid_execution_request = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/execution-requests",
                headers=headers,
                json={
                    "deliverable_id": deliverable_id,
                    "title": "Invalid execution request from archived deliverable",
                },
            )
            assert invalid_execution_request.status_code == 400

            patch_archived_deliverable = await client.patch(
                f"/api/v1/commercial-operations/{operation_id}/deliverables/{deliverable_id}",
                headers=headers,
                json={"summary": "Should not change."},
            )
            assert patch_archived_deliverable.status_code == 400

            invalid_deliverable = await client.post(
                f"/api/v1/commercial-operations/{operation_id}/deliverables",
                headers=headers,
                json={
                    "step_key": "missing_step",
                    "content_draft_id": content_draft_id,
                    "title": "Invalid deliverable step",
                },
            )
            assert invalid_deliverable.status_code == 400

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
