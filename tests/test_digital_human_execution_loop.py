"""Digital human execution loop tests."""

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


async def _create_approved_job(
    session: AsyncSession,
    service: DigitalHumanService,
    *,
    workspace_id: str,
):
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
    created = await service.create_video_job(
        session,
        workspace_id=workspace_id,
        user_id="user-digital-human",
        objective="Create a product launch digital human video",
        script="Open with the pain point, show proof, and ask viewers to book.",
        avatar_asset_id=portrait.id,
        target_channels=["douyin"],
        duration_seconds=12,
    )
    approved = await service.update_video_job_review(
        session,
        workspace_id=workspace_id,
        job_id=created.id,
        action="approve",
    )
    return portrait, approved


@pytest.mark.asyncio
async def test_digital_human_mock_execution_creates_delivery_asset(
    session: AsyncSession,
    tmp_path: Path,
) -> None:
    service = DigitalHumanService(
        settings=Settings(
            DIGITAL_HUMAN_ASSET_DIR=str(tmp_path / "assets"),
            DIGITAL_HUMAN_OUTPUT_DIR=str(tmp_path / "outputs"),
        )
    )
    _, approved = await _create_approved_job(
        session,
        service,
        workspace_id="workspace-digital-human-mock-execute",
    )

    executed = await service.execute_video_job(
        session,
        workspace_id="workspace-digital-human-mock-execute",
        job_id=approved.id,
        execution_mode="mock_render",
        metadata={"commercial_operation_id": "operation-123"},
    )
    generated_assets = await service.list_assets(
        session,
        workspace_id="workspace-digital-human-mock-execute",
        asset_type="video",
    )

    assert executed.job_status == "completed"
    assert executed.execution_mode == "mock_render"
    assert executed.progress_percent == 100
    assert executed.current_stage == "delivery_ready"
    assert executed.external_request_attempted is False
    assert executed.outputs[0]["output_type"] == "digital_human_delivery_manifest"
    assert executed.outputs[0]["commercial_operation_id"] == "operation-123"
    assert Path(str(executed.outputs[0]["source_uri"])).exists()
    assert len(generated_assets.items) == 1
    assert generated_assets.items[0].asset_type == "video"


@pytest.mark.asyncio
async def test_digital_human_comfyui_handoff_creates_guarded_video_job(
    session: AsyncSession,
    tmp_path: Path,
) -> None:
    service = DigitalHumanService(
        settings=Settings(
            DIGITAL_HUMAN_ASSET_DIR=str(tmp_path / "assets"),
            DIGITAL_HUMAN_OUTPUT_DIR=str(tmp_path / "outputs"),
        )
    )
    _, approved = await _create_approved_job(
        session,
        service,
        workspace_id="workspace-digital-human-comfyui-handoff",
    )

    executed = await service.execute_video_job(
        session,
        workspace_id="workspace-digital-human-comfyui-handoff",
        job_id=approved.id,
        execution_mode="comfyui_handoff",
        submit_immediately=False,
        metadata={"commercial_operation_id": "operation-456"},
    )
    result = await session.execute(
        select(ComfyUIRuntimeVideoJob).where(
            ComfyUIRuntimeVideoJob.workspace_id == "workspace-digital-human-comfyui-handoff"
        )
    )
    comfyui_job = result.scalar_one()

    assert executed.job_status == "queued_for_comfyui"
    assert executed.execution_mode == "comfyui_handoff"
    assert executed.progress_percent == 60
    assert executed.current_stage == "comfyui_video_queue"
    assert executed.linked_comfyui_video_job_id == str(comfyui_job.id)
    assert executed.outputs[0]["output_type"] == "comfyui_video_job"
    assert executed.outputs[0]["comfyui_video_job_id"] == str(comfyui_job.id)
    assert executed.outputs[0]["resource_plan"]["admission_status"] == "blocked"
    assert comfyui_job.job_status == "resource_blocked"
    assert comfyui_job.external_request_attempted is False
    assert comfyui_job.prompt_submission_enabled is False


@pytest.mark.asyncio
async def test_digital_human_execute_requires_approval(
    session: AsyncSession,
    tmp_path: Path,
) -> None:
    service = DigitalHumanService(settings=Settings(DIGITAL_HUMAN_ASSET_DIR=str(tmp_path / "assets")))
    portrait = await service.create_asset(
        session,
        workspace_id="workspace-digital-human-execute-gate",
        user_id="user-digital-human",
        asset_type="portrait",
        name="Authorized portrait",
        file_name="portrait.jpg",
        mime_type="image/jpeg",
        content=b"fake-image-bytes",
        consent_status="authorized",
    )
    created = await service.create_video_job(
        session,
        workspace_id="workspace-digital-human-execute-gate",
        user_id="user-digital-human",
        objective="Create a video",
        script="Short script",
        avatar_asset_id=portrait.id,
    )

    with pytest.raises(AppError, match="Only approved digital human jobs can be executed"):
        await service.execute_video_job(
            session,
            workspace_id="workspace-digital-human-execute-gate",
            job_id=created.id,
            execution_mode="mock_render",
        )


@pytest.mark.asyncio
async def test_digital_human_execute_api(tmp_path: Path) -> None:
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
    headers = {"X-Workspace-Id": "workspace-digital-human-execute-api", "X-User-Id": "user-api"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        portrait = await client.post(
            "/api/v1/digital-humans/assets",
            headers=headers,
            data={"asset_type": "portrait", "name": "API portrait", "consent_status": "authorized"},
            files={"file": ("portrait.jpg", b"fake-image", "image/jpeg")},
        )
        created = await client.post(
            "/api/v1/digital-humans/video-jobs",
            headers=headers,
            json={
                "objective": "Create digital human launch video",
                "script": "Introduce the product and ask viewers to book.",
                "avatar_asset_id": portrait.json()["id"],
            },
        )
        approved = await client.post(
            f"/api/v1/digital-humans/video-jobs/{created.json()['id']}/approve",
            headers=headers,
            json={"reviewer_notes": "Ready"},
        )
        executed = await client.post(
            f"/api/v1/digital-humans/video-jobs/{created.json()['id']}/execute",
            headers=headers,
            json={"execution_mode": "mock_render", "metadata": {"commercial_operation_id": "operation-api"}},
        )

    assert approved.status_code == 200
    assert executed.status_code == 200
    assert executed.json()["job_status"] == "completed"
    assert executed.json()["progress_percent"] == 100
    assert executed.json()["outputs"][0]["commercial_operation_id"] == "operation-api"

    await engine.dispose()
