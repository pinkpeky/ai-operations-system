"""Remote Browser Worker API 与 mock worker runtime routes。"""

from __future__ import annotations

import logging
from dataclasses import asdict
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.remote.schemas import (
    BrowserWorkerActionResponse,
    BrowserSessionCleanupRequest,
    BrowserSessionCleanupResponse,
    BrowserWorkerHeartbeatRequest,
    BrowserWorkerHealthSummaryResponse,
    BrowserWorkerHumanControlRequest,
    BrowserWorkerHumanControlResponse,
    BrowserWorkerListResponse,
    BrowserWorkerMarkOfflineRequest,
    BrowserWorkerRegisterRequest,
    BrowserWorkerRevokeRequest,
    BrowserWorkerResponse,
    BrowserWorkerRotateSecretResponse,
    BrowserWorkerRuntimeActionRequest,
    BrowserWorkerRuntimeHealthResponse,
    BrowserWorkerRuntimeSessionRequest,
    BrowserWorkerRuntimeSessionResponse,
    BrowserWorkerSessionListResponse,
    BrowserWorkerSessionResponse,
    BrowserWorkerUIAccessCapabilitiesResponse,
)
from app.browser.remote.services import BrowserSessionCleanupService, BrowserWorkerHealthService, BrowserWorkerSelector, BrowserWorkerService
from app.core.errors import AppError
from app.core.workspace_context import WorkspaceContext, get_workspace_context
from app.db.postgres import get_session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/browser-workers", tags=["browser-workers"])
runtime_router = APIRouter(prefix="/browser-worker-runtime", tags=["browser-worker-runtime"])


