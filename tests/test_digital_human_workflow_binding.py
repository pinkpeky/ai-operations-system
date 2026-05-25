"""Digital human ComfyUI workflow binding tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.api.router import create_api_router
from app.core.config import Settings, get_settings
from app.core.errors import AppError, app_error_handler
from app.db.base import Base
from app.db.postgres import get_session
from app.digital_humans import DigitalHumanService
from app.models import ComfyUIRuntimeVideoJob, DigitalHumanAsset, DigitalHumanVideoJob


async def _create_approved_workflow_job(
    session: AsyncSession,
    service: DigitalHumanService,
    *,
    workspace_id: str,
) -> tuple[DigitalHumanAsset, DigitalHumanAsset, object]:
    portrait = await service.create_asset(
        session,
        workspace_id=workspace_id,
        user_id="user-digital-human",
        asset_type="portrait",
        name="Authorized portrait",
        file_name="portrait.jpg",
        mime_type="image/jpeg",
        content=b"fake-image-bytes",
        consent_status="authorized",
    )
    material = await service.create_asset(
        session,
        workspace_id=workspace_id,
        user_id="user-digital-human",
        asset_type="material",
        name="Product material",
        file_name="product.png",
        mime_type="image/png",
        content=b"fake-product-bytes",
        consent_status="authorized",
    )
    created = await service.create_video_job(
        session,
        workspace_id=workspace_id,
        user_id="user-digital-human",
        objective="Create a product launch digital human video",
        script="Open with the pain point, show proof, and ask viewers to book.",
        avatar_asset_id=portrait.id,
        material_asset_ids=[material.id],
        target_channels=["douyin"],
        duration_seconds=12,
    )
    approved = await service.update_video_job_review(
        session,
        workspace_id=workspace_id,
        job_id=created.id,
        action="approve",
    )
    return portrait, material, approved


def test_digital_human_workflow_templates_are_visible_without_runtime_calls() -> None:
    service = DigitalHumanService(settings=Settings())

    capabilities = service.capabilities(workspace_id="workspace-digital-human-workflows")
    templates = service.list_workflow_templates(workspace_id="workspace-digital-human-workflows")
    template = service.get_workflow_template(template_id="liveportrait-musetalk-broll")

    template_ids = {item.template_id for item in templates.items}
    assert "liveportrait-musetalk-broll" in template_ids
    assert "wan-i2v-reference-avatar" in template_ids
    assert capabilities.raw["phase"] == "67C"
    assert "liveportrait-musetalk-broll" in capabilities.raw["workflow_template_ids"]
    assert template.provider == "comfyui"
    assert template.default_resource_profile == "standard"
    assert template.recommended_vram_mb == 12288
    assert "ComfyUI-MuseTalk" in template.required_nodes
    assert template.prompt_contract["submission_policy"].startswith("requires operator-imported graph")
    assert template.metadata["no_external_call_performed"] is True


@pytest.mark.asyncio
async def test_bind_comfyui_workflow_creates_reviewable_input_contract(
    session: AsyncSession,
    tmp_path: Path,
) -> None:
    service = DigitalHumanService(
        settings=Settings(
            DIGITAL_HUMAN_ASSET_DIR=str(tmp_path / "assets"),
            DIGITAL_HUMAN_OUTPUT_DIR=str(tmp_path / "outputs"),
        )
    )
    _, material, approved = await _create_approved_workflow_job(
        session,
        service,
        workspace_id="workspace-digital-human-workflow-binding",
    )

    bound = await service.bind_comfyui_workflow(
        session,
        workspace_id="workspace-digital-human-workflow-binding",
        job_id=approved.id,
        template_id="liveportrait-musetalk-broll",
        material_asset_ids=[material.id],
        resource_profile="standard",
        estimated_vram_mb=12288,
        operator_parameters={"motion_strength": 0.4},
        operator_note="Bind inputs before importing the real graph.",
        metadata={"commercial_operation_id": "operation-workflow-binding"},
    )

    binding = bound.metadata["comfyui_workflow_binding"]
    output = next(item for item in bound.outputs if item["output_type"] == "digital_human_comfyui_input_binding")
    assert bound.job_status == "approved"
    assert bound.selected_workflow_template_id == "liveportrait-musetalk-broll"
    assert bound.workflow_binding_status == "ready_for_operator_review"
    assert bound.external_request_attempted is False
    assert bound.provider_response["phase"] == "67C"
    assert bound.result_summary == "ComfyUI workflow inputs are bound and ready for operator graph verification."
    assert binding["phase"] == "67C"
    assert binding["status"] == "ready_for_operator_review"
    assert binding["resource_plan"]["estimated_vram_mb"] == 12288
    assert binding["operator_parameters"]["motion_strength"] == 0.4
    assert binding["submit_policy"] == "operator_must_import_real_graph_then_enable_guarded_runtime"
    assert any(asset["slot"] == "avatar_portrait" for asset in binding["input_assets"])
    assert any(asset["asset_id"] == str(material.id) for asset in binding["input_assets"])
    assert output["workflow_template_id"] == "liveportrait-musetalk-broll"
    assert "ComfyUI-AdvancedLivePortrait" in output["required_nodes"]


@pytest.mark.asyncio
async def test_bound_workflow_handoff_uses_binding_contract_without_prompt_submission(
    session: AsyncSession,
    tmp_path: Path,
) -> None:
    service = DigitalHumanService(
        settings=Settings(
            DIGITAL_HUMAN_ASSET_DIR=str(tmp_path / "assets"),
            DIGITAL_HUMAN_OUTPUT_DIR=str(tmp_path / "outputs"),
        )
    )
    _, material, approved = await _create_approved_workflow_job(
        session,
        service,
        workspace_id="workspace-digital-human-bound-handoff",
    )
    bound = await service.bind_comfyui_workflow(
        session,
        workspace_id="workspace-digital-human-bound-handoff",
        job_id=approved.id,
        template_id="liveportrait-musetalk-broll",
        material_asset_ids=[material.id],
        resource_profile="standard",
        estimated_vram_mb=12288,
    )

    executed = await service.execute_video_job(
        session,
        workspace_id="workspace-digital-human-bound-handoff",
        job_id=bound.id,
        execution_mode="comfyui_handoff",
        submit_immediately=True,
        metadata={"commercial_operation_id": "operation-bound-handoff"},
    )
    result = await session.execute(
        select(ComfyUIRuntimeVideoJob).where(
            ComfyUIRuntimeVideoJob.workspace_id == "workspace-digital-human-bound-handoff"
        )
    )
    comfyui_job = result.scalar_one()

    assert executed.job_status == "queued_for_comfyui"
    assert executed.selected_workflow_template_id == "liveportrait-musetalk-broll"
    assert executed.workflow_binding_status == "ready_for_operator_review"
    assert executed.provider_response["phase"] == "67C"
    assert executed.provider_response["generated_prompt_submission_skipped"] is True
    assert comfyui_job.prompt["aiops_bound_digital_human_workflow"]["inputs"]["template_id"] == "liveportrait-musetalk-broll"
    assert comfyui_job.workflow["template_id"] == "liveportrait-musetalk-broll"
    assert comfyui_job.extra_data["digital_human"]["workflow_template_id"] == "liveportrait-musetalk-broll"
    assert comfyui_job.job_metadata["phase"] == "67C"
    assert comfyui_job.prompt_submission_enabled is False
    assert comfyui_job.external_request_attempted is False


@pytest.mark.asyncio
async def test_digital_human_workflow_binding_api(tmp_path: Path) -> None:
    _ = (DigitalHumanAsset, DigitalHumanVideoJob, ComfyUIRuntimeVideoJob)
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    settings = Settings(
        DIGITAL_HUMAN_ASSET_DIR=str(tmp_path / "assets"),
        DIGITAL_HUMAN_OUTPUT_DIR=str(tmp_path / "outputs"),
    )

    app = FastAPI()
    app.add_exception_handler(AppError, app_error_handler)
    app.include_router(create_api_router())

    async def override_get_session():  # type: ignore[no-untyped-def]
        async with session_factory() as db_session:
            yield db_session

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_settings] = lambda: settings
    headers = {"X-Workspace-Id": "workspace-digital-human-workflow-api", "X-User-Id": "user-api"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        templates = await client.get("/api/v1/digital-humans/workflow-templates", headers=headers)
        template = await client.get(
            "/api/v1/digital-humans/workflow-templates/liveportrait-musetalk-broll",
            headers=headers,
        )
        portrait = await client.post(
            "/api/v1/digital-humans/assets",
            headers=headers,
            data={"asset_type": "portrait", "name": "API portrait", "consent_status": "authorized"},
            files={"file": ("portrait.jpg", b"fake-image", "image/jpeg")},
        )
        material = await client.post(
            "/api/v1/digital-humans/assets",
            headers=headers,
            data={"asset_type": "material", "name": "API product", "consent_status": "authorized"},
            files={"file": ("product.png", b"fake-product", "image/png")},
        )
        created = await client.post(
            "/api/v1/digital-humans/video-jobs",
            headers=headers,
            json={
                "objective": "Create digital human launch video",
                "script": "Introduce the product and ask viewers to book.",
                "avatar_asset_id": portrait.json()["id"],
                "material_asset_ids": [material.json()["id"]],
            },
        )
        await client.post(
            f"/api/v1/digital-humans/video-jobs/{created.json()['id']}/approve",
            headers=headers,
            json={"reviewer_notes": "Ready"},
        )
        bound = await client.post(
            f"/api/v1/digital-humans/video-jobs/{created.json()['id']}/workflow-binding",
            headers=headers,
            json={
                "template_id": "liveportrait-musetalk-broll",
                "material_asset_ids": [material.json()["id"]],
                "metadata": {"commercial_operation_id": "operation-api-workflow"},
            },
        )

    assert templates.status_code == 200
    assert any(item["template_id"] == "liveportrait-musetalk-broll" for item in templates.json()["items"])
    assert template.status_code == 200
    assert template.json()["workflow_kind"] == "portrait_photo_script_to_short_video"
    assert bound.status_code == 200
    assert bound.json()["selected_workflow_template_id"] == "liveportrait-musetalk-broll"
    assert bound.json()["workflow_binding_status"] == "ready_for_operator_review"
    assert bound.json()["outputs"][0]["output_type"] == "digital_human_comfyui_input_binding"

    await engine.dispose()
