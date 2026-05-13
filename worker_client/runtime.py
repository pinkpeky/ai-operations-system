"""客户机本地 Worker Runtime Server。"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import Depends, FastAPI, HTTPException, Request, status

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
) -> FastAPI:
    """创建客户机本地 Worker API，与现有 browser-worker 协议兼容。"""

    worker_state = state or load_worker_state(config.state_path)
    worker_secret = (worker_state.worker_secret if worker_state is not None else None) or config.worker_secret or ""
    worker_settings = build_worker_settings(config)
    if worker_secret:
        worker_settings.browser_worker_secret = worker_secret
    runtime_instance = runtime or PlaywrightBrowserWorkerRuntime(settings=worker_settings)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        try:
            yield
        finally:
            await runtime_instance.close_all()

    app = FastAPI(title="AI Ops Customer Machine Worker", version="27.0.0", lifespan=lifespan)

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
                "ui_access_placeholder": True,
            },
            message="customer machine worker reachable",
        )

    @app.get("/ui-access/capabilities", response_model=WorkerUIAccessCapabilitiesResponse)
    async def ui_access_capabilities() -> WorkerUIAccessCapabilitiesResponse:
        """声明当前仍是 UI access placeholder。"""

        return WorkerUIAccessCapabilitiesResponse(vnc=False, novnc=False, devtools=False, placeholder=True)

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

