"""Digital human production APIs."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.workspace_context import WorkspaceContext, get_workspace_context
from app.db.postgres import get_session
from app.digital_humans import DigitalHumanService
from app.schemas.digital_human import (
    DigitalHumanAssetListResponse,
    DigitalHumanAssetResponse,
    DigitalHumanCapabilitiesResponse,
    DigitalHumanComfyUIOutputIngestionRequest,
    DigitalHumanComfyUIWorkflowBindingRequest,
    DigitalHumanComfyUIWorkflowReadinessRequest,
    DigitalHumanShotExecutionPlanRequest,
    DigitalHumanWorkflowTemplateListResponse,
    DigitalHumanWorkflowTemplateResponse,
    DigitalHumanVideoJobActionRequest,
    DigitalHumanVideoJobCreateRequest,
    DigitalHumanVideoJobExecuteRequest,
    DigitalHumanVideoJobListResponse,
    DigitalHumanVideoJobRefreshRequest,
    DigitalHumanVideoJobResponse,
)


router = APIRouter(prefix="/digital-humans", tags=["digital-humans"])


def create_digital_human_service(settings: Settings = Depends(get_settings)) -> DigitalHumanService:
    return DigitalHumanService(settings=settings)


@router.get("/capabilities", response_model=DigitalHumanCapabilitiesResponse)
async def get_digital_human_capabilities(
    context: WorkspaceContext = Depends(get_workspace_context),
    service: DigitalHumanService = Depends(create_digital_human_service),
) -> DigitalHumanCapabilitiesResponse:
    """Return digital human provider readiness without calling external providers."""

    return service.capabilities(workspace_id=context.workspace_id)


@router.get("/workflow-templates", response_model=DigitalHumanWorkflowTemplateListResponse)
async def list_digital_human_workflow_templates(
    context: WorkspaceContext = Depends(get_workspace_context),
    service: DigitalHumanService = Depends(create_digital_human_service),
) -> DigitalHumanWorkflowTemplateListResponse:
    """List built-in digital human ComfyUI workflow template contracts."""

    return service.list_workflow_templates(workspace_id=context.workspace_id)


@router.get("/workflow-templates/{template_id}", response_model=DigitalHumanWorkflowTemplateResponse)
async def get_digital_human_workflow_template(
    template_id: str,
    service: DigitalHumanService = Depends(create_digital_human_service),
) -> DigitalHumanWorkflowTemplateResponse:
    """Return one built-in digital human ComfyUI workflow template contract."""

    return service.get_workflow_template(template_id=template_id)


@router.post("/assets", response_model=DigitalHumanAssetResponse)
async def upload_digital_human_asset(
    file: UploadFile = File(...),
    asset_type: str = Form(default="reference_image"),
    name: str | None = Form(default=None),
    consent_status: str = Form(default="unverified"),
    usage_scope: str | None = Form(default=None),
    operator_note: str | None = Form(default=None),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
    service: DigitalHumanService = Depends(create_digital_human_service),
) -> DigitalHumanAssetResponse:
    """Upload a portrait or material asset for digital human video production."""

    content = await file.read()
    return await service.create_asset(
        session,
        workspace_id=context.workspace_id,
        user_id=context.user_id,
        asset_type=asset_type,
        name=name,
        file_name=file.filename or "digital-human-asset",
        mime_type=file.content_type,
        content=content,
        consent_status=consent_status,
        usage_scope=usage_scope,
        operator_note=operator_note,
        metadata={"source_endpoint": "/api/v1/digital-humans/assets"},
    )


@router.get("/assets", response_model=DigitalHumanAssetListResponse)
async def list_digital_human_assets(
    asset_type: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
    service: DigitalHumanService = Depends(create_digital_human_service),
) -> DigitalHumanAssetListResponse:
    """List digital human assets for the current workspace."""

    return await service.list_assets(session, workspace_id=context.workspace_id, asset_type=asset_type, limit=limit)


@router.get("/assets/{asset_id}", response_model=DigitalHumanAssetResponse)
async def get_digital_human_asset(
    asset_id: UUID,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
    service: DigitalHumanService = Depends(create_digital_human_service),
) -> DigitalHumanAssetResponse:
    """Return one digital human asset."""

    return await service.get_asset(session, workspace_id=context.workspace_id, asset_id=asset_id)


@router.post("/video-jobs", response_model=DigitalHumanVideoJobResponse)
async def create_digital_human_video_job(
    request: DigitalHumanVideoJobCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
    service: DigitalHumanService = Depends(create_digital_human_service),
) -> DigitalHumanVideoJobResponse:
    """Create a recoverable digital human video job plan."""

    return await service.create_video_job(
        session,
        workspace_id=context.workspace_id,
        user_id=context.user_id,
        objective=request.objective,
        script=request.script,
        provider=request.provider,
        avatar_asset_id=request.avatar_asset_id,
        material_asset_ids=request.material_asset_ids,
        reference_asset_ids=request.reference_asset_ids,
        target_channels=request.target_channels,
        voice_profile=request.voice_profile,
        aspect_ratio=request.aspect_ratio,
        duration_seconds=request.duration_seconds,
        llm_planning_enabled=request.llm_planning_enabled,
        planning_context=request.planning_context,
        operator_note=request.operator_note,
        metadata=request.metadata,
    )


@router.get("/video-jobs", response_model=DigitalHumanVideoJobListResponse)
async def list_digital_human_video_jobs(
    status: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
    service: DigitalHumanService = Depends(create_digital_human_service),
) -> DigitalHumanVideoJobListResponse:
    """List digital human video jobs for the current workspace."""

    return await service.list_video_jobs(session, workspace_id=context.workspace_id, status=status, limit=limit)


@router.get("/video-jobs/{job_id}", response_model=DigitalHumanVideoJobResponse)
async def get_digital_human_video_job(
    job_id: UUID,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
    service: DigitalHumanService = Depends(create_digital_human_service),
) -> DigitalHumanVideoJobResponse:
    """Return one digital human video job."""

    return await service.get_video_job(session, workspace_id=context.workspace_id, job_id=job_id)


@router.post("/video-jobs/{job_id}/workflow-binding", response_model=DigitalHumanVideoJobResponse)
async def bind_digital_human_comfyui_workflow(
    job_id: UUID,
    request: DigitalHumanComfyUIWorkflowBindingRequest | None = None,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
    service: DigitalHumanService = Depends(create_digital_human_service),
) -> DigitalHumanVideoJobResponse:
    """Bind a digital human video job to a ComfyUI workflow template and local assets."""

    payload = request or DigitalHumanComfyUIWorkflowBindingRequest()
    return await service.bind_comfyui_workflow(
        session,
        workspace_id=context.workspace_id,
        job_id=job_id,
        template_id=payload.template_id,
        material_asset_ids=payload.material_asset_ids,
        reference_asset_ids=payload.reference_asset_ids,
        resource_profile=payload.resource_profile,
        width=payload.width,
        height=payload.height,
        frames=payload.frames,
        fps=payload.fps,
        estimated_vram_mb=payload.estimated_vram_mb,
        reserve_vram_mb=payload.reserve_vram_mb,
        operator_parameters=payload.operator_parameters,
        operator_note=payload.operator_note,
        metadata=payload.metadata,
    )


@router.post("/video-jobs/{job_id}/workflow-readiness-check", response_model=DigitalHumanVideoJobResponse)
async def check_digital_human_comfyui_workflow_readiness(
    job_id: UUID,
    request: DigitalHumanComfyUIWorkflowReadinessRequest | None = None,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
    service: DigitalHumanService = Depends(create_digital_human_service),
) -> DigitalHumanVideoJobResponse:
    """Record operator evidence for a bound real ComfyUI workflow before guarded execution."""

    payload = request or DigitalHumanComfyUIWorkflowReadinessRequest()
    return await service.check_comfyui_workflow_readiness(
        session,
        workspace_id=context.workspace_id,
        job_id=job_id,
        operator_imported_workflow=payload.operator_imported_workflow,
        installed_nodes=payload.installed_nodes,
        installed_models=payload.installed_models,
        uploaded_asset_ids=payload.uploaded_asset_ids,
        comfyui_base_url=payload.comfyui_base_url,
        output_watch_path=payload.output_watch_path,
        gpu_name=payload.gpu_name,
        free_vram_mb=payload.free_vram_mb,
        queue_depth=payload.queue_depth,
        operator_note=payload.operator_note,
        metadata=payload.metadata,
    )


@router.post("/video-jobs/{job_id}/shot-execution-plan", response_model=DigitalHumanVideoJobResponse)
async def prepare_digital_human_shot_execution_plan(
    job_id: UUID,
    request: DigitalHumanShotExecutionPlanRequest | None = None,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
    service: DigitalHumanService = Depends(create_digital_human_service),
) -> DigitalHumanVideoJobResponse:
    """Turn the LLM creative plan into per-shot render contracts for ComfyUI."""

    payload = request or DigitalHumanShotExecutionPlanRequest()
    return await service.prepare_shot_execution_plan(
        session,
        workspace_id=context.workspace_id,
        job_id=job_id,
        template_id=payload.template_id,
        resource_profile=payload.resource_profile,
        width=payload.width,
        height=payload.height,
        fps=payload.fps,
        quality_profile=payload.quality_profile,
        operator_note=payload.operator_note,
        metadata=payload.metadata,
    )


@router.post("/video-jobs/{job_id}/comfyui-output-ingestion", response_model=DigitalHumanVideoJobResponse)
async def ingest_digital_human_comfyui_output(
    job_id: UUID,
    request: DigitalHumanComfyUIOutputIngestionRequest | None = None,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
    service: DigitalHumanService = Depends(create_digital_human_service),
) -> DigitalHumanVideoJobResponse:
    """Refresh and ingest linked ComfyUI outputs as a digital human delivery asset."""

    payload = request or DigitalHumanComfyUIOutputIngestionRequest()
    return await service.ingest_comfyui_output(
        session,
        workspace_id=context.workspace_id,
        job_id=job_id,
        comfyui_video_job_id=payload.comfyui_video_job_id,
        refresh_comfyui_job=payload.refresh_comfyui_job,
        poll_history=payload.poll_history,
        resubmit_if_waiting=payload.resubmit_if_waiting,
        asset_name=payload.asset_name,
        operator_note=payload.operator_note,
        metadata=payload.metadata,
    )


@router.post("/video-jobs/{job_id}/refresh", response_model=DigitalHumanVideoJobResponse)
async def refresh_digital_human_video_job(
    job_id: UUID,
    request: DigitalHumanVideoJobRefreshRequest | None = None,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
    service: DigitalHumanService = Depends(create_digital_human_service),
) -> DigitalHumanVideoJobResponse:
    """Refresh one digital human job without performing external calls by default."""

    return await service.refresh_video_job(
        session,
        workspace_id=context.workspace_id,
        job_id=job_id,
        metadata=(request.metadata if request else {}),
    )


@router.post("/video-jobs/{job_id}/execute", response_model=DigitalHumanVideoJobResponse)
async def execute_digital_human_video_job(
    job_id: UUID,
    request: DigitalHumanVideoJobExecuteRequest | None = None,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
    service: DigitalHumanService = Depends(create_digital_human_service),
) -> DigitalHumanVideoJobResponse:
    """Execute an approved digital human job through a local artifact or ComfyUI handoff."""

    payload = request or DigitalHumanVideoJobExecuteRequest()
    return await service.execute_video_job(
        session,
        workspace_id=context.workspace_id,
        job_id=job_id,
        execution_mode=payload.execution_mode,
        submit_immediately=payload.submit_immediately,
        poll_history=payload.poll_history,
        prompt=payload.prompt,
        workflow=payload.workflow,
        resource_profile=payload.resource_profile,
        width=payload.width,
        height=payload.height,
        frames=payload.frames,
        fps=payload.fps,
        estimated_vram_mb=payload.estimated_vram_mb,
        reserve_vram_mb=payload.reserve_vram_mb,
        operator_note=payload.operator_note,
        metadata=payload.metadata,
    )


@router.post("/video-jobs/{job_id}/{action}", response_model=DigitalHumanVideoJobResponse)
async def review_digital_human_video_job(
    job_id: UUID,
    action: str,
    request: DigitalHumanVideoJobActionRequest | None = None,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
    service: DigitalHumanService = Depends(create_digital_human_service),
) -> DigitalHumanVideoJobResponse:
    """Approve, reject, or cancel a digital human video job."""

    return await service.update_video_job_review(
        session,
        workspace_id=context.workspace_id,
        job_id=job_id,
        action=action,
        reviewer_notes=request.reviewer_notes if request else None,
        metadata=request.metadata if request else {},
    )
