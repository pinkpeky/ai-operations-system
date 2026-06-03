"""Worker Client heartbeat loop。"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Any

import httpx

from app.browser.remote.services.browser_worker_auth_service import BrowserWorkerAuthService
from worker_client.config import WorkerClientConfig, WorkerClientState, load_worker_state
from worker_client.logging import log_event
from worker_client.status import update_status

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class WorkerHeartbeatResult:
    """单次 heartbeat 结果。"""

    success: bool
    status_code: int
    worker_id: str
    auth_status: str | None
    response: dict[str, Any]


def _heartbeat_headers(config: WorkerClientConfig, state: WorkerClientState, body: dict[str, Any]) -> dict[str, str]:
    """构造 heartbeat headers：workspace + secret hash 校验 + Phase 26 签名。"""

    headers = config.headers()
    headers["X-Worker-Secret"] = state.worker_secret
    headers["X-Worker-Id"] = state.worker_id
    headers.update(BrowserWorkerAuthService.sign_request(secret=state.worker_secret, body=body))
    return headers


async def send_heartbeat_once(
    config: WorkerClientConfig,
    *,
    status: str = "online",
    http_client: httpx.AsyncClient | None = None,
) -> WorkerHeartbeatResult:
    """发送一次 heartbeat。"""

    config.validate_config()
    state = load_worker_state(config.state_path)
    if state is None:
        raise FileNotFoundError("worker_state.json not found. Run `python -m worker_client.cli register` first.")
    body = {
        "status": status,
        "capabilities": config.capabilities,
        "metadata": {"source": "worker_client", "worker_base_url": state.worker_base_url},
    }
    url = f"{config.normalized_server_url}/api/v1/browser-workers/{state.worker_id}/heartbeat"
    client = http_client or httpx.AsyncClient(timeout=config.timeout_seconds)
    close_client = http_client is None
    try:
        response = await client.post(url, headers=_heartbeat_headers(config, state, body), json=body)
        payload = response.json()
        if response.status_code >= 400:
            logger.error("Worker heartbeat failed", extra={"worker_id": state.worker_id, "status_code": response.status_code})
            update_status({"current_status": "error", "last_error": f"heartbeat failed: {response.status_code}"})
            log_event("worker heartbeat failed", extra={"worker_id": state.worker_id, "status_code": response.status_code})
        else:
            logger.info("Worker heartbeat sent", extra={"worker_id": state.worker_id, "status": status})
            update_status(
                {
                    "worker_id": state.worker_id,
                    "worker_name": state.worker_name,
                    "workspace_id": state.workspace_id,
                    "server_url": state.server_url,
                    "registered": True,
                    "last_heartbeat_at": response.headers.get("date"),
                    "current_status": status,
                    "last_error": None,
                }
            )
            log_event("worker heartbeat sent", extra={"worker_id": state.worker_id, "status": status})
        return WorkerHeartbeatResult(
            success=response.status_code < 400,
            status_code=response.status_code,
            worker_id=state.worker_id,
            auth_status=payload.get("auth_status") if isinstance(payload, dict) else None,
            response=payload if isinstance(payload, dict) else {"raw": payload},
        )
    finally:
        if close_client:
            await client.aclose()


async def heartbeat_loop(config: WorkerClientConfig, *, status: str = "online", stop_event: asyncio.Event | None = None) -> None:
    """循环发送 heartbeat，支持 Ctrl+C / graceful shutdown。"""

    event = stop_event or asyncio.Event()
    update_status({"heartbeat_running": True, "current_status": status, "last_error": None})
    try:
        while not event.is_set():
            update_status({"heartbeat_running": True, "current_status": status, "last_error": None})
            try:
                await send_heartbeat_once(config, status=status)
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                logger.error("Worker heartbeat loop iteration failed", extra={"error": str(exc)})
            try:
                await asyncio.wait_for(event.wait(), timeout=config.heartbeat_interval_seconds)
            except asyncio.TimeoutError:
                continue
    finally:
        update_status({"heartbeat_running": False})
