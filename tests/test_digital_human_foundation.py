"""Digital human production foundation tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.api.router import create_api_router
from app.core.config import Settings, get_settings
from app.core.errors import AppError, app_error_handler
from app.db.base import Base
from app.db.postgres import get_session
from app.digital_humans import DigitalHumanService
from app.models import DigitalHumanAsset, DigitalHumanVideoJob


def test_digital_human_capabilities_are_plan_only_by_default() -> None:
    service = DigitalHumanService(settings=Settings())

    capabilities = service.capabilities(workspace_id="workspace-digital-human")

    assert capabilities.provider == "mock"
    assert capabilities.enabled is False
    assert capabilities.external_api_allowed is False
    assert capabilities.provider_calls_enabled is False
    assert "heygen" in capabilities.available_providers
    assert "tavus" in capabilities.available_providers
    assert "local_musetalk_liveportrait" in capabilities.available_providers
    assert "execute_digital_human_provider" in capabilities.disabled_actions
    assert capabilities.raw["no_external_call_performed"] is True


@pytest.mark.asyncio
async def test_digital_human_service_uploads_assets_and_creates_video_job(
    session: AsyncSession,
    tmp_path: Path,
) -> None:
    service = DigitalHumanService(settings=Settings(DIGITAL_HUMAN_ASSET_DIR=str(tmp_path)))

    portrait = await service.create_asset(
        session,
        workspace_id="workspace-digital-human-service",
        user_id="user-digital-human",
        asset_type="portrait",
        name="Founder portrait",
        file_name="founder.jpg",
        mime_type="image/jpeg",
        content=b"fake-image-bytes",
        consent_status="authorized",
        usage_scope="commercial operation avatar",
    )
    material = await service.create_asset(
        session,
        workspace_id="workspace-digital-human-service",
        user_id="user-digital-human",
        asset_type="material",
        name="Product hero",
        file_name="product.png",
        mime_type="image/png",
        content=b"fake-product-bytes",
        consent_status="authorized",
    )

    job = await service.create_video_job(
        session,
        workspace_id="workspace-digital-human-service",
        user_id="user-digital-human",
        objective="Launch a product video",
        script="Introduce the product, show proof, and ask users to book a demo.",
        avatar_asset_id=portrait.id,
        material_asset_ids=[material.id],
        target_channels=["douyin", "xiaohongshu"],
        voice_profile={"voice_id": "zh-CN-default"},
    )
    refreshed = await service.refresh_video_job(
        session,
        workspace_id="workspace-digital-human-service",
        job_id=job.id,
    )
    approved = await service.update_video_job_review(
        session,
        workspace_id="workspace-digital-human-service",
        job_id=job.id,
        action="approve",
    )

    assert Path(portrait.source_uri).exists()
    assert portrait.asset_type == "portrait"
    assert portrait.consent_status == "authorized"
    assert material.asset_type == "material"
    assert job.job_status == "planned"
    assert job.provider == "mock"
    assert job.execution_mode == "plan_only"
    assert job.consent_status == "authorized"
    assert job.external_request_attempted is False
    assert job.provider_calls_enabled is False
    assert {step["step"] for step in job.scene_plan} >= {"asset_intake", "avatar_motion", "ffmpeg_compose"}
    assert "provider=mock" in str(job.result_summary)
    assert refreshed.job_status == "planned"
    assert refreshed.provider_response["external_request_attempted"] is False
    assert approved.job_status == "approved"
    assert approved.approval_status == "approved"


@pytest.mark.asyncio
async def test_digital_human_video_job_requires_authorized_portrait(
    session: AsyncSession,
    tmp_path: Path,
) -> None:
    service = DigitalHumanService(settings=Settings(DIGITAL_HUMAN_ASSET_DIR=str(tmp_path)))
    portrait = await service.create_asset(
        session,
        workspace_id="workspace-digital-human-consent",
        user_id="user-digital-human",
        asset_type="portrait",
        name="Unverified portrait",
        file_name="portrait.jpg",
        mime_type="image/jpeg",
        content=b"fake-image-bytes",
        consent_status="unverified",
    )

    job = await service.create_video_job(
        session,
        workspace_id="workspace-digital-human-consent",
        user_id="user-digital-human",
        objective="Create talking head video",
        script="Short script",
        avatar_asset_id=portrait.id,
    )

    assert job.job_status == "needs_consent"
    assert job.consent_status == "unverified"
    assert "authorized consent is required" in str(job.failure_reason)


@pytest.mark.asyncio
async def test_digital_human_api_upload_create_refresh_and_review(tmp_path: Path) -> None:
    _ = (DigitalHumanAsset, DigitalHumanVideoJob)
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    settings = Settings(DIGITAL_HUMAN_ASSET_DIR=str(tmp_path))

    app = FastAPI()
    app.add_exception_handler(AppError, app_error_handler)
    app.include_router(create_api_router())

    async def override_get_session():  # type: ignore[no-untyped-def]
        async with session_factory() as db_session:
            yield db_session

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_settings] = lambda: settings
    headers = {"X-Workspace-Id": "workspace-digital-human-api", "X-User-Id": "user-digital-human-api"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        capabilities = await client.get("/api/v1/digital-humans/capabilities", headers=headers)
        portrait = await client.post(
            "/api/v1/digital-humans/assets",
            headers=headers,
            data={
                "asset_type": "portrait",
                "name": "API portrait",
                "consent_status": "authorized",
                "usage_scope": "commercial avatar",
            },
            files={"file": ("portrait.jpg", b"fake-image", "image/jpeg")},
        )
        material = await client.post(
            "/api/v1/digital-humans/assets",
            headers=headers,
            data={"asset_type": "material", "name": "API material", "consent_status": "authorized"},
            files={"file": ("material.png", b"fake-material", "image/png")},
        )
        created = await client.post(
            "/api/v1/digital-humans/video-jobs",
            headers=headers,
            json={
                "objective": "Create a product explainer digital human video",
                "script": "Hello, this is the product. Here is why it matters.",
                "avatar_asset_id": portrait.json()["id"],
                "material_asset_ids": [material.json()["id"]],
                "target_channels": ["douyin"],
                "voice_profile": {"voice_id": "zh-CN-default"},
            },
        )
        listed = await client.get("/api/v1/digital-humans/video-jobs?limit=5", headers=headers)
        refreshed = await client.post(
            f"/api/v1/digital-humans/video-jobs/{created.json()['id']}/refresh",
            headers=headers,
            json={},
        )
        approved = await client.post(
            f"/api/v1/digital-humans/video-jobs/{created.json()['id']}/approve",
            headers=headers,
            json={"reviewer_notes": "Ready for next execution phase"},
        )

    assert capabilities.status_code == 200
    assert portrait.status_code == 200
    assert material.status_code == 200
    assert created.status_code == 200
    assert created.json()["job_status"] == "planned"
    assert created.json()["external_request_attempted"] is False
    assert listed.status_code == 200
    assert len(listed.json()["items"]) == 1
    assert refreshed.status_code == 200
    assert refreshed.json()["job_status"] == "planned"
    assert approved.status_code == 200
    assert approved.json()["approval_status"] == "approved"

    await engine.dispose()
