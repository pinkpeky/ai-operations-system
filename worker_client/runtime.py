"""客户机本地 Worker Runtime Server。"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware

from app.browser.remote.services.browser_worker_auth_service import BrowserWorkerAuthService
from worker.browser_worker.config import WorkerSettings
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
from worker_client.config import WorkerClientConfig, WorkerClientState, load_worker_state
from worker_client.logging import get_recent_logs, log_event
from worker_client.openclaw import (
    OpenClawActionRequest,
    OpenClawActionResponse,
    OpenClawCapabilitiesResponse,
    OpenClawHealthResponse,
    OpenClawRuntime,
)

logger = logging.getLogger(__name__)


def build_worker_settings(config: WorkerClientConfig) -> WorkerSettings:
    """把 Worker Client 配置转换为现有 browser-worker runtime settings。"""

    return WorkerSettings(
        WORKER_HOST=config.runtime_host,
        WORKER_PORT=config.runtime_port,
        WORKER_TIMEOUT_SECONDS=config.timeout_seconds,
        WORKER_HEADLESS=True,
        WORKER_BROWSER_TYPE=str(config.capabilities.get("browser") or "chromium"),
        WORKER_SCREENSHOT_DIR=config.screenshot_dir,
        WORKER_PROFILE_DIR=config.profile_dir,
        BROWSER_WORKER_AUTH_ENABLED=config.auth_enabled,
        BROWSER_WORKER_AUTH_STRICT=config.auth_strict,
        BROWSER_WORKER_SECRET=config.worker_secret or "",
    )


def create_worker_client_app(
    config: WorkerClientConfig,
    *,
    runtime: PlaywrightBrowserWorkerRuntime | None = None,
    state: WorkerClientState | None = None,
    manager: Any | None = None,
) -> FastAPI:
    """创建客户机本地 Worker API，与现有 browser-worker 协议兼容。"""

    config.validate_config()
    worker_state = state or load_worker_state(config.state_path)
    worker_secret = (worker_state.worker_secret if worker_state is not None else None) or config.worker_secret or ""
    worker_settings = build_worker_settings(config)
    if worker_secret:
        worker_settings.browser_worker_secret = worker_secret
    runtime_instance = runtime or PlaywrightBrowserWorkerRuntime(settings=worker_settings)
    openclaw_runtime = OpenClawRuntime(
        provider_name=config.openclaw_provider,
        enabled=config.openclaw_enabled,
    )
    runtime_manager = manager
    if runtime_manager is None:
        from worker_client.runtime_manager import WorkerRuntimeManager

        runtime_manager = WorkerRuntimeManager(config)

    def safe_local_payload(payload: dict[str, Any]) -> dict[str, Any]:
        """本地管理 API 响应不允许包含 worker_secret。"""

        clean = dict(payload)
        clean.pop("worker_secret", None)
        clean.pop("secret", None)
        return clean

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        try:
            yield
        finally:
            await runtime_instance.close_all()

    app = FastAPI(title="AI Ops Customer Machine Worker", version="30.0.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    async def verify_worker_request(request: Request) -> None:
        """校验 AI Server -> 客户机 worker runtime 的签名。"""

        if not config.auth_enabled:
            return
        signature = request.headers.get("x-worker-signature")
        if not signature:
            if config.auth_strict:
                raise HTTPException(status_code=401, detail="worker signature required")
            return
        if not worker_secret:
            if config.auth_strict:
                raise HTTPException(status_code=401, detail="worker secret is not configured")
            return
        body = await request.body()
        valid = BrowserWorkerAuthService.verify_signature(
            secret=worker_secret,
            body=body.decode("utf-8") if body else None,
            timestamp=request.headers.get("x-worker-timestamp"),
            nonce=request.headers.get("x-worker-nonce"),
            body_hash=request.headers.get("x-worker-body-hash"),
            signature=signature,
        )
        if not valid:
            raise HTTPException(status_code=401, detail="invalid worker signature")

    @app.get("/health", response_model=WorkerHealthResponse)
    async def health() -> WorkerHealthResponse:
        """客户机 worker health。"""

        return WorkerHealthResponse(
            success=True,
            worker_type=config.worker_type,
            reachable=True,
            capabilities={
                **config.capabilities,
                "headless": True,
                "click": True,
                "type_text": True,
                "scroll": True,
                "openclaw": config.openclaw_enabled,
                "ui_access_placeholder": True,
            },
            message="customer machine worker reachable",
        )

    @app.get("/ui-access/capabilities", response_model=WorkerUIAccessCapabilitiesResponse)
    async def ui_access_capabilities() -> WorkerUIAccessCapabilitiesResponse:
        """声明当前仍是 UI access placeholder。"""

        return WorkerUIAccessCapabilitiesResponse(vnc=False, novnc=False, devtools=False, placeholder=True)

    @app.get("/openclaw/health", response_model=OpenClawHealthResponse)
    async def openclaw_health() -> OpenClawHealthResponse:
        """返回 OpenClaw mock runtime health。"""

        return await openclaw_runtime.health_check()

    @app.get("/openclaw/capabilities", response_model=OpenClawCapabilitiesResponse)
    async def openclaw_capabilities() -> OpenClawCapabilitiesResponse:
        """返回 OpenClaw mock runtime capabilities。"""

        return await openclaw_runtime.capabilities()

    @app.post("/openclaw/actions", response_model=OpenClawActionResponse)
    async def execute_openclaw_action(
        request: OpenClawActionRequest,
        _: None = Depends(verify_worker_request),
    ) -> OpenClawActionResponse:
        """执行 OpenClaw mock action。"""

        return await openclaw_runtime.execute_action(request)

    @app.get("/local/status")
    async def local_status() -> dict[str, Any]:
        """返回本地 Worker Console 状态，不包含 worker_secret。"""

        return safe_local_payload(runtime_manager.runtime_state())

    @app.get("/local/health")
    async def local_health() -> dict[str, Any]:
        """返回本地 Runtime Manager 健康信息。"""

        return safe_local_payload(runtime_manager.runtime_health())

    @app.post("/local/runtime/start")
    async def local_runtime_start() -> dict[str, Any]:
        """通过本地管理 API 启动 runtime。"""

        log_event("local api runtime start requested")
        return safe_local_payload(runtime_manager.start_runtime())

    @app.post("/local/runtime/stop")
    async def local_runtime_stop() -> dict[str, Any]:
        """通过本地管理 API 停止 runtime。"""

        log_event("local api runtime stop requested")
        return safe_local_payload(runtime_manager.stop_runtime())

    @app.post("/local/runtime/restart")
    async def local_runtime_restart() -> dict[str, Any]:
        """通过本地管理 API 重启 runtime。"""

        log_event("local api runtime restart requested")
        return safe_local_payload(runtime_manager.restart_runtime())

    @app.post("/local/heartbeat/start")
    async def local_heartbeat_start() -> dict[str, Any]:
        """通过本地管理 API 启动 heartbeat。"""

        log_event("local api heartbeat start requested")
        return safe_local_payload(runtime_manager.start_heartbeat())

    @app.post("/local/heartbeat/stop")
    async def local_heartbeat_stop() -> dict[str, Any]:
        """通过本地管理 API 停止 heartbeat。"""

        log_event("local api heartbeat stop requested")
        return safe_local_payload(runtime_manager.stop_heartbeat())

    @app.get("/local/logs")
    async def local_logs(lines: int = 100) -> dict[str, Any]:
        """返回本地最近日志，供未来 Worker Console GUI 使用。"""

        return {"lines": get_recent_logs(lines=lines)}

    @app.post("/sessions", response_model=WorkerSessionResponse, status_code=status.HTTP_201_CREATED)
    async def create_session(request: WorkerSessionRequest, _: None = Depends(verify_worker_request)) -> WorkerSessionResponse:
        """创建 Playwright session。"""

        return await runtime_instance.create_session(
            workspace_id=request.workspace_id,
            local_browser_session_id=request.local_browser_session_id,
            metadata=request.metadata,
            profile_id=request.profile_id,
            profile_path=request.profile_path,
            use_persistent_profile=request.use_persistent_profile,
        )

    @app.post("/actions", response_model=WorkerActionResponse)
    async def execute_action(request: WorkerActionRequest, _: None = Depends(verify_worker_request)) -> WorkerActionResponse:
        """执行 browser action。"""

        return await runtime_instance.execute_action(
            remote_session_id=request.remote_session_id,
            action_type=request.action_type,
            target=request.target,
            input_payload=request.input_payload,
        )

    @app.post("/sessions/{session_id}/close", response_model=WorkerSessionResponse)
    async def close_session(session_id: str, _: None = Depends(verify_worker_request)) -> WorkerSessionResponse:
        """关闭 browser session。"""

        return await runtime_instance.close_session(remote_session_id=session_id)

    @app.post("/human-control/start", response_model=WorkerHumanControlResponse)
    async def start_human_control(request: WorkerHumanControlRequest) -> WorkerHumanControlResponse:
        """进入 metadata-level human control。"""

        return await runtime_instance.start_human_control(
            remote_session_id=request.remote_session_id,
            control_session_id=request.control_session_id,
            payload=request.model_dump(mode="json"),
        )

    @app.post("/human-control/complete", response_model=WorkerHumanControlResponse)
    async def complete_human_control(request: WorkerHumanControlRequest) -> WorkerHumanControlResponse:
        """完成 metadata-level human control。"""

        return await runtime_instance.complete_human_control(
            remote_session_id=request.remote_session_id,
            control_session_id=request.control_session_id,
            note=request.note,
            payload=request.model_dump(mode="json"),
        )

    @app.get("/human-control/status/{session_id}", response_model=WorkerHumanControlResponse)
    async def get_human_control_status(session_id: str) -> WorkerHumanControlResponse:
        """查询 metadata-level human control 状态。"""

        return await runtime_instance.get_human_control_status(remote_session_id=session_id)

    return app
