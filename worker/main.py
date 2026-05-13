"""Independent Browser Worker FastAPI service.

This worker is intentionally narrow: it runs a local headless Chromium session
for safe smoke-test pages such as example.com or local static test pages. It
does not implement login, social platform automation, proxy rotation, captcha
handling, or browser fingerprint workarounds.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
import logging
from typing import AsyncIterator

from fastapi import Depends, FastAPI, HTTPException, Request, status

from app.browser.remote.services.browser_worker_auth_service import BrowserWorkerAuthService
from worker.browser_worker.config import WorkerSettings, get_worker_settings
from worker.browser_worker.playwright_runtime import PlaywrightBrowserWorkerRuntime
from worker.browser_worker.schemas import (
    WorkerActionRequest,
    WorkerActionResponse,
    WorkerHealthResponse,
    WorkerHumanControlRequest,
    WorkerHumanControlResponse,
    WorkerSessionRequest,
    WorkerSessionResponse,
    WorkerUIAccessCapabilitiesResponse,
)

logger = logging.getLogger(__name__)

_runtime: PlaywrightBrowserWorkerRuntime | None = None


def get_runtime() -> PlaywrightBrowserWorkerRuntime:
    """Return the process-local browser runtime singleton."""

    global _runtime
    if _runtime is None:
        _runtime = PlaywrightBrowserWorkerRuntime(settings=get_worker_settings())
    return _runtime


async def verify_worker_request(request: Request) -> None:
    """Verify signed worker requests when strict auth is enabled.

    Local development keeps BROWSER_WORKER_AUTH_STRICT=false, so missing secrets
    do not block smoke tests. If BROWSER_WORKER_SECRET is configured, signatures
    are verified whenever signed headers are present.
    """

    settings = get_worker_settings()
    if not settings.browser_worker_auth_enabled:
        return
    headers = request.headers
    signature = headers.get("x-worker-signature")
    if not signature:
        if settings.browser_worker_auth_strict:
            raise HTTPException(status_code=401, detail="worker signature required")
        return
    if not settings.browser_worker_secret:
        if settings.browser_worker_auth_strict:
            raise HTTPException(status_code=401, detail="worker secret is not configured")
        return
    body = await request.body()
    valid = BrowserWorkerAuthService.verify_signature(
        secret=settings.browser_worker_secret,
        body=body.decode("utf-8") if body else None,
        timestamp=headers.get("x-worker-timestamp"),
        nonce=headers.get("x-worker-nonce"),
        body_hash=headers.get("x-worker-body-hash"),
        signature=signature,
    )
    if not valid:
        raise HTTPException(status_code=401, detail="invalid worker signature")


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Close all Playwright sessions when the worker shuts down."""

    try:
        yield
    finally:
        if _runtime is not None:
            await _runtime.close_all()


def create_app(settings: WorkerSettings | None = None) -> FastAPI:
    """Create the standalone Browser Worker application."""

    if settings is not None:
        get_worker_settings.cache_clear()

    app = FastAPI(
        title="AI Ops Browser Worker",
        version="20.0.0",
        lifespan=lifespan,
    )

    @app.get("/health", response_model=WorkerHealthResponse)
    async def health() -> WorkerHealthResponse:
        """Report worker reachability and declared capabilities."""

        worker_settings = settings or get_worker_settings()
        return WorkerHealthResponse(
            success=True,
            worker_type="playwright",
            reachable=True,
            capabilities={
                "browser": worker_settings.worker_browser_type,
                "headless": worker_settings.worker_headless,
                "screenshot": True,
                "page_content": True,
                "click": True,
                "type_text": True,
                "scroll": True,
                "persistent_profile": True,
                "human_control": True,
                "ui_access_placeholder": True,
            },
            message="browser worker reachable",
        )

    @app.get("/ui-access/capabilities", response_model=WorkerUIAccessCapabilitiesResponse)
    async def ui_access_capabilities() -> WorkerUIAccessCapabilitiesResponse:
        """Report placeholder UI access capabilities without starting any UI service."""

        return WorkerUIAccessCapabilitiesResponse(
            vnc=False,
            novnc=False,
            devtools=False,
            placeholder=True,
        )

    @app.post("/sessions", response_model=WorkerSessionResponse, status_code=status.HTTP_201_CREATED)
    async def create_session(
        request: WorkerSessionRequest,
        _: None = Depends(verify_worker_request),
        runtime: PlaywrightBrowserWorkerRuntime = Depends(get_runtime),
    ) -> WorkerSessionResponse:
        """Create a Playwright-backed browser session."""

        result = await runtime.create_session(
            workspace_id=request.workspace_id,
            local_browser_session_id=request.local_browser_session_id,
            metadata=request.metadata,
            profile_id=request.profile_id,
            profile_path=request.profile_path,
            use_persistent_profile=request.use_persistent_profile,
        )
        if not result.success:
            logger.error("Browser worker session creation failed", extra={"error": result.error})
        return result

    @app.post("/actions", response_model=WorkerActionResponse)
    async def execute_action(
        request: WorkerActionRequest,
        _: None = Depends(verify_worker_request),
        runtime: PlaywrightBrowserWorkerRuntime = Depends(get_runtime),
    ) -> WorkerActionResponse:
        """Execute one browser action inside an existing worker session."""

        result = await runtime.execute_action(
            remote_session_id=request.remote_session_id,
            action_type=request.action_type,
            target=request.target,
            input_payload=request.input_payload,
        )
        if not result.success:
            logger.error(
                "Browser worker action failed",
                extra={"action_type": request.action_type, "error": result.error},
            )
        return result

    @app.post("/sessions/{session_id}/close", response_model=WorkerSessionResponse)
    async def close_session(
        session_id: str,
        _: None = Depends(verify_worker_request),
        runtime: PlaywrightBrowserWorkerRuntime = Depends(get_runtime),
    ) -> WorkerSessionResponse:
        """Close a worker browser session."""

        return await runtime.close_session(remote_session_id=session_id)

    @app.post("/human-control/start", response_model=WorkerHumanControlResponse)
    async def start_human_control(
        request: WorkerHumanControlRequest,
        runtime: PlaywrightBrowserWorkerRuntime = Depends(get_runtime),
    ) -> WorkerHumanControlResponse:
        """Enter metadata-level human control mode for a worker session."""

        return await runtime.start_human_control(
            remote_session_id=request.remote_session_id,
            control_session_id=request.control_session_id,
            payload=request.model_dump(mode="json"),
        )

    @app.post("/human-control/complete", response_model=WorkerHumanControlResponse)
    async def complete_human_control(
        request: WorkerHumanControlRequest,
        runtime: PlaywrightBrowserWorkerRuntime = Depends(get_runtime),
    ) -> WorkerHumanControlResponse:
        """Complete metadata-level human control mode for a worker session."""

        return await runtime.complete_human_control(
            remote_session_id=request.remote_session_id,
            control_session_id=request.control_session_id,
            note=request.note,
            payload=request.model_dump(mode="json"),
        )

    @app.get("/human-control/status/{session_id}", response_model=WorkerHumanControlResponse)
    async def get_human_control_status(
        session_id: str,
        runtime: PlaywrightBrowserWorkerRuntime = Depends(get_runtime),
    ) -> WorkerHumanControlResponse:
        """Return metadata-level human control status for a worker session."""

        return await runtime.get_human_control_status(remote_session_id=session_id)

    return app


app = create_app()
