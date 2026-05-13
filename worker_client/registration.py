"""Worker Client 注册 AI Server。"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import httpx

from worker_client.config import WorkerClientConfig, WorkerClientState, load_worker_state, save_worker_state

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class WorkerRegistrationResult:
    """注册结果。"""

    registered: bool
    worker_id: str
    state: WorkerClientState
    message: str


async def register_worker(
    config: WorkerClientConfig,
    *,
    force: bool = False,
    http_client: httpx.AsyncClient | None = None,
) -> WorkerRegistrationResult:
    """注册客户机 worker；已有 state 且未 force 时直接复用。"""

    existing = load_worker_state(config.state_path)
    if existing is not None and not force:
        logger.info("Worker already registered; reusing local state", extra={"worker_id": existing.worker_id})
        return WorkerRegistrationResult(registered=False, worker_id=existing.worker_id, state=existing, message="existing worker state reused")

    payload = {
        "worker_name": config.worker_name,
        "worker_type": config.worker_type,
        "base_url": config.effective_worker_base_url,
        "capabilities": config.capabilities,
        "metadata": {"source": "worker_client", "runtime_port": config.runtime_port},
        "max_sessions": config.max_sessions,
        "max_actions_per_minute": config.max_actions_per_minute,
        "priority": config.priority,
        "allowed_actions": config.allowed_actions,
        "allowed_domains": config.allowed_domains,
        "generate_secret": True,
    }
    url = f"{config.normalized_server_url}/api/v1/browser-workers/register"
    client = http_client or httpx.AsyncClient(timeout=config.timeout_seconds)
    close_client = http_client is None
    try:
        response = await client.post(url, headers=config.headers(), json=payload)
        response.raise_for_status()
        body = response.json()
        worker_id = str(body["id"])
        worker_secret = body.get("worker_secret")
        if not worker_secret:
            raise RuntimeError("AI Server did not return worker_secret")
        state = WorkerClientState(
            worker_id=worker_id,
            worker_secret=str(worker_secret),
            server_url=config.normalized_server_url,
            worker_name=config.worker_name,
            workspace_id=config.workspace_id,
            worker_base_url=config.effective_worker_base_url,
        )
        save_worker_state(config.state_path, state)
        logger.info("Worker registered", extra={"worker_id": worker_id, "workspace_id": config.workspace_id})
        return WorkerRegistrationResult(registered=True, worker_id=worker_id, state=state, message="worker registered")
    finally:
        if close_client:
            await client.aclose()

