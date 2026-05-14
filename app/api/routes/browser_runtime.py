"""Remote Browser Runtime API routes."""

from __future__ import annotations

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.services.browser_runtime_observability_service import BrowserRuntimeObservabilityService
from app.browser.services.browser_runtime_session_service import BrowserRuntimeSessionService
from app.core.config import get_settings
from app.core.errors import AppError
from app.core.workspace_context import WorkspaceContext, get_workspace_context
from app.db.postgres import get_session
from app.schemas.browser_runtime import (
    BrowserRuntimeNavigateRequest,
    BrowserRuntimePageResponse,
    BrowserRuntimeScreenshotRequest,
    BrowserRuntimeSessionCreateRequest,
    BrowserRuntimeSessionListResponse,
    BrowserRuntimeSessionResponse,
)
from app.schemas.browser_runtime_observability import (
    BrowserRuntimeEventListResponse,
    BrowserRuntimeEventResponse,
    BrowserRuntimeReplayCreateRequest,
    BrowserRuntimeReplayExportResponse,
    BrowserRuntimeReplayResponse,
    BrowserRuntimeSnapshotListResponse,
    BrowserRuntimeSnapshotResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/browser-runtime", tags=["browser-runtime"])


@router.post("/sessions", response_model=BrowserRuntimeSessionResponse, status_code=201)
async def create_browser_runtime_session(
    request: BrowserRuntimeSessionCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> BrowserRuntimeSessionResponse:
    """Create a remote Playwright browser runtime session."""

    try:
        service = BrowserRuntimeSessionService(session, settings=get_settings())
        runtime_session = await service.create_session(
            workspace_id=context.workspace_id,
            browser=request.browser,
            metadata={**request.metadata, "user_id": context.user_id},
            worker_id=request.worker_id,
        )
        return BrowserRuntimeSessionResponse.from_model(runtime_session)
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc
    except Exception as exc:
        logger.exception("Create browser runtime session failed")
        raise AppError("Create browser runtime session failed", status_code=500) from exc


@router.get("/sessions", response_model=BrowserRuntimeSessionListResponse)
async def list_browser_runtime_sessions(
    status: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> BrowserRuntimeSessionListResponse:
    """List remote browser runtime sessions in the current workspace."""

    service = BrowserRuntimeSessionService(session, settings=get_settings())
    sessions = await service.list_sessions(workspace_id=context.workspace_id, status=status, limit=limit)
    return BrowserRuntimeSessionListResponse(items=[BrowserRuntimeSessionResponse.from_model(item) for item in sessions])


@router.get("/sessions/{session_id}", response_model=BrowserRuntimeSessionResponse)
async def get_browser_runtime_session(
    session_id: UUID,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> BrowserRuntimeSessionResponse:
    """Get one remote browser runtime session."""

    runtime_session = await BrowserRuntimeSessionService(session, settings=get_settings()).get_session(
        workspace_id=context.workspace_id,
        session_id=session_id,
    )
    if runtime_session is None:
        raise AppError("Browser runtime session not found", status_code=404)
    return BrowserRuntimeSessionResponse.from_model(runtime_session)


@router.post("/sessions/{session_id}/navigate", response_model=BrowserRuntimeSessionResponse)
async def navigate_browser_runtime_session(
    session_id: UUID,
    request: BrowserRuntimeNavigateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> BrowserRuntimeSessionResponse:
    """Navigate one remote browser runtime session."""

    try:
        runtime_session = await BrowserRuntimeSessionService(session, settings=get_settings()).navigate(
            workspace_id=context.workspace_id,
            session_id=session_id,
            url=request.url,
        )
        return BrowserRuntimeSessionResponse.from_model(runtime_session)
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc


@router.post("/sessions/{session_id}/screenshot", response_model=BrowserRuntimeSessionResponse)
async def screenshot_browser_runtime_session(
    session_id: UUID,
    request: BrowserRuntimeScreenshotRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> BrowserRuntimeSessionResponse:
    """Capture a remote browser runtime screenshot."""

    try:
        runtime_session = await BrowserRuntimeSessionService(session, settings=get_settings()).screenshot(
            workspace_id=context.workspace_id,
            session_id=session_id,
            full_page=request.full_page,
            screenshot_name=request.screenshot_name,
        )
        return BrowserRuntimeSessionResponse.from_model(runtime_session)
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc


@router.get("/sessions/{session_id}/page", response_model=BrowserRuntimePageResponse)
async def get_browser_runtime_page(
    session_id: UUID,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> BrowserRuntimePageResponse:
    """Fetch current remote browser page title and content."""

    try:
        service = BrowserRuntimeSessionService(session, settings=get_settings())
        page = await service.get_page(workspace_id=context.workspace_id, session_id=session_id)
        runtime_session = await service.get_session(workspace_id=context.workspace_id, session_id=session_id)
        if runtime_session is None:
            raise AppError("Browser runtime session not found", status_code=404)
        return BrowserRuntimePageResponse(
            session=BrowserRuntimeSessionResponse.from_model(runtime_session),
            title=page.get("page_title") or page.get("title"),
            url=page.get("current_url") or page.get("url"),
            content=page.get("content"),
            metadata={key: value for key, value in page.items() if key != "content"},
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc


@router.post("/sessions/{session_id}/close", response_model=BrowserRuntimeSessionResponse)
async def close_browser_runtime_session(
    session_id: UUID,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> BrowserRuntimeSessionResponse:
    """Close one remote browser runtime session."""

    try:
        runtime_session = await BrowserRuntimeSessionService(session, settings=get_settings()).close_session(
            workspace_id=context.workspace_id,
            session_id=session_id,
        )
        return BrowserRuntimeSessionResponse.from_model(runtime_session)
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc


@router.get("/sessions/{session_id}/events", response_model=BrowserRuntimeEventListResponse)
async def list_browser_runtime_events(
    session_id: UUID,
    limit: int = Query(default=100, ge=1, le=1000),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> BrowserRuntimeEventListResponse:
    """List timeline events for one browser runtime session."""

    service = BrowserRuntimeObservabilityService(session, settings=get_settings())
    events = await service.list_events(
        workspace_id=context.workspace_id,
        runtime_session_id=session_id,
        limit=limit,
    )
    return BrowserRuntimeEventListResponse(items=[BrowserRuntimeEventResponse.from_model(event) for event in events])


@router.get("/sessions/{session_id}/snapshots", response_model=BrowserRuntimeSnapshotListResponse)
async def list_browser_runtime_snapshots(
    session_id: UUID,
    snapshot_type: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=1000),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> BrowserRuntimeSnapshotListResponse:
    """List stored snapshots for one browser runtime session."""

    service = BrowserRuntimeObservabilityService(session, settings=get_settings())
    snapshots = await service.list_snapshots(
        workspace_id=context.workspace_id,
        runtime_session_id=session_id,
        snapshot_type=snapshot_type,
        limit=limit,
    )
    return BrowserRuntimeSnapshotListResponse(
        items=[BrowserRuntimeSnapshotResponse.from_model(snapshot) for snapshot in snapshots]
    )


@router.post("/sessions/{session_id}/replay", response_model=BrowserRuntimeReplayResponse, status_code=201)
async def create_browser_runtime_replay(
    session_id: UUID,
    request: BrowserRuntimeReplayCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> BrowserRuntimeReplayResponse:
    """Create metadata-only replay for one browser runtime session."""

    try:
        replay = await BrowserRuntimeObservabilityService(session, settings=get_settings()).create_replay(
            workspace_id=context.workspace_id,
            runtime_session_id=session_id,
            metadata=request.metadata,
        )
        return BrowserRuntimeReplayResponse.from_model(replay)
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc


@router.get("/replays/{replay_id}", response_model=BrowserRuntimeReplayResponse)
async def get_browser_runtime_replay(
    replay_id: UUID,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> BrowserRuntimeReplayResponse:
    """Get one browser runtime replay metadata record."""

    replay = await BrowserRuntimeObservabilityService(session, settings=get_settings()).get_replay(
        workspace_id=context.workspace_id,
        replay_id=replay_id,
    )
    if replay is None:
        raise AppError("Browser runtime replay not found", status_code=404)
    return BrowserRuntimeReplayResponse.from_model(replay)


@router.get("/replays/{replay_id}/export", response_model=BrowserRuntimeReplayExportResponse)
async def export_browser_runtime_replay(
    replay_id: UUID,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> BrowserRuntimeReplayExportResponse:
    """Export metadata-only replay JSON."""

    try:
        replay, export_path, payload = await BrowserRuntimeObservabilityService(session, settings=get_settings()).export_replay_json(
            workspace_id=context.workspace_id,
            replay_id=replay_id,
        )
        return BrowserRuntimeReplayExportResponse(
            replay=BrowserRuntimeReplayResponse.from_model(replay),
            export_path=str(export_path),
            export=payload,
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
