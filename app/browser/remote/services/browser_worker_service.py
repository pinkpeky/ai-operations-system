"""Remote Browser Worker business service."""

from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.remote.services.browser_worker_auth_service import BrowserWorkerAuthService
from app.browser.remote.services.browser_worker_repository import BrowserWorkerRepository
from app.core.config import Settings, get_settings
from app.models.browser import BrowserSecurityAuditLog
from app.models.browser_worker import BrowserWorker
from app.models.enums import BrowserWorkerAuthStatus, BrowserWorkerStatus

logger = logging.getLogger(__name__)


class BrowserWorkerService:
    """Worker registration, heartbeat, auth rotation and query service."""

    def __init__(self, session: AsyncSession, *, settings: Settings | None = None) -> None:
        self.session = session
        self.settings = settings or get_settings()
        self.repository = BrowserWorkerRepository(session)
        self.auth = BrowserWorkerAuthService()
        self.last_worker_secret: str | None = None

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
        allowed_actions: list[str] | None = None,
        allowed_domains: list[str] | None = None,
        generate_secret: bool = True,
    ) -> BrowserWorker:
        """Register or update one worker.

        When `generate_secret` is true, plaintext secret is returned once through
        the API response and cached only in the current API process for request signing.
        """

        try:
            configured_secret = self.settings.browser_worker_shared_secret.strip()
            worker_secret = configured_secret if generate_secret and configured_secret else (self.auth.generate_worker_secret() if generate_secret else None)
            worker_secret_hash = self.auth.hash_secret(worker_secret) if worker_secret else None
            worker = await self.repository.register_worker(
                workspace_id=workspace_id,
                worker_name=worker_name,
                worker_type=worker_type,
                base_url=base_url,
                capabilities=capabilities,
                metadata=metadata,
                max_sessions=max_sessions,
                max_actions_per_minute=max_actions_per_minute,
                priority=priority,
                worker_secret_hash=worker_secret_hash,
                allowed_actions=allowed_actions or self._default_allowed_actions(),
                allowed_domains=allowed_domains or sorted(self.settings.browser_allowed_domain_set),
            )
            if worker_secret is not None:
                self.auth.cache_worker_secret(worker.id, worker_secret)
            self.last_worker_secret = worker_secret
            await self._log_audit(
                workspace_id=workspace_id,
                actor_type="system",
                actor_id=None,
                event_type="worker_registered",
                target_type="browser_worker",
                target_id=str(worker.id),
                success=True,
                metadata={"worker_name": worker_name, "secret_returned_once": bool(worker_secret)},
            )
            await self.session.commit()
            await self.session.refresh(worker)
            logger.info("Browser worker registered", extra={"workspace_id": workspace_id, "worker_id": str(worker.id)})
            return worker
        except Exception:
            await self.session.rollback()
            logger.exception("Browser worker registration failed", extra={"workspace_id": workspace_id, "worker_name": worker_name})
            raise

    async def heartbeat_worker(
        self,
        *,
        workspace_id: str,
        worker_id: UUID,
        status: str,
        capabilities: dict[str, Any],
        metadata: dict[str, Any],
        worker_secret: str | None = None,
    ) -> BrowserWorker:
        """Update worker heartbeat and optionally verify worker secret."""

        if status not in {item.value for item in BrowserWorkerStatus}:
            raise ValueError(f"Unsupported worker status: {status}")
        worker = await self.repository.get_worker(workspace_id=workspace_id, worker_id=worker_id)
        if worker is None:
            raise ValueError("Browser worker not found")
        await self._verify_worker_secret(
            workspace_id=workspace_id,
            worker=worker,
            worker_secret=worker_secret,
            event_type="worker_heartbeat_auth",
        )
        try:
            updated = await self.repository.heartbeat_worker(
                worker=worker,
                status=status,
                capabilities=capabilities,
                metadata=metadata,
            )
            await self.session.commit()
            await self.session.refresh(updated)
            logger.info("Browser worker heartbeat updated", extra={"workspace_id": workspace_id, "worker_id": str(worker_id)})
            return updated
        except Exception:
            await self.session.rollback()
            logger.exception("Browser worker heartbeat failed", extra={"workspace_id": workspace_id, "worker_id": str(worker_id)})
            raise

    async def rotate_worker_secret(self, *, workspace_id: str, worker_id: UUID) -> tuple[BrowserWorker, str]:
        """Rotate worker secret and return plaintext only once."""

        worker = await self.repository.get_worker(workspace_id=workspace_id, worker_id=worker_id)
        if worker is None:
            raise ValueError("Browser worker not found")
        secret = self.auth.generate_worker_secret()
        updated = await self.repository.rotate_worker_secret(worker=worker, worker_secret_hash=self.auth.hash_secret(secret))
        self.auth.cache_worker_secret(worker_id, secret)
        await self._log_audit(
            workspace_id=workspace_id,
            actor_type="system",
            actor_id=None,
            event_type="worker_secret_rotated",
            target_type="browser_worker",
            target_id=str(worker_id),
            success=True,
            metadata={"secret_returned_once": True},
        )
        await self.session.commit()
        await self.session.refresh(updated)
        return updated, secret

    async def revoke_worker(self, *, workspace_id: str, worker_id: UUID, reason: str | None = None) -> BrowserWorker:
        """Revoke worker auth and mark worker offline."""

        worker = await self.repository.get_worker(workspace_id=workspace_id, worker_id=worker_id)
        if worker is None:
            raise ValueError("Browser worker not found")
        updated = await self.repository.revoke_worker_auth(worker=worker, error_message=reason or "worker auth revoked")
        self.auth.pop_cached_secret(worker_id)
        await self._log_audit(
            workspace_id=workspace_id,
            actor_type="system",
            actor_id=None,
            event_type="worker_revoked",
            target_type="browser_worker",
            target_id=str(worker_id),
            success=True,
            error=reason,
        )
        await self.session.commit()
        await self.session.refresh(updated)
        return updated

    async def list_workers(
        self,
        *,
        workspace_id: str,
        status: str | None = None,
        worker_type: str | None = None,
        limit: int = 100,
    ) -> list[BrowserWorker]:
        """List workspace-scoped workers."""

        return await self.repository.list_workers(
            workspace_id=workspace_id,
            status=status,
            worker_type=worker_type,
            limit=limit,
        )

    async def _verify_worker_secret(
        self,
        *,
        workspace_id: str,
        worker: BrowserWorker,
        worker_secret: str | None,
        event_type: str,
    ) -> None:
        """Verify optional worker secret under strict/non-strict local policy."""

        if not self.settings.browser_worker_auth_enabled:
            return
        if worker.auth_status == BrowserWorkerAuthStatus.REVOKED.value:
            await self._audit_auth(worker=worker, workspace_id=workspace_id, event_type=event_type, success=False, error="worker_auth_revoked")
            raise ValueError("Worker auth revoked")
        if worker_secret and self.auth.verify_secret(secret=worker_secret, secret_hash=worker.worker_secret_hash):
            await self.repository.mark_worker_auth_success(worker=worker)
            await self._audit_auth(worker=worker, workspace_id=workspace_id, event_type=event_type, success=True, error=None)
            return
        if worker_secret:
            await self.repository.mark_worker_auth_failed(worker=worker, error_message="worker secret mismatch")
            await self._audit_auth(worker=worker, workspace_id=workspace_id, event_type=event_type, success=False, error="worker_secret_mismatch")
            if self.settings.browser_worker_auth_strict:
                raise ValueError("Worker auth failed")
            return
        if self.settings.browser_worker_auth_strict:
            await self.repository.mark_worker_auth_failed(worker=worker, error_message="worker secret missing")
            await self._audit_auth(worker=worker, workspace_id=workspace_id, event_type=event_type, success=False, error="worker_secret_missing")
            raise ValueError("Worker auth required")

    async def _audit_auth(
        self,
        *,
        worker: BrowserWorker,
        workspace_id: str,
        event_type: str,
        success: bool,
        error: str | None,
    ) -> None:
        await self._log_audit(
            workspace_id=workspace_id,
            actor_type="browser_worker",
            actor_id=str(worker.id),
            event_type=event_type if success else "worker_auth_failed",
            target_type="browser_worker",
            target_id=str(worker.id),
            success=success,
            error=error,
        )

    async def _log_audit(
        self,
        *,
        workspace_id: str,
        actor_type: str,
        actor_id: str | None,
        event_type: str,
        target_type: str,
        target_id: str | None,
        success: bool,
        error: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Write an audit log without importing BrowserService package."""

        self.session.add(
            BrowserSecurityAuditLog(
                workspace_id=workspace_id,
                actor_type=actor_type,
                actor_id=actor_id,
                event_type=event_type,
                target_type=target_type,
                target_id=target_id,
                success=success,
                error=error,
                audit_metadata=metadata or {},
            )
        )
        await self.session.flush()

    @staticmethod
    def _default_allowed_actions() -> list[str]:
        return ["navigate", "click", "type_text", "scroll", "screenshot", "get_page_content"]
