"""Browser Adapter API 路由。"""

from __future__ import annotations

import logging
from dataclasses import asdict
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.services import (
    BrowserActionPolicyService,
    BrowserHumanControlService,
    BrowserProfileBackupService,
    BrowserProfileCleanupService,
    BrowserProfileHealthService,
    BrowserProfileService,
    BrowserSecurityAuditService,
    BrowserService,
    BrowserUIAccessService,
    ScreenshotCleanupService,
)
from app.core.config import get_settings
from app.core.errors import AppError
from app.core.workspace_context import WorkspaceContext, get_workspace_context
from app.db.postgres import get_session
from app.schemas.browser import (
    BrowserActionListResponse,
    BrowserActionLogListResponse,
    BrowserActionLogResponse,
    BrowserActionRequest,
    BrowserActionResponse,
    BrowserProfileBackupListResponse,
    BrowserProfileBackupResponse,
    BrowserProfileCleanupRequest,
    BrowserProfileCleanupResponse,
    BrowserProfileCreateRequest,
    BrowserHumanControlApproveRequest,
    BrowserHumanControlCancelRequest,
    BrowserHumanControlCompleteRequest,
    BrowserHumanControlEventListResponse,
    BrowserHumanControlEventResponse,
    BrowserHumanControlRequest,
    BrowserHumanControlSessionListResponse,
    BrowserHumanControlSessionResponse,
    BrowserHumanControlStartRequest,
    BrowserProfileHealthCheckResponse,
    BrowserProfileHealthSummaryResponse,
    BrowserProfileListResponse,
    BrowserProfileLockRequest,
    BrowserProfileRecoverLocksResponse,
    BrowserProfileReleaseRequest,
    BrowserProfileResponse,
    BrowserProfileRestoreRequest,
    BrowserProfileUsageLogListResponse,
    BrowserProfileUsageLogResponse,
    BrowserSessionCreateRequest,
    BrowserSessionListResponse,
    BrowserSessionResponse,
    BrowserUIAccessCreateRequest,
    BrowserUIAccessExpireResponse,
    BrowserUIAccessRevokeRequest,
    BrowserUIAccessResponse,
    BrowserUIAccessValidateResponse,
    BrowserSecurityAuditLogListResponse,
    BrowserSecurityAuditLogResponse,
    BrowserSecurityPolicyCheckRequest,
    BrowserSecurityPolicyCheckResponse,
    ScreenshotCleanupRequest,
    ScreenshotCleanupResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/browser", tags=["browser"])


@router.post("/human-control/request", response_model=BrowserHumanControlSessionResponse, status_code=201)
async def request_browser_human_control(
    request: BrowserHumanControlRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> BrowserHumanControlSessionResponse:
    """请求人工接管 browser session，并暂停自动化动作。"""

    try:
        service = BrowserHumanControlService(session, settings=get_settings())
        control_session = await service.request_control(
            workspace_id=context.workspace_id,
            browser_session_id=request.browser_session_id,
            reason=request.reason,
            requested_by=context.user_id,
            metadata=request.metadata,
        )
        return BrowserHumanControlSessionResponse.from_model(control_session)
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc


@router.get("/human-control", response_model=BrowserHumanControlSessionListResponse)
async def list_browser_human_control_sessions(
    status: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> BrowserHumanControlSessionListResponse:
    """列出当前 workspace 的人工接管 sessions。"""

    service = BrowserHumanControlService(session, settings=get_settings())
    control_sessions = await service.list_control_sessions(
        workspace_id=context.workspace_id,
        status=status,
        limit=limit,
    )
    return BrowserHumanControlSessionListResponse(
        items=[BrowserHumanControlSessionResponse.from_model(item) for item in control_sessions]
    )


@router.get("/human-control/{control_session_id}", response_model=BrowserHumanControlSessionResponse)
async def get_browser_human_control_session(
    control_session_id: UUID,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> BrowserHumanControlSessionResponse:
    """读取单个人工接管 session。"""

    service = BrowserHumanControlService(session, settings=get_settings())
    control_session = await service.get_control_session(
        workspace_id=context.workspace_id,
        control_session_id=control_session_id,
    )
    if control_session is None:
        raise AppError("Human control session not found", status_code=404)
    return BrowserHumanControlSessionResponse.from_model(control_session)


@router.post("/human-control/{control_session_id}/approve", response_model=BrowserHumanControlSessionResponse)
async def approve_browser_human_control(
    control_session_id: UUID,
    request: BrowserHumanControlApproveRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> BrowserHumanControlSessionResponse:
    """批准人工接管请求。"""

    try:
        control_session = await BrowserHumanControlService(session, settings=get_settings()).approve_control(
            workspace_id=context.workspace_id,
            control_session_id=control_session_id,
            approved_by=context.user_id,
            metadata=request.metadata,
        )
        return BrowserHumanControlSessionResponse.from_model(control_session)
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc


@router.post("/human-control/{control_session_id}/start", response_model=BrowserHumanControlSessionResponse)
async def start_browser_human_control(
    control_session_id: UUID,
    request: BrowserHumanControlStartRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> BrowserHumanControlSessionResponse:
    """启动人工接管窗口。"""

    try:
        control_session = await BrowserHumanControlService(session, settings=get_settings()).start_control(
            workspace_id=context.workspace_id,
            control_session_id=control_session_id,
            metadata=request.metadata,
        )
        return BrowserHumanControlSessionResponse.from_model(control_session)
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc


@router.post("/human-control/{control_session_id}/complete", response_model=BrowserHumanControlSessionResponse)
async def complete_browser_human_control(
    control_session_id: UUID,
    request: BrowserHumanControlCompleteRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> BrowserHumanControlSessionResponse:
    """完成人工接管，并恢复 browser session。"""

    try:
        control_session = await BrowserHumanControlService(session, settings=get_settings()).complete_control(
            workspace_id=context.workspace_id,
            control_session_id=control_session_id,
            note=request.note,
            metadata=request.metadata,
        )
        return BrowserHumanControlSessionResponse.from_model(control_session)
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc


@router.post("/human-control/{control_session_id}/cancel", response_model=BrowserHumanControlSessionResponse)
async def cancel_browser_human_control(
    control_session_id: UUID,
    request: BrowserHumanControlCancelRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> BrowserHumanControlSessionResponse:
    """取消人工接管，并恢复 browser session。"""

    try:
        control_session = await BrowserHumanControlService(session, settings=get_settings()).cancel_control(
            workspace_id=context.workspace_id,
            control_session_id=control_session_id,
            reason=request.reason,
        )
        return BrowserHumanControlSessionResponse.from_model(control_session)
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc


@router.get("/human-control/{control_session_id}/events", response_model=BrowserHumanControlEventListResponse)
async def list_browser_human_control_events(
    control_session_id: UUID,
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> BrowserHumanControlEventListResponse:
    """列出人工接管事件。"""

    try:
        events = await BrowserHumanControlService(session, settings=get_settings()).list_control_events(
            workspace_id=context.workspace_id,
            control_session_id=control_session_id,
            limit=limit,
        )
        return BrowserHumanControlEventListResponse(items=[BrowserHumanControlEventResponse.from_model(item) for item in events])
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc


@router.post("/ui-access", response_model=BrowserUIAccessResponse, status_code=201)
async def create_browser_ui_access(
    request: BrowserUIAccessCreateRequest,
    http_request: Request,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> BrowserUIAccessResponse:
    """创建 UI Access Placeholder，只在本次响应返回明文 token。"""

    try:
        result = await BrowserUIAccessService(session, settings=get_settings()).create_access_session(
            workspace_id=context.workspace_id,
            browser_session_id=request.browser_session_id,
            human_control_session_id=request.human_control_session_id,
            scopes=request.scopes,
            one_time=request.one_time,
            client_ip=http_request.client.host if http_request.client else None,
            user_agent=http_request.headers.get("user-agent"),
            metadata=request.metadata,
        )
        return BrowserUIAccessResponse.from_model(result.access_session, access_token=result.access_token)
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc


@router.post("/ui-access/expire", response_model=BrowserUIAccessExpireResponse)
async def expire_browser_ui_access_sessions(
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> BrowserUIAccessExpireResponse:
    """手动过期当前 workspace 中已超时的 UI access sessions。"""

    expired = await BrowserUIAccessService(session, settings=get_settings()).expire_access_sessions(
        workspace_id=context.workspace_id,
    )
    return BrowserUIAccessExpireResponse(
        expired_count=len(expired),
        items=[BrowserUIAccessResponse.from_model(item) for item in expired],
    )


@router.get("/ui-access/{access_session_id}", response_model=BrowserUIAccessResponse)
async def get_browser_ui_access(
    access_session_id: UUID,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> BrowserUIAccessResponse:
    """读取 UI Access Placeholder，不返回明文 token。"""

    access_session = await BrowserUIAccessService(session, settings=get_settings()).get_access_session(
        workspace_id=context.workspace_id,
        access_session_id=access_session_id,
    )
    if access_session is None:
        raise AppError("UI access session not found", status_code=404)
    return BrowserUIAccessResponse.from_model(access_session)


@router.post("/ui-access/{access_session_id}/revoke", response_model=BrowserUIAccessResponse)
async def revoke_browser_ui_access(
    access_session_id: UUID,
    request: BrowserUIAccessRevokeRequest | None = None,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> BrowserUIAccessResponse:
    """撤销 UI Access Placeholder。"""

    try:
        access_session = await BrowserUIAccessService(session, settings=get_settings()).revoke_access_session(
            workspace_id=context.workspace_id,
            access_session_id=access_session_id,
            reason=(request.reason if request is not None else None) or "manual revoke",
        )
        return BrowserUIAccessResponse.from_model(access_session)
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc


@router.get("/ui-access/{access_session_id}/validate", response_model=BrowserUIAccessValidateResponse)
async def validate_browser_ui_access(
    access_session_id: UUID,
    http_request: Request,
    token: str = Query(min_length=1),
    scope: str | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> BrowserUIAccessValidateResponse:
    """校验 UI Access token。"""

    result = await BrowserUIAccessService(session, settings=get_settings()).validate_access_token(
        workspace_id=context.workspace_id,
        access_session_id=access_session_id,
        token=token,
        scope=scope,
        client_ip=http_request.client.host if http_request.client else None,
        user_agent=http_request.headers.get("user-agent"),
    )
    return BrowserUIAccessValidateResponse(
        access_session_id=access_session_id,
        valid=result.valid,
        status=result.access_session.status if result.access_session is not None else None,
        reason=result.reason,
        scope=scope,
    )


@router.get("/security/audit-logs", response_model=BrowserSecurityAuditLogListResponse)
async def list_browser_security_audit_logs(
    event_type: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> BrowserSecurityAuditLogListResponse:
    """List workspace-scoped browser security audit logs."""

    logs = await BrowserSecurityAuditService(session).list_logs(
        workspace_id=context.workspace_id,
        event_type=event_type,
        limit=limit,
    )
    return BrowserSecurityAuditLogListResponse(items=[BrowserSecurityAuditLogResponse.from_model(item) for item in logs])


@router.post("/security/policy/check", response_model=BrowserSecurityPolicyCheckResponse)
async def check_browser_security_policy(
    request: BrowserSecurityPolicyCheckRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> BrowserSecurityPolicyCheckResponse:
    """Check browser action policy without executing the action."""

    service = BrowserService(session, settings=get_settings())
    browser_session = None
    if request.session_id is not None:
        browser_session = await service.repository.get_session(session_id=request.session_id, workspace_id=context.workspace_id)
        if browser_session is None:
            raise AppError("Browser session not found", status_code=404)
    result = await BrowserActionPolicyService(session, settings=get_settings()).check_action_policy(
        workspace_id=context.workspace_id,
        browser_session=browser_session,
        action_type=request.action_type,
        target=request.target,
        input_payload=request.metadata,
    )
    await session.commit()
    return BrowserSecurityPolicyCheckResponse(
        allowed=result.allowed,
        reason=result.reason,
        metadata=result.metadata or {},
    )


@router.post("/profiles", response_model=BrowserProfileResponse, status_code=201)
async def create_browser_profile(
    request: BrowserProfileCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> BrowserProfileResponse:
    """创建当前 workspace 的持久化 browser profile。"""

    try:
        service = BrowserProfileService(session, settings=get_settings())
        profile = await service.create_profile(
            workspace_id=context.workspace_id,
            user_id=context.user_id,
            profile_name=request.profile_name,
            profile_type=request.profile_type,
            provider=request.provider,
            metadata=request.metadata,
        )
        return BrowserProfileResponse.from_model(profile)
    except Exception as exc:
        logger.exception("Create browser profile API failed")
        raise AppError("Create browser profile failed", status_code=500) from exc


@router.get("/profiles", response_model=BrowserProfileListResponse)
async def list_browser_profiles(
    status: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> BrowserProfileListResponse:
    """列出当前 workspace 的 browser profiles。"""

    service = BrowserProfileService(session, settings=get_settings())
    profiles = await service.list_profiles(workspace_id=context.workspace_id, status=status, limit=limit)
    return BrowserProfileListResponse(items=[BrowserProfileResponse.from_model(profile) for profile in profiles])


@router.post("/profiles/recover-stale-locks", response_model=BrowserProfileRecoverLocksResponse)
async def recover_browser_profile_stale_locks(
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> BrowserProfileRecoverLocksResponse:
    """恢复当前 workspace 中超时或失效 session 持有的 profile lock。"""

    service = BrowserProfileHealthService(session, settings=get_settings())
    result = await service.recover_stale_locks(workspace_id=context.workspace_id)
    return BrowserProfileRecoverLocksResponse(
        workspace_id=result.workspace_id,
        recovered_count=result.recovered_count,
        checked_count=result.checked_count,
        recovered_profile_ids=result.recovered_profile_ids,
    )


@router.post("/profiles/cleanup", response_model=BrowserProfileCleanupResponse)
async def cleanup_browser_profiles(
    request: BrowserProfileCleanupRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> BrowserProfileCleanupResponse:
    """手动清理 deleted/corrupted/unused profile 目录，默认 dry-run。"""

    service = BrowserProfileCleanupService(session, settings=get_settings())
    result = await service.cleanup_profiles(
        workspace_id=context.workspace_id,
        include_deleted=request.include_deleted,
        include_corrupted=request.include_corrupted,
        include_unused=request.include_unused,
        dry_run=request.dry_run,
    )
    return BrowserProfileCleanupResponse(**asdict(result))


@router.get("/profiles/health/summary", response_model=BrowserProfileHealthSummaryResponse)
async def summarize_browser_profile_health(
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> BrowserProfileHealthSummaryResponse:
    """汇总当前 workspace 的 browser profile 健康状态。"""

    result = await BrowserProfileHealthService(session, settings=get_settings()).summarize_profiles(
        workspace_id=context.workspace_id,
    )
    return BrowserProfileHealthSummaryResponse(**asdict(result))


@router.get("/profiles/{profile_id}", response_model=BrowserProfileResponse)
async def get_browser_profile(
    profile_id: UUID,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> BrowserProfileResponse:
    """读取当前 workspace 的单个 browser profile。"""

    service = BrowserProfileService(session, settings=get_settings())
    profile = await service.get_profile(workspace_id=context.workspace_id, profile_id=profile_id)
    if profile is None:
        raise AppError("Browser profile not found", status_code=404)
    return BrowserProfileResponse.from_model(profile)


@router.post("/profiles/{profile_id}/health-check", response_model=BrowserProfileHealthCheckResponse)
async def check_browser_profile_health(
    profile_id: UUID,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> BrowserProfileHealthCheckResponse:
    """执行 profile health check。"""

    try:
        result = await BrowserProfileHealthService(session, settings=get_settings()).check_profile_health(
            workspace_id=context.workspace_id,
            profile_id=profile_id,
        )
        return BrowserProfileHealthCheckResponse(
            profile=BrowserProfileResponse.from_model(result.profile),
            healthy=result.healthy,
            health_status=result.health_status,
            error=result.error,
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc


@router.post("/profiles/{profile_id}/backup", response_model=BrowserProfileBackupResponse)
async def backup_browser_profile(
    profile_id: UUID,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> BrowserProfileBackupResponse:
    """创建 profile zip backup。"""

    try:
        result = await BrowserProfileBackupService(session, settings=get_settings()).create_backup(
            workspace_id=context.workspace_id,
            profile_id=profile_id,
        )
        return BrowserProfileBackupResponse(**asdict(result))
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc


@router.get("/profiles/{profile_id}/backups", response_model=BrowserProfileBackupListResponse)
async def list_browser_profile_backups(
    profile_id: UUID,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> BrowserProfileBackupListResponse:
    """列出 profile backups。"""

    try:
        backups = await BrowserProfileBackupService(session, settings=get_settings()).list_backups(
            workspace_id=context.workspace_id,
            profile_id=profile_id,
        )
        return BrowserProfileBackupListResponse(items=backups)
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc


@router.post("/profiles/{profile_id}/restore", response_model=BrowserProfileBackupResponse)
async def restore_browser_profile_backup(
    profile_id: UUID,
    request: BrowserProfileRestoreRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> BrowserProfileBackupResponse:
    """从指定 backup zip 恢复 profile。"""

    try:
        result = await BrowserProfileBackupService(session, settings=get_settings()).restore_backup(
            workspace_id=context.workspace_id,
            profile_id=profile_id,
            backup_path=request.backup_path,
        )
        return BrowserProfileBackupResponse(**asdict(result))
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc


@router.get("/profiles/{profile_id}/usage-logs", response_model=BrowserProfileUsageLogListResponse)
async def list_browser_profile_usage_logs(
    profile_id: UUID,
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> BrowserProfileUsageLogListResponse:
    """列出 profile usage logs。"""

    logs = await BrowserProfileHealthService(session, settings=get_settings()).list_usage_logs(
        workspace_id=context.workspace_id,
        profile_id=profile_id,
        limit=limit,
    )
    return BrowserProfileUsageLogListResponse(items=[BrowserProfileUsageLogResponse.from_model(log) for log in logs])


@router.post("/profiles/{profile_id}/lock", response_model=BrowserProfileResponse)
async def lock_browser_profile(
    profile_id: UUID,
    request: BrowserProfileLockRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> BrowserProfileResponse:
    """手动锁定 browser profile。"""

    try:
        service = BrowserProfileService(session, settings=get_settings())
        profile = await service.lock_profile(
            workspace_id=context.workspace_id,
            profile_id=profile_id,
            session_id=request.session_id,
        )
        return BrowserProfileResponse.from_model(profile)
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc


@router.post("/profiles/{profile_id}/release", response_model=BrowserProfileResponse)
async def release_browser_profile(
    profile_id: UUID,
    request: BrowserProfileReleaseRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> BrowserProfileResponse:
    """手动释放 browser profile lock。"""

    try:
        service = BrowserProfileService(session, settings=get_settings())
        profile = await service.release_profile(
            workspace_id=context.workspace_id,
            profile_id=profile_id,
            session_id=request.session_id,
        )
        return BrowserProfileResponse.from_model(profile)
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc


@router.delete("/profiles/{profile_id}", response_model=BrowserProfileResponse)
async def delete_browser_profile(
    profile_id: UUID,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> BrowserProfileResponse:
    """逻辑删除 browser profile。"""

    try:
        service = BrowserProfileService(session, settings=get_settings())
        profile = await service.delete_profile(workspace_id=context.workspace_id, profile_id=profile_id)
        return BrowserProfileResponse.from_model(profile)
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc


@router.post("/sessions", response_model=BrowserSessionResponse, status_code=201)
async def create_browser_session(
    request: BrowserSessionCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> BrowserSessionResponse:
    """在当前 workspace 创建 browser session。"""

    try:
        service = BrowserService(session, settings=get_settings())
        browser_session = await service.create_browser_session(
            workspace_id=context.workspace_id,
            user_id=context.user_id,
            metadata=request.metadata,
            profile_id=request.profile_id,
            use_persistent_profile=request.use_persistent_profile,
        )
        return BrowserSessionResponse.from_model(browser_session)
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc
    except Exception as exc:
        logger.exception("Create browser session API failed")
        raise AppError("Create browser session failed", status_code=500) from exc


@router.post("/sessions/{session_id}/close", response_model=BrowserSessionResponse)
async def close_browser_session(
    session_id: UUID,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> BrowserSessionResponse:
    """关闭 browser session，并释放关联 persistent profile。"""

    try:
        service = BrowserService(session, settings=get_settings())
        browser_session = await service.close_browser_session(workspace_id=context.workspace_id, session_id=session_id)
        return BrowserSessionResponse.from_model(browser_session)
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc


@router.get("/sessions", response_model=BrowserSessionListResponse)
async def list_browser_sessions(
    status: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> BrowserSessionListResponse:
    """列出当前 workspace 的 browser sessions。"""

    service = BrowserService(session, settings=get_settings())
    sessions = await service.list_sessions(workspace_id=context.workspace_id, status=status, limit=limit)
    return BrowserSessionListResponse(items=[BrowserSessionResponse.from_model(item) for item in sessions])


@router.post("/actions", response_model=BrowserActionResponse, status_code=201)
async def execute_browser_action(
    request: BrowserActionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> BrowserActionResponse:
    """通过当前 provider 执行 browser action。"""

    try:
        service = BrowserService(session, settings=get_settings())
        payload = dict(request.input_payload)
        if request.selector is not None:
            payload["selector"] = request.selector
        if request.text is not None:
            payload["text"] = request.text
        if request.screenshot_name is not None:
            payload["screenshot_name"] = request.screenshot_name
        action = await service.execute_action(
            workspace_id=context.workspace_id,
            session_id=request.session_id,
            action_type=request.action_type,
            target=request.target,
            input_payload=payload,
        )
        return BrowserActionResponse.from_model(action)
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc
    except Exception as exc:
        logger.exception("Execute browser action API failed")
        raise AppError("Execute browser action failed", status_code=500) from exc


@router.get("/actions/{session_id}", response_model=BrowserActionListResponse)
async def list_browser_actions(
    session_id: UUID,
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> BrowserActionListResponse:
    """列出指定 session 的 browser actions。"""

    try:
        service = BrowserService(session, settings=get_settings())
        actions = await service.list_actions(workspace_id=context.workspace_id, session_id=session_id, limit=limit)
        return BrowserActionListResponse(
            session_id=session_id,
            items=[BrowserActionResponse.from_model(action) for action in actions],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc


@router.get("/screenshot/{session_id}/{filename}")
async def get_browser_screenshot(
    session_id: UUID,
    filename: str,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> FileResponse:
    """读取当前 workspace/session 下的浏览器截图。"""

    try:
        service = BrowserService(session, settings=get_settings())
        browser_session = await service.repository.get_session(session_id=session_id, workspace_id=context.workspace_id)
        if browser_session is None:
            raise AppError("Browser session not found", status_code=404)
        safe_filename = Path(filename).name
        if safe_filename != filename or not safe_filename.endswith(".png"):
            raise AppError("Invalid screenshot filename", status_code=400)
        settings = get_settings()
        base_dir = (Path(settings.browser_screenshot_dir) / context.workspace_id / str(session_id)).resolve()
        screenshot_path = (base_dir / safe_filename).resolve()
        if not str(screenshot_path).startswith(str(base_dir)) or not screenshot_path.exists():
            raise AppError("Screenshot not found", status_code=404)
        return FileResponse(path=str(screenshot_path), media_type="image/png", filename=safe_filename)
    except AppError:
        raise
    except Exception as exc:
        logger.exception("Get browser screenshot API failed")
        raise AppError("Get browser screenshot failed", status_code=500) from exc


@router.post("/screenshots/cleanup", response_model=ScreenshotCleanupResponse)
async def cleanup_browser_screenshots(
    request: ScreenshotCleanupRequest,
    context: WorkspaceContext = Depends(get_workspace_context),
) -> ScreenshotCleanupResponse:
    """Manually cleanup screenshots by workspace and age. Defaults to dry-run."""

    cleanup_workspace_id = request.workspace_id or context.workspace_id
    if cleanup_workspace_id != context.workspace_id:
        raise AppError("Cannot cleanup screenshots from another workspace", status_code=403)
    service = ScreenshotCleanupService(settings=get_settings())
    result = service.cleanup(
        workspace_id=cleanup_workspace_id,
        older_than_days=request.older_than_days,
        dry_run=request.dry_run,
    )
    return ScreenshotCleanupResponse(**asdict(result))


@router.get("/logs/{session_id}", response_model=BrowserActionLogListResponse)
async def list_browser_logs(
    session_id: UUID,
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> BrowserActionLogListResponse:
    """列出指定 session 的 browser logs。"""

    try:
        service = BrowserService(session, settings=get_settings())
        logs = await service.list_logs(workspace_id=context.workspace_id, session_id=session_id, limit=limit)
        return BrowserActionLogListResponse(
            session_id=session_id,
            items=[BrowserActionLogResponse.from_model(log) for log in logs],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
