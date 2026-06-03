"""Independent Browser Worker FastAPI service.

This worker is intentionally narrow: it runs a local headless Chromium session
for safe smoke-test pages such as example.com or local static test pages. It
does not implement login, social platform automation, proxy rotation, captcha
handling, or browser fingerprint workarounds.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
import logging
import os
from pathlib import Path
from typing import Any, AsyncIterator

from fastapi import Body, Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware

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
from worker_client.browser_runtime import (
    BrowserRuntime,
    BrowserRuntimeCreateSessionRequest,
    BrowserRuntimeNavigateRequest,
    BrowserRuntimePageResponse,
    BrowserRuntimeScreenshotRequest,
    BrowserRuntimeSessionResponse,
)
from worker_client.config import DEFAULT_CONFIG_PATH, WorkerClientConfig, load_worker_client_config, load_worker_state
from worker_client.logging import get_recent_logs, log_event
from worker_client.openclaw import (
    OpenClawActionRequest,
    OpenClawActionResponse,
    OpenClawCapabilitiesResponse,
    OpenClawHealthResponse,
    OpenClawProviderDiagnosticsResponse,
    OpenClawRuntime,
)
from worker_client.runtime_manager import WorkerRuntimeManager

logger = logging.getLogger(__name__)

_runtime: PlaywrightBrowserWorkerRuntime | None = None
_browser_runtime: BrowserRuntime | None = None
_local_runtime_manager: WorkerRuntimeManager | None = None
_openclaw_runtime: OpenClawRuntime | None = None


def get_runtime() -> PlaywrightBrowserWorkerRuntime:
    """Return the process-local browser runtime singleton."""

    global _runtime
    if _runtime is None:
        _runtime = PlaywrightBrowserWorkerRuntime(settings=get_worker_settings())
    return _runtime


def get_browser_runtime() -> BrowserRuntime:
    """Return the Phase 34 browser runtime singleton."""

    global _browser_runtime
    if _browser_runtime is None:
        _browser_runtime = BrowserRuntime.from_worker_settings(get_worker_settings())
    return _browser_runtime


def _build_compat_worker_client_config(settings: WorkerSettings) -> WorkerClientConfig:
    """Build a worker_client config for the standalone browser-worker entrypoint."""

    config_path = os.getenv("WORKER_CLIENT_CONFIG")
    if config_path or DEFAULT_CONFIG_PATH.exists():
        try:
            config = load_worker_client_config(config_path)
            config.runtime_host = settings.worker_host
            config.runtime_port = settings.worker_port
            config.timeout_seconds = settings.worker_timeout_seconds
            config.screenshot_dir = settings.worker_screenshot_dir
            config.profile_dir = settings.worker_profile_dir
            config.auth_enabled = settings.browser_worker_auth_enabled
            config.auth_strict = settings.browser_worker_auth_strict
            if settings.browser_worker_secret and not config.worker_secret:
                config.worker_secret = settings.browser_worker_secret
            return config
        except Exception as exc:
            logger.warning("Falling back to browser-worker local compatibility config: %s", exc)

    return WorkerClientConfig(
        server_url=os.getenv("WORKER_CLIENT_SERVER_URL")
        or os.getenv("AI_OPS_SERVER_URL")
        or os.getenv("SERVER_URL")
        or "http://localhost:8000",
        worker_name=os.getenv("WORKER_CLIENT_WORKER_NAME") or os.getenv("WORKER_NAME") or "browser-worker-compat",
        worker_type="playwright",
        workspace_id=os.getenv("WORKER_CLIENT_WORKSPACE_ID") or os.getenv("WORKSPACE_ID") or "demo-workspace",
        worker_secret=os.getenv("WORKER_CLIENT_WORKER_SECRET") or settings.browser_worker_secret or None,
        worker_base_url=os.getenv("WORKER_CLIENT_WORKER_BASE_URL") or f"http://localhost:{settings.worker_port}",
        runtime_host=settings.worker_host,
        runtime_port=settings.worker_port,
        state_path=Path(os.getenv("WORKER_CLIENT_STATE_PATH") or "worker_client/worker_state.json"),
        heartbeat_interval_seconds=int(os.getenv("WORKER_CLIENT_HEARTBEAT_INTERVAL_SECONDS") or 30),
        capabilities={
            "browser": settings.worker_browser_type,
            "browser_runtime": True,
            "screenshot": True,
            "page_content": True,
            "persistent_profile": True,
            "human_control": True,
            "ui_access_placeholder": True,
            "openclaw": True,
        },
        auth_enabled=settings.browser_worker_auth_enabled,
        auth_strict=settings.browser_worker_auth_strict,
        timeout_seconds=settings.worker_timeout_seconds,
        screenshot_dir=settings.worker_screenshot_dir,
        profile_dir=settings.worker_profile_dir,
        openclaw={
            "enabled": (os.getenv("WORKER_CLIENT_OPENCLAW_ENABLED") or os.getenv("OPENCLAW_ENABLED") or "true").strip().lower()
            in {"1", "true", "yes", "y", "on"},
            "provider": os.getenv("WORKER_CLIENT_OPENCLAW_PROVIDER") or os.getenv("OPENCLAW_PROVIDER") or "mock",
            "base_url": os.getenv("WORKER_CLIENT_OPENCLAW_BASE_URL") or os.getenv("OPENCLAW_BASE_URL") or "",
            "api_key": os.getenv("WORKER_CLIENT_OPENCLAW_API_KEY") or os.getenv("OPENCLAW_API_KEY") or "",
            "timeout_seconds": float(
                os.getenv("WORKER_CLIENT_OPENCLAW_TIMEOUT_SECONDS") or os.getenv("OPENCLAW_ACTION_TIMEOUT_SECONDS") or 60.0
            ),
            "health_path": os.getenv("WORKER_CLIENT_OPENCLAW_HEALTH_PATH") or os.getenv("OPENCLAW_HEALTH_PATH") or "/openclaw/health",
            "capabilities_path": os.getenv("WORKER_CLIENT_OPENCLAW_CAPABILITIES_PATH")
            or os.getenv("OPENCLAW_CAPABILITIES_PATH")
            or "/openclaw/capabilities",
            "action_path": os.getenv("WORKER_CLIENT_OPENCLAW_ACTION_PATH") or os.getenv("OPENCLAW_ACTION_PATH") or "/openclaw/actions",
        },
    )


def get_local_runtime_manager(settings: WorkerSettings | None = None) -> WorkerRuntimeManager:
    """Return the local management compatibility manager for worker.main."""

    global _local_runtime_manager
    if _local_runtime_manager is None:
        worker_settings = settings or get_worker_settings()
        _local_runtime_manager = WorkerRuntimeManager(_build_compat_worker_client_config(worker_settings))
    return _local_runtime_manager


def get_openclaw_runtime(settings: WorkerSettings | None = None) -> OpenClawRuntime:
    """Return the worker_client-compatible OpenClaw runtime for worker.main."""

    global _openclaw_runtime
    if _openclaw_runtime is None:
        worker_settings = settings or get_worker_settings()
        config = _build_compat_worker_client_config(worker_settings)
        _openclaw_runtime = OpenClawRuntime(
            provider_name=config.openclaw_provider,
            enabled=config.openclaw_enabled,
            provider_config=config.openclaw,
        )
    return _openclaw_runtime


def safe_local_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Remove local-only secrets from compatibility API responses."""

    clean = dict(payload)
    clean.pop("worker_secret", None)
    clean.pop("secret", None)
    clean["standalone_browser_worker_compatibility"] = True
    return clean


