"""Digital human production foundation tests."""

from __future__ import annotations

import json
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
from app.schemas.llm import LLMRequest, LLMResponse


class FakeCreativeLLMClient:
    """Records the digital-human planning prompt and returns a structured director plan."""

    def __init__(self) -> None:
        self.last_request: LLMRequest | None = None

    async def generate(self, request: LLMRequest) -> LLMResponse:
        self.last_request = request
        return LLMResponse(
            provider="local",
            model="llama70b",
            content=json.dumps(
                {
                    "production_intent": {
                        "positioning": "商务 KTV 高端运营宣传片",
                        "target_audience": "商务接待用户",
                        "narrative_angle": "90 后老板娘的开门前巡场故事",
                        "value_proposition": "把客户接待的细节提前安排好",
                    },
                    "character_bible": {
                        "identity_role": "KTV 经营者",
                        "personality": "真实、克制、专业",
                        "visual_identity": "统一女性经营者形象",
                        "wardrobe": "高质感浅色通勤礼服",
                        "continuity_rules": ["same face", "same wardrobe", "same venue logic"],
                    },
                    "voiceover": {
                        "final_script": "开门前，我会先检查包厢气味、灯光和音响。",
                        "tone": "自然经营者口播",
                        "pacing": "medium slow",
                        "ai_voice_avoidance": ["avoid ad tone"],
                    },
                    "story_beats": ["巡场", "检查细节", "接待承诺"],
                    "shot_plan": [
                        {
                            "shot_id": "S01",
                            "duration_seconds": 3.5,
                            "scene_goal": "建立真实高端包厢环境",
                            "camera": "slow push in",
                            "visual_prompt": "realistic premium KTV room, preserve reference lighting",
                            "negative_prompt": "raw montage, identity drift",
                            "reference_asset_usage": "use uploaded venue image as layout and lighting reference",
                            "character_continuity": "same operator appears later",
                            "audio_line": "很多人以为商务 KTV 拼的是装修。",
                            "quality_checks": ["scene continuity", "premium realism"],
                        }
                    ],
                    "asset_strategy": {
                        "material_reference_policy": "素材只作空间、灯光和质感参考",
                        "generated_scene_policy": "生成连贯新镜头",
                        "no_raw_montage_rule": "不得直接拼接素材当成成片",
                    },
                    "comfyui_plan": {
                        "recommended_template": "wan-i2v-reference-avatar",
                        "model_family": "Wan I2V + MuseTalk",
                        "resolution": "1080x1920",
                        "fps": 24,
                        "generation_passes": ["identity lock", "scene generation", "lip sync"],
                    },
                    "quality_gates": ["人物统一", "镜头连贯", "声音自然"],
                    "risk_notes": ["需要更多全身参考提升一致性"],
                    "approval_checklist": ["确认角色", "确认分镜", "确认声音"],
                },
                ensure_ascii=False,
            ),
        )


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
async def test_digital_human_video_job_can_use_llm_creative_planning(
    session: AsyncSession,
    tmp_path: Path,
) -> None:
    llm_client = FakeCreativeLLMClient()
    service = DigitalHumanService(
        settings=Settings(DIGITAL_HUMAN_ASSET_DIR=str(tmp_path)),
        llm_client=llm_client,
    )
    portrait = await service.create_asset(
        session,
        workspace_id="workspace-digital-human-llm-plan",
        user_id="user-digital-human",
        asset_type="portrait",
        name="KTV owner portrait",
        file_name="owner.jpg",
        mime_type="image/jpeg",
        content=b"fake-image-bytes",
        consent_status="authorized",
    )
    material = await service.create_asset(
        session,
        workspace_id="workspace-digital-human-llm-plan",
        user_id="user-digital-human",
        asset_type="material",
        name="KTV room reference",
        file_name="room.png",
        mime_type="image/png",
        content=b"fake-material-bytes",
        consent_status="authorized",
    )

    job = await service.create_video_job(
        session,
        workspace_id="workspace-digital-human-llm-plan",
        user_id="user-digital-human",
        objective="商务 KTV 宣传视频",
        script="请生成老板娘经营日常风格的真实宣传片。",
        avatar_asset_id=portrait.id,
        material_asset_ids=[material.id],
        target_channels=["douyin"],
        duration_seconds=30,
        llm_planning_enabled=True,
        planning_context={"style": "真实高级", "requirement": "人物统一，素材只作参考"},
    )

    assert llm_client.last_request is not None
    assert "required_json_schema" in llm_client.last_request.user_prompt
    assert "人物统一" in llm_client.last_request.user_prompt
    assert job.provider_response["creative_planning"]["enabled"] is True
    assert job.provider_response["creative_planning"]["provider"] == "local"
    assert job.provider_response["creative_planning"]["model"] == "llama70b"
    assert job.provider_request["llm_planning_enabled"] is True
    assert job.provider_request["creative_plan"]["voiceover"]["final_script"].startswith("开门前")
    assert job.metadata["llm_creative_plan"]["asset_strategy"]["no_raw_montage_rule"] == "不得直接拼接素材当成成片"
    assert job.scene_plan[0]["step"] == "llm_creative_direction"
    assert any(step["step"] == "llm_shot_s01" for step in job.scene_plan)

    planned = await service.prepare_shot_execution_plan(
        session,
        workspace_id="workspace-digital-human-llm-plan",
        job_id=job.id,
        template_id="wan-i2v-reference-avatar",
        resource_profile="production",
        width=1080,
        height=1920,
        fps=24,
        quality_profile="production",
    )
    shot_plan = planned.metadata["shot_execution_plan"]
    shot = shot_plan["shots"][0]

    assert planned.shot_execution_plan_status == "ready_for_operator_review"
    assert planned.shot_execution_plan_count == 1
    assert shot_plan["phase"] == "67F"
    assert shot["shot_id"] == "S01"
    assert shot["render_mode"] == "avatar_performance"
    assert shot["prompt_contract"]["inputs"]["positive_prompt"].startswith("realistic premium KTV")
    assert shot["reference_assets"][0]["role"] == "identity_reference"
    assert any(asset["asset_id"] == str(material.id) for asset in shot["reference_assets"])
    assert "no_raw_montage" in shot["quality_gates"]
    assert "identity_consistency" in shot["quality_gates"]
    assert planned.outputs[-1]["output_type"] == "digital_human_shot_execution_plan"


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