@router.post("/register", response_model=BrowserWorkerResponse, status_code=201)
async def register_browser_worker(
    request: BrowserWorkerRegisterRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> BrowserWorkerResponse:
    """注册或更新当前 workspace 的 browser worker。"""

    try:
        service = BrowserWorkerService(session)
        worker = await service.register_worker(
            workspace_id=context.workspace_id,
            worker_name=request.worker_name,
            worker_type=request.worker_type,
            base_url=request.base_url,
            capabilities=request.capabilities,
            metadata=request.metadata,
            max_sessions=request.max_sessions,
            max_actions_per_minute=request.max_actions_per_minute,
            priority=request.priority,
            allowed_actions=request.allowed_actions,
            allowed_domains=request.allowed_domains,
            generate_secret=request.generate_secret,
        )
        return BrowserWorkerResponse.from_model(worker, worker_secret=service.last_worker_secret)
    except Exception as exc:
        logger.exception("Register browser worker API failed")
        raise AppError("Register browser worker failed", status_code=500) from exc


@router.get("/health/summary", response_model=BrowserWorkerHealthSummaryResponse)
async def get_browser_worker_health_summary(
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> BrowserWorkerHealthSummaryResponse:
    """Return workspace-scoped worker health/capacity summary."""

    service = BrowserWorkerHealthService(session)
    stale_workers = await service.mark_stale_workers_offline(workspace_id=context.workspace_id)
    summary = await service.health_summary(workspace_id=context.workspace_id)
    if stale_workers:
        logger.warning("Stale browser workers marked offline", extra={"count": len(stale_workers), "workspace_id": context.workspace_id})
    return BrowserWorkerHealthSummaryResponse(
        **{key: value for key, value in summary.items() if key != "workers"},
        workers=[BrowserWorkerResponse.from_model(worker) for worker in summary["workers"]],
    )


@router.get("/available", response_model=BrowserWorkerListResponse)
async def list_available_browser_workers(
    capability: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> BrowserWorkerListResponse:
    """List online workers that have remaining capacity."""

    selector = BrowserWorkerSelector(session)
    workers = await selector.list_available_workers(workspace_id=context.workspace_id, capability=capability, limit=limit)
    return BrowserWorkerListResponse(items=[BrowserWorkerResponse.from_model(worker) for worker in workers])


@router.post("/cleanup-sessions", response_model=BrowserSessionCleanupResponse)
async def cleanup_browser_worker_sessions(
    request: BrowserSessionCleanupRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> BrowserSessionCleanupResponse:
    """Manually cleanup stale or offline-worker browser sessions."""

    service = BrowserSessionCleanupService(session)
    result = await service.cleanup_stale_sessions(
        workspace_id=context.workspace_id,
        session_timeout_seconds=request.session_timeout_seconds,
        close_stale_sessions=request.close_stale_sessions,
    )
    return BrowserSessionCleanupResponse(**asdict(result))


@router.post("/{worker_id}/heartbeat", response_model=BrowserWorkerResponse)
async def heartbeat_browser_worker(
    worker_id: UUID,
    request: BrowserWorkerHeartbeatRequest,
    x_worker_secret: str | None = Header(default=None, alias="X-Worker-Secret"),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> BrowserWorkerResponse:
    """更新 browser worker heartbeat。"""

    try:
        service = BrowserWorkerService(session)
        worker = await service.heartbeat_worker(
            workspace_id=context.workspace_id,
            worker_id=worker_id,
            status=request.status,
            capabilities=request.capabilities,
            metadata=request.metadata,
            worker_secret=x_worker_secret,
        )
        return BrowserWorkerResponse.from_model(worker)
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception("Browser worker heartbeat API failed", extra={"worker_id": str(worker_id)})
        raise AppError("Browser worker heartbeat failed", status_code=500) from exc


@router.post("/{worker_id}/rotate-secret", response_model=BrowserWorkerRotateSecretResponse)
async def rotate_browser_worker_secret(
    worker_id: UUID,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> BrowserWorkerRotateSecretResponse:
    """Rotate worker secret and return plaintext once."""

    try:
        worker, secret = await BrowserWorkerService(session).rotate_worker_secret(
            workspace_id=context.workspace_id,
            worker_id=worker_id,
        )
        return BrowserWorkerRotateSecretResponse(**BrowserWorkerResponse.from_model(worker, worker_secret=secret).model_dump())
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc


@router.post("/{worker_id}/revoke", response_model=BrowserWorkerResponse)
async def revoke_browser_worker(
    worker_id: UUID,
    request: BrowserWorkerRevokeRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> BrowserWorkerResponse:
    """Revoke worker auth and mark it offline."""

    try:
        worker = await BrowserWorkerService(session).revoke_worker(
            workspace_id=context.workspace_id,
            worker_id=worker_id,
            reason=request.reason,
        )
        return BrowserWorkerResponse.from_model(worker)
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc


@router.post("/{worker_id}/mark-offline", response_model=BrowserWorkerResponse)
async def mark_browser_worker_offline(
    worker_id: UUID,
    request: BrowserWorkerMarkOfflineRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> BrowserWorkerResponse:
    """Manually mark a worker offline in the current workspace."""

    try:
        service = BrowserWorkerHealthService(session)
        worker = await service.mark_worker_offline(
            workspace_id=context.workspace_id,
            worker_id=worker_id,
            error_message=request.error_message,
        )
        return BrowserWorkerResponse.from_model(worker)
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception("Mark browser worker offline API failed", extra={"worker_id": str(worker_id)})
        raise AppError("Mark browser worker offline failed", status_code=500) from exc


@router.get("/{worker_id}/sessions", response_model=BrowserWorkerSessionListResponse)
async def list_browser_worker_sessions(
    worker_id: UUID,
    status: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> BrowserWorkerSessionListResponse:
    """List sessions attached to one worker."""

    service = BrowserWorkerService(session)
    worker = await service.repository.get_worker(workspace_id=context.workspace_id, worker_id=worker_id)
    if worker is None:
        raise AppError("Browser worker not found", status_code=404)
    sessions = await service.repository.list_worker_sessions(
        workspace_id=context.workspace_id,
        worker_id=worker_id,
        status=status,
        limit=limit,
    )
    return BrowserWorkerSessionListResponse(items=[BrowserWorkerSessionResponse.from_model(item) for item in sessions])


@router.get("", response_model=BrowserWorkerListResponse)
async def list_browser_workers(
    status: str | None = Query(default=None),
    worker_type: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> BrowserWorkerListResponse:
    """列出当前 workspace 的 browser workers。"""

    service = BrowserWorkerService(session)
    workers = await service.list_workers(
        workspace_id=context.workspace_id,
        status=status,
        worker_type=worker_type,
        limit=limit,
    )
    return BrowserWorkerListResponse(items=[BrowserWorkerResponse.from_model(worker) for worker in workers])


@runtime_router.get("/health", response_model=BrowserWorkerRuntimeHealthResponse)
async def browser_worker_runtime_health() -> BrowserWorkerRuntimeHealthResponse:
    """Mock worker runtime health check。"""

    return BrowserWorkerRuntimeHealthResponse(
        success=True,
        worker_type="mock",
        reachable=True,
        capabilities={
            "browser": "chromium",
            "screenshot": True,
            "page_content": True,
            "persistent_profile": True,
            "human_control": True,
            "ui_access_placeholder": True,
        },
        message="mock browser worker runtime reachable",
    )


@runtime_router.get("/ui-access/capabilities", response_model=BrowserWorkerUIAccessCapabilitiesResponse)
async def mock_worker_ui_access_capabilities() -> BrowserWorkerUIAccessCapabilitiesResponse:
    """Mock worker runtime UI access placeholder capabilities."""

    return BrowserWorkerUIAccessCapabilitiesResponse(vnc=False, novnc=False, devtools=False, placeholder=True)


@runtime_router.post("/sessions", response_model=BrowserWorkerRuntimeSessionResponse, status_code=201)
async def create_mock_worker_session(
    request: BrowserWorkerRuntimeSessionRequest,
) -> BrowserWorkerRuntimeSessionResponse:
    """Mock worker runtime 创建 remote session。"""

    remote_session_id = f"mock-remote-session-{uuid4()}"
    return BrowserWorkerRuntimeSessionResponse(
        success=True,
        remote_session_id=remote_session_id,
        message="mock remote browser session created",
        data={
            "remote_session_id": remote_session_id,
            "workspace_id": request.workspace_id,
            "local_browser_session_id": request.local_browser_session_id,
            "profile_id": request.profile_id,
            "profile_path": request.profile_path,
            "persistent_context_enabled": request.use_persistent_profile,
        },
    )


@runtime_router.post("/actions", response_model=BrowserWorkerActionResponse)
async def execute_mock_worker_action(
    request: BrowserWorkerRuntimeActionRequest,
) -> BrowserWorkerActionResponse:
    """Mock worker runtime 执行 remote action。"""

    remote_action_id = f"mock-remote-action-{uuid4()}"
    data = {
        "remote_session_id": request.remote_session_id,
        "remote_action_id": remote_action_id,
        "action_type": request.action_type,
        "target": request.target,
        "page_title": "Mock Remote Browser",
        "target_url": request.target if request.action_type == "navigate" else None,
        "selector": request.input_payload.get("selector"),
    }
    if request.action_type == "screenshot":
        data["screenshot_path"] = f"remote://{request.remote_session_id}/mock-screenshot.png"
    if request.action_type == "get_page_content":
        data["content"] = "<html><body><h1>Mock Remote Browser</h1></body></html>"
    return BrowserWorkerActionResponse(
        success=True,
        remote_action_id=remote_action_id,
        message="mock remote browser action success",
        data=data,
    )


@runtime_router.post("/sessions/{session_id}/close", response_model=BrowserWorkerRuntimeSessionResponse)
async def close_mock_worker_session(session_id: str) -> BrowserWorkerRuntimeSessionResponse:
    """Mock worker runtime 关闭 remote session。"""

    return BrowserWorkerRuntimeSessionResponse(
        success=True,
        remote_session_id=session_id,
        message="mock remote browser session closed",
        data={"remote_session_id": session_id},
    )


@runtime_router.post("/human-control/start", response_model=BrowserWorkerHumanControlResponse)
async def start_mock_worker_human_control(request: BrowserWorkerHumanControlRequest) -> BrowserWorkerHumanControlResponse:
    """Mock worker runtime 开始 metadata-level human control。"""

    return BrowserWorkerHumanControlResponse(
        success=True,
        remote_session_id=request.remote_session_id,
        status="active",
        message="mock human control started",
        data=request.model_dump(mode="json"),
    )


@runtime_router.post("/human-control/complete", response_model=BrowserWorkerHumanControlResponse)
async def complete_mock_worker_human_control(request: BrowserWorkerHumanControlRequest) -> BrowserWorkerHumanControlResponse:
    """Mock worker runtime 完成 metadata-level human control。"""

    return BrowserWorkerHumanControlResponse(
        success=True,
        remote_session_id=request.remote_session_id,
        status="completed",
        message="mock human control completed",
        data=request.model_dump(mode="json"),
    )


@runtime_router.get("/human-control/status/{session_id}", response_model=BrowserWorkerHumanControlResponse)
async def get_mock_worker_human_control_status(session_id: str) -> BrowserWorkerHumanControlResponse:
    """Mock worker runtime 查询 human control 状态。"""

    return BrowserWorkerHumanControlResponse(
        success=True,
        remote_session_id=session_id,
        status="inactive",
        message="mock human control status",
        data={"remote_session_id": session_id, "status": "inactive"},
    )