def _resolve_worker_request_secret(settings: WorkerSettings) -> str:
    """Resolve the plaintext secret used to verify signed API-to-worker requests."""

    try:
        config = _build_compat_worker_client_config(settings)
        state = load_worker_state(config.state_path)
        if state is not None and state.worker_secret:
            return state.worker_secret
        if config.worker_secret:
            return config.worker_secret
    except Exception as exc:
        logger.warning("Unable to load worker_client auth state; falling back to worker settings: %s", exc)
    return settings.browser_worker_secret


async def verify_worker_request(request: Request) -> None:
    """Verify signed worker requests when strict auth is enabled.

    Local development keeps BROWSER_WORKER_AUTH_STRICT=false, so missing secrets
    do not block smoke tests. In production, the worker first trusts the
    registered worker_client state secret, then the explicit worker config or
    BROWSER_WORKER_SECRET fallback.
    """

    settings = getattr(request.app.state, "worker_settings", None) or get_worker_settings()
    if not settings.browser_worker_auth_enabled:
        return
    headers = request.headers
    signature = headers.get("x-worker-signature")
    if not signature:
        if settings.browser_worker_auth_strict:
            raise HTTPException(status_code=401, detail="worker signature required")
        return
    worker_secret = _resolve_worker_request_secret(settings)
    if not worker_secret:
        if settings.browser_worker_auth_strict:
            raise HTTPException(status_code=401, detail="worker secret is not configured")
        return
    body = await request.body()
    valid = BrowserWorkerAuthService.verify_signature(
        secret=worker_secret,
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
        if _browser_runtime is not None:
            await _browser_runtime.close_all()


def create_app(settings: WorkerSettings | None = None) -> FastAPI:
    """Create the standalone Browser Worker application."""

    global _local_runtime_manager
    global _openclaw_runtime
    if settings is not None:
        get_worker_settings.cache_clear()
        _local_runtime_manager = None
        _openclaw_runtime = None

    app = FastAPI(
        title="AI Ops Browser Worker",
        version="20.0.0",
        lifespan=lifespan,
    )
    if settings is not None:
        app.state.worker_settings = settings
    worker_settings = settings or get_worker_settings()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:5174",
            "http://127.0.0.1:5174",
            "http://localhost:5180",
            "http://127.0.0.1:5180",
            "http://localhost:5181",
            "http://127.0.0.1:5181",
            "http://localhost:5182",
            "http://127.0.0.1:5182",
            "http://localhost:5184",
            "http://127.0.0.1:5184",
            "http://localhost:4174",
            "http://127.0.0.1:4174",
        ],
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    def local_manager() -> WorkerRuntimeManager:
        manager = getattr(app.state, "local_runtime_manager", None)
        if manager is not None:
            return manager
        return get_local_runtime_manager(worker_settings)

    def openclaw_runtime() -> OpenClawRuntime:
        runtime = getattr(app.state, "openclaw_runtime", None)
        if runtime is not None:
            return runtime
        return get_openclaw_runtime(worker_settings)

    @app.get("/health", response_model=WorkerHealthResponse)
    async def health() -> WorkerHealthResponse:
        """Report worker reachability and declared capabilities."""

        return WorkerHealthResponse(
            success=True,
            worker_type="playwright",
            reachable=True,
            capabilities={
                "browser": worker_settings.worker_browser_type,
                "headless": worker_settings.worker_headless,
                "screenshot": True,
                "browser_runtime": True,
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

    @app.get("/local/status")
    async def local_status() -> dict[str, Any]:
        """Expose worker_client-compatible local status from worker.main."""

        manager = local_manager()
        status_payload = manager.mark_runtime_running(True)
        return safe_local_payload(
            {
                **status_payload,
                "runtime_running": True,
                "current_status": "running",
                "runtime_control_mode": "standalone_browser_worker_process",
            }
        )

    @app.get("/local/health")
    async def local_health() -> dict[str, Any]:
        """Expose worker_client-compatible local health from worker.main."""

        manager = local_manager()
        health_payload = manager.runtime_health()
        health_payload["runtime_running"] = True
        health_payload["runtime_control_mode"] = "standalone_browser_worker_process"
        return safe_local_payload(health_payload)

    @app.post("/local/runtime/start")
    async def local_runtime_start() -> dict[str, Any]:
        """Mark the externally managed browser-worker process as running."""

        log_event("standalone browser worker local runtime start acknowledged")
        manager = local_manager()
        return safe_local_payload(
            {
                **manager.mark_runtime_running(True),
                "runtime_running": True,
                "runtime_control_mode": "standalone_browser_worker_process",
            }
        )

    @app.post("/local/runtime/stop")
    async def local_runtime_stop() -> dict[str, Any]:
        """Report that this standalone process must be stopped by its service manager."""

        log_event("standalone browser worker local runtime stop requested")
        manager = local_manager()
        return safe_local_payload(
            {
                **manager.mark_runtime_running(True, error="standalone worker process must be stopped by service manager"),
                "runtime_running": True,
                "current_status": "running",
                "runtime_control_mode": "external_process_control_required",
            }
        )

    @app.post("/local/runtime/restart")
    async def local_runtime_restart() -> dict[str, Any]:
        """Report that this standalone process must be restarted by its service manager."""

        log_event("standalone browser worker local runtime restart requested")
        manager = local_manager()
        return safe_local_payload(
            {
                **manager.mark_runtime_running(True, error="standalone worker process must be restarted by service manager"),
                "runtime_running": True,
                "current_status": "running",
                "runtime_control_mode": "external_process_control_required",
            }
        )

    @app.post("/local/heartbeat/start")
    async def local_heartbeat_start() -> dict[str, Any]:
        """Start the worker_client heartbeat loop from the compatibility API."""

        log_event("standalone browser worker local heartbeat start requested")
        return safe_local_payload(local_manager().start_heartbeat())

    @app.post("/local/heartbeat/stop")
    async def local_heartbeat_stop() -> dict[str, Any]:
        """Stop the worker_client heartbeat loop from the compatibility API."""

        log_event("standalone browser worker local heartbeat stop requested")
        return safe_local_payload(local_manager().stop_heartbeat())

    @app.get("/local/metric-dispatch-scheduler")
    async def local_metric_dispatch_scheduler_status() -> dict[str, Any]:
        """Return the local metric dispatch scheduler state."""

        return safe_local_payload(local_manager().metric_dispatch_scheduler_state())

    @app.post("/local/metric-dispatch-scheduler/configure")
    async def local_metric_dispatch_scheduler_configure(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
        """Persist a Phase 68T client_timer_payload for this local worker."""

        log_event("standalone browser worker metric dispatch scheduler configure requested")
        try:
            return safe_local_payload(local_manager().configure_metric_dispatch_scheduler(payload))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/local/metric-dispatch-scheduler/tick")
    async def local_metric_dispatch_scheduler_tick(payload: dict[str, Any] | None = Body(default=None)) -> dict[str, Any]:
        """Run one local metric dispatch scheduler tick."""

        force = bool((payload or {}).get("force")) if isinstance(payload, dict) else False
        log_event("standalone browser worker metric dispatch scheduler tick requested", extra={"force": force})
        return safe_local_payload(await local_manager().tick_metric_dispatch_scheduler(force=force))

    @app.post("/local/metric-dispatch-scheduler/start")
    async def local_metric_dispatch_scheduler_start() -> dict[str, Any]:
        """Start the local metric dispatch scheduler loop."""

        log_event("standalone browser worker metric dispatch scheduler start requested")
        return safe_local_payload(local_manager().start_metric_dispatch_scheduler())

    @app.post("/local/metric-dispatch-scheduler/stop")
    async def local_metric_dispatch_scheduler_stop() -> dict[str, Any]:
        """Stop the local metric dispatch scheduler loop."""

        log_event("standalone browser worker metric dispatch scheduler stop requested")
        return safe_local_payload(local_manager().stop_metric_dispatch_scheduler())

    @app.post("/local/metric-dispatch-scheduler/clear")
    async def local_metric_dispatch_scheduler_clear() -> dict[str, Any]:
        """Clear local metric dispatch scheduler state."""

        log_event("standalone browser worker metric dispatch scheduler clear requested")
        return safe_local_payload(local_manager().clear_metric_dispatch_scheduler())

    @app.get("/local/logs")
    async def local_logs(lines: int = 100) -> dict[str, Any]:
        """Return recent local worker logs for the customer console."""

        return {"lines": get_recent_logs(lines=lines), "standalone_browser_worker_compatibility": True}

    @app.get("/ui-access/capabilities", response_model=WorkerUIAccessCapabilitiesResponse)
    async def ui_access_capabilities() -> WorkerUIAccessCapabilitiesResponse:
        """Report placeholder UI access capabilities without starting any UI service."""

        return WorkerUIAccessCapabilitiesResponse(
            vnc=False,
            novnc=False,
            devtools=False,
            placeholder=True,
        )

    @app.get("/openclaw/health", response_model=OpenClawHealthResponse)
    async def openclaw_health() -> OpenClawHealthResponse:
        """Expose worker_client-compatible OpenClaw health from worker.main."""

        return await openclaw_runtime().health_check()

    @app.get("/openclaw/capabilities", response_model=OpenClawCapabilitiesResponse)
    async def openclaw_capabilities() -> OpenClawCapabilitiesResponse:
        """Expose worker_client-compatible OpenClaw capabilities from worker.main."""

        return await openclaw_runtime().capabilities()

    @app.get("/openclaw/provider-diagnostics", response_model=OpenClawProviderDiagnosticsResponse)
    async def openclaw_provider_diagnostics() -> OpenClawProviderDiagnosticsResponse:
        """Expose OpenClaw provider configuration preflight from worker.main."""

        return openclaw_runtime().provider_diagnostics()

    @app.post("/openclaw/actions", response_model=OpenClawActionResponse)
    async def execute_openclaw_action(
        request: OpenClawActionRequest,
    ) -> OpenClawActionResponse:
        """Execute a worker_client-compatible OpenClaw action from worker.main."""

        return await openclaw_runtime().execute_action(request)

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

    @app.post("/browser/session/create", response_model=BrowserRuntimeSessionResponse, status_code=status.HTTP_201_CREATED)
    async def create_browser_runtime_session(
        request: BrowserRuntimeCreateSessionRequest,
        _: None = Depends(verify_worker_request),
        runtime: BrowserRuntime = Depends(get_browser_runtime),
    ) -> BrowserRuntimeSessionResponse:
        """Create a Phase 34 Playwright browser runtime session."""

        return await runtime.create_session(request)

    @app.post("/browser/session/{session_id}/navigate")
    async def navigate_browser_runtime_session(
        session_id: str,
        request: BrowserRuntimeNavigateRequest,
        _: None = Depends(verify_worker_request),
        runtime: BrowserRuntime = Depends(get_browser_runtime),
    ) -> dict:
        """Navigate a Phase 34 browser runtime session."""

        return (await runtime.navigate(session_id=session_id, request=request)).model_dump()

    @app.post("/browser/session/{session_id}/screenshot")
    async def screenshot_browser_runtime_session(
        session_id: str,
        request: BrowserRuntimeScreenshotRequest,
        _: None = Depends(verify_worker_request),
        runtime: BrowserRuntime = Depends(get_browser_runtime),
    ) -> dict:
        """Capture a Phase 34 browser runtime screenshot."""

        return (await runtime.screenshot(session_id=session_id, request=request)).model_dump()

    @app.get("/browser/session/{session_id}/page", response_model=BrowserRuntimePageResponse)
    async def get_browser_runtime_page(
        session_id: str,
        _: None = Depends(verify_worker_request),
        runtime: BrowserRuntime = Depends(get_browser_runtime),
    ) -> BrowserRuntimePageResponse:
        """Return current Phase 34 browser runtime page content."""

        return await runtime.get_page(session_id=session_id)

    @app.post("/browser/session/{session_id}/close", response_model=BrowserRuntimeSessionResponse)
    async def close_browser_runtime_session(
        session_id: str,
        _: None = Depends(verify_worker_request),
        runtime: BrowserRuntime = Depends(get_browser_runtime),
    ) -> BrowserRuntimeSessionResponse:
        """Close a Phase 34 browser runtime session."""

        return await runtime.close_session(session_id=session_id)

    @app.post("/human-control/start", response_model=WorkerHumanControlResponse)
    async def start_human_control(
        request: WorkerHumanControlRequest,
        _: None = Depends(verify_worker_request),
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
        _: None = Depends(verify_worker_request),
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
        _: None = Depends(verify_worker_request),
        runtime: PlaywrightBrowserWorkerRuntime = Depends(get_runtime),
    ) -> WorkerHumanControlResponse:
        """Return metadata-level human control status for a worker session."""

        return await runtime.get_human_control_status(remote_session_id=session_id)

    return app


app = create_app()
