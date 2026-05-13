"""Remote Browser Worker repository.

All queries are scoped by workspace_id to preserve workspace isolation. The
repository only persists worker/session/action state; provider execution stays
in BrowserService / RemoteBrowserProvider.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.browser_worker import BrowserWorker, BrowserWorkerAction, BrowserWorkerSession
from app.models.enums import BrowserWorkerActionStatus, BrowserWorkerAuthStatus, BrowserWorkerSessionStatus, BrowserWorkerStatus


class BrowserWorkerRepository:
    """Workspace-scoped browser worker persistence layer."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def register_worker(
        self,
        *,
        workspace_id: str,
        worker_name: str,
        worker_type: str,
        base_url: str,
        capabilities: dict[str, Any],
        metadata: dict[str, Any],
        max_sessions: int = 5,
        max_actions_per_minute: int = 60,
        priority: int = 100,
        worker_secret_hash: str | None = None,
        api_key_hash: str | None = None,
        allowed_actions: list[str] | None = None,
        allowed_domains: list[str] | None = None,
    ) -> BrowserWorker:
        """Register or update one worker in a workspace."""

        statement = select(BrowserWorker).where(
            BrowserWorker.workspace_id == workspace_id,
            BrowserWorker.worker_name == worker_name,
        )
        result = await self.session.execute(statement)
        worker = result.scalar_one_or_none()
        if worker is None:
            worker = BrowserWorker(
                workspace_id=workspace_id,
                worker_name=worker_name,
                worker_type=worker_type,
                base_url=base_url.rstrip("/"),
                status=BrowserWorkerStatus.ONLINE.value,
                capabilities=capabilities,
                max_sessions=max_sessions,
                active_sessions=0,
                max_actions_per_minute=max_actions_per_minute,
                current_load=0,
                priority=priority,
                error_message=None,
                worker_secret_hash=worker_secret_hash,
                api_key_hash=api_key_hash,
                auth_status=BrowserWorkerAuthStatus.UNVERIFIED.value if worker_secret_hash else BrowserWorkerAuthStatus.VERIFIED.value,
                allowed_actions=allowed_actions or [],
                allowed_domains=allowed_domains or [],
                worker_metadata=metadata,
                last_heartbeat_at=datetime.now(UTC),
            )
            self.session.add(worker)
        else:
            worker.worker_type = worker_type
            worker.base_url = base_url.rstrip("/")
            worker.status = BrowserWorkerStatus.ONLINE.value
            worker.capabilities = capabilities
            worker.max_sessions = max_sessions
            worker.max_actions_per_minute = max_actions_per_minute
            worker.priority = priority
            worker.error_message = None
            if worker_secret_hash is not None:
                worker.worker_secret_hash = worker_secret_hash
                worker.auth_status = BrowserWorkerAuthStatus.UNVERIFIED.value
            if api_key_hash is not None:
                worker.api_key_hash = api_key_hash
            worker.allowed_actions = allowed_actions or worker.allowed_actions or []
            worker.allowed_domains = allowed_domains or worker.allowed_domains or []
            worker.worker_metadata = {**(worker.worker_metadata or {}), **metadata}
            worker.last_heartbeat_at = datetime.now(UTC)
        await self.session.flush()
        return worker

    async def rotate_worker_secret(self, *, worker: BrowserWorker, worker_secret_hash: str) -> BrowserWorker:
        """Rotate worker secret hash and reset auth status."""

        worker.worker_secret_hash = worker_secret_hash
        worker.auth_status = BrowserWorkerAuthStatus.UNVERIFIED.value
        worker.last_auth_at = None
        await self.session.flush()
        return worker

    async def mark_worker_auth_success(self, *, worker: BrowserWorker) -> BrowserWorker:
        """Mark worker authentication as verified."""

        worker.auth_status = BrowserWorkerAuthStatus.VERIFIED.value
        worker.last_auth_at = datetime.now(UTC)
        await self.session.flush()
        return worker

    async def mark_worker_auth_failed(self, *, worker: BrowserWorker, error_message: str | None = None) -> BrowserWorker:
        """Mark worker authentication failed."""

        worker.auth_status = BrowserWorkerAuthStatus.FAILED.value
        worker.error_message = error_message
        await self.session.flush()
        return worker

    async def revoke_worker_auth(self, *, worker: BrowserWorker, error_message: str | None = None) -> BrowserWorker:
        """Revoke worker auth and mark worker offline."""

        worker.auth_status = BrowserWorkerAuthStatus.REVOKED.value
        worker.status = BrowserWorkerStatus.OFFLINE.value
        worker.error_message = error_message
        worker.current_load = max(0, worker.active_sessions)
        await self.session.flush()
        return worker

    async def get_worker(self, *, workspace_id: str, worker_id: UUID) -> BrowserWorker | None:
        """Load one worker by workspace and ID."""

        statement = select(BrowserWorker).where(BrowserWorker.workspace_id == workspace_id, BrowserWorker.id == worker_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def list_workers(
        self,
        *,
        workspace_id: str,
        status: str | None = None,
        worker_type: str | None = None,
        limit: int = 100,
    ) -> list[BrowserWorker]:
        """List workers in one workspace."""

        statement = select(BrowserWorker).where(BrowserWorker.workspace_id == workspace_id)
        if status is not None:
            statement = statement.where(BrowserWorker.status == status)
        if worker_type is not None:
            statement = statement.where(BrowserWorker.worker_type == worker_type)
        statement = statement.order_by(BrowserWorker.updated_at.desc()).limit(limit)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def heartbeat_worker(
        self,
        *,
        worker: BrowserWorker,
        status: str,
        capabilities: dict[str, Any],
        metadata: dict[str, Any],
    ) -> BrowserWorker:
        """Update heartbeat, status, capabilities, and error message."""

        worker.status = status
        worker.capabilities = capabilities or worker.capabilities
        worker.error_message = str(metadata.get("error_message")) if metadata.get("error_message") else None
        if metadata:
            worker.worker_metadata = {**(worker.worker_metadata or {}), **metadata}
        worker.last_heartbeat_at = datetime.now(UTC)
        await self.session.flush()
        return worker

    async def get_available_worker(self, *, workspace_id: str) -> BrowserWorker | None:
        """Select the least-loaded available worker."""

        workers = await self.list_available_workers(workspace_id=workspace_id, limit=1)
        return workers[0] if workers else None

    async def list_available_workers(
        self,
        *,
        workspace_id: str,
        capability: str | None = None,
        limit: int = 100,
    ) -> list[BrowserWorker]:
        """List online workers that still have session capacity."""

        statement = (
            select(BrowserWorker)
            .where(
                BrowserWorker.workspace_id == workspace_id,
                BrowserWorker.status == BrowserWorkerStatus.ONLINE.value,
                BrowserWorker.active_sessions < BrowserWorker.max_sessions,
            )
            .order_by(
                BrowserWorker.current_load.asc(),
                BrowserWorker.active_sessions.asc(),
                BrowserWorker.priority.desc(),
                BrowserWorker.updated_at.desc(),
            )
            .limit(limit)
        )
        result = await self.session.execute(statement)
        workers = list(result.scalars().all())
        if capability is None:
            return workers
        return [worker for worker in workers if bool((worker.capabilities or {}).get(capability))]

    async def mark_worker_offline(self, *, worker: BrowserWorker, error_message: str | None = None) -> BrowserWorker:
        """Mark a worker offline and persist the last error."""

        worker.status = BrowserWorkerStatus.OFFLINE.value
        worker.error_message = error_message
        worker.current_load = max(0, worker.active_sessions)
        await self.session.flush()
        return worker

    async def mark_stale_workers_offline(self, *, workspace_id: str, timeout_seconds: int) -> list[BrowserWorker]:
        """Mark workers with stale heartbeat as offline."""

        threshold = datetime.now(UTC) - timedelta(seconds=timeout_seconds)
        statement = select(BrowserWorker).where(
            BrowserWorker.workspace_id == workspace_id,
            BrowserWorker.status.in_(
                [
                    BrowserWorkerStatus.ONLINE.value,
                    BrowserWorkerStatus.BUSY.value,
                    BrowserWorkerStatus.ERROR.value,
                ]
            ),
            BrowserWorker.last_heartbeat_at.is_not(None),
            BrowserWorker.last_heartbeat_at < threshold,
        )
        result = await self.session.execute(statement)
        workers = list(result.scalars().all())
        for worker in workers:
            await self.mark_worker_offline(worker=worker, error_message=f"heartbeat stale for {timeout_seconds}s")
        return workers

    async def summarize_workers(self, *, workspace_id: str, timeout_seconds: int) -> dict[str, Any]:
        """Return a workspace-scoped worker health/capacity summary."""

        workers = await self.list_workers(workspace_id=workspace_id, limit=1000)
        now = datetime.now(UTC)
        stale_count = 0
        for worker in workers:
            if worker.last_heartbeat_at is None:
                stale_count += 1
                continue
            last_seen = worker.last_heartbeat_at
            if last_seen.tzinfo is None:
                last_seen = last_seen.replace(tzinfo=UTC)
            if now - last_seen > timedelta(seconds=timeout_seconds):
                stale_count += 1
        counts = {status.value: 0 for status in BrowserWorkerStatus}
        for worker in workers:
            counts[worker.status] = counts.get(worker.status, 0) + 1
        return {
            "workspace_id": workspace_id,
            "total_workers": len(workers),
            "online_workers": counts.get(BrowserWorkerStatus.ONLINE.value, 0),
            "offline_workers": counts.get(BrowserWorkerStatus.OFFLINE.value, 0),
            "busy_workers": counts.get(BrowserWorkerStatus.BUSY.value, 0),
            "error_workers": counts.get(BrowserWorkerStatus.ERROR.value, 0),
            "stale_workers": stale_count,
            "active_sessions": sum(max(0, worker.active_sessions) for worker in workers),
            "max_sessions": sum(max(0, worker.max_sessions) for worker in workers),
            "workers": workers,
        }

    async def create_worker_session(
        self,
        *,
        workspace_id: str,
        worker_id: UUID,
        remote_session_id: str,
        local_browser_session_id: UUID | None,
        metadata: dict[str, Any] | None = None,
    ) -> BrowserWorkerSession:
        """Create a local-to-remote session mapping and increment load."""

        worker_session = BrowserWorkerSession(
            workspace_id=workspace_id,
            worker_id=worker_id,
            remote_session_id=remote_session_id,
            local_browser_session_id=local_browser_session_id,
            status=BrowserWorkerSessionStatus.ACTIVE.value,
            session_metadata=metadata or {},
        )
        self.session.add(worker_session)
        worker = await self.get_worker(workspace_id=workspace_id, worker_id=worker_id)
        if worker is not None:
            worker.active_sessions = max(0, worker.active_sessions) + 1
            worker.current_load = worker.active_sessions
        await self.session.flush()
        return worker_session

    async def get_worker_session_by_local(
        self,
        *,
        workspace_id: str,
        local_browser_session_id: UUID,
    ) -> BrowserWorkerSession | None:
        """Find an active worker session by local BrowserSession ID."""

        statement = select(BrowserWorkerSession).where(
            BrowserWorkerSession.workspace_id == workspace_id,
            BrowserWorkerSession.local_browser_session_id == local_browser_session_id,
            BrowserWorkerSession.status == BrowserWorkerSessionStatus.ACTIVE.value,
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_worker_session_by_remote(self, *, remote_session_id: str) -> BrowserWorkerSession | None:
        """Find a worker session by remote session ID."""

        statement = select(BrowserWorkerSession).where(BrowserWorkerSession.remote_session_id == remote_session_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def close_worker_session(self, worker_session: BrowserWorkerSession) -> BrowserWorkerSession:
        """Close a worker session and decrement load once."""

        if worker_session.status == BrowserWorkerSessionStatus.ACTIVE.value:
            worker = await self.get_worker(workspace_id=worker_session.workspace_id, worker_id=worker_session.worker_id)
            if worker is not None:
                worker.active_sessions = max(0, worker.active_sessions - 1)
                worker.current_load = worker.active_sessions
        worker_session.status = BrowserWorkerSessionStatus.CLOSED.value
        await self.session.flush()
        return worker_session

    async def fail_worker_session(self, worker_session: BrowserWorkerSession, *, error: str | None = None) -> BrowserWorkerSession:
        """Mark a worker session failed and decrement load once."""

        if worker_session.status == BrowserWorkerSessionStatus.ACTIVE.value:
            worker = await self.get_worker(workspace_id=worker_session.workspace_id, worker_id=worker_session.worker_id)
            if worker is not None:
                worker.active_sessions = max(0, worker.active_sessions - 1)
                worker.current_load = worker.active_sessions
        worker_session.status = BrowserWorkerSessionStatus.FAILED.value
        if error:
            worker_session.session_metadata = {**(worker_session.session_metadata or {}), "error": error}
        await self.session.flush()
        return worker_session

    async def list_worker_sessions(
        self,
        *,
        workspace_id: str,
        worker_id: UUID,
        status: str | None = None,
        limit: int = 100,
    ) -> list[BrowserWorkerSession]:
        """List worker session mappings."""

        statement = select(BrowserWorkerSession).where(
            BrowserWorkerSession.workspace_id == workspace_id,
            BrowserWorkerSession.worker_id == worker_id,
        )
        if status is not None:
            statement = statement.where(BrowserWorkerSession.status == status)
        statement = statement.order_by(BrowserWorkerSession.created_at.desc()).limit(limit)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def create_worker_action(
        self,
        *,
        workspace_id: str,
        worker_id: UUID,
        worker_session_id: UUID,
        local_action_id: UUID | None,
        action_type: str,
        request_payload: dict[str, Any],
        max_retries: int = 0,
    ) -> BrowserWorkerAction:
        """Create a remote worker action scheduling record."""

        action = BrowserWorkerAction(
            workspace_id=workspace_id,
            worker_id=worker_id,
            worker_session_id=worker_session_id,
            local_action_id=local_action_id,
            action_type=action_type,
            request_payload=request_payload,
            max_retries=max_retries,
            status=BrowserWorkerActionStatus.RUNNING.value,
        )
        self.session.add(action)
        await self.session.flush()
        return action

    async def complete_worker_action(
        self,
        action: BrowserWorkerAction,
        *,
        remote_action_id: str | None,
        response_payload: dict[str, Any],
        duration_ms: int,
        retry_count: int = 0,
    ) -> BrowserWorkerAction:
        """Mark a remote worker action completed."""

        action.status = BrowserWorkerActionStatus.COMPLETED.value
        action.remote_action_id = remote_action_id
        action.response_payload = response_payload
        action.duration_ms = duration_ms
        action.retry_count = retry_count
        action.error = None
        await self.session.flush()
        return action

    async def fail_worker_action(
        self,
        action: BrowserWorkerAction,
        *,
        response_payload: dict[str, Any] | None,
        error: str,
        duration_ms: int,
        retry_count: int = 0,
    ) -> BrowserWorkerAction:
        """Mark a remote worker action failed."""

        action.status = BrowserWorkerActionStatus.FAILED.value
        action.response_payload = response_payload
        action.duration_ms = duration_ms
        action.retry_count = retry_count
        action.error = error
        await self.session.flush()
        return action
