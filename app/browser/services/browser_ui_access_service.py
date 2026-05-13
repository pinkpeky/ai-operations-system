"""Browser UI Access Placeholder 服务。

当前阶段只生成占位访问 URL 与一次性 token，不提供真实 VNC/noVNC/DevTools 远程 UI。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
import hashlib
import logging
import secrets
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.repositories import BrowserRepository
from app.browser.services.browser_security_audit_service import BrowserSecurityAuditService
from app.core.config import Settings, get_settings
from app.models.browser import (
    BrowserHumanControlEvent,
    BrowserHumanControlSession,
    BrowserSession,
    BrowserUIAccessSession,
)
from app.models.enums import BrowserHumanControlEventType, BrowserHumanControlStatus, BrowserUIAccessStatus

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class BrowserUIAccessCreation:
    """UI access 创建结果，token 只在这里明文返回一次。"""

    access_session: BrowserUIAccessSession
    access_token: str


@dataclass(slots=True)
class BrowserUIAccessValidation:
    """UI access token 校验结果。"""

    access_session: BrowserUIAccessSession | None
    valid: bool
    reason: str | None = None


class BrowserUIAccessService:
    """按 workspace 隔离管理 UI Access Placeholder session。"""

    def __init__(self, session: AsyncSession, *, settings: Settings | None = None) -> None:
        self.session = session
        self.settings = settings or get_settings()
        self.browser_repository = BrowserRepository(session)
        self.audit = BrowserSecurityAuditService(session)

    async def create_access_session(
        self,
        *,
        workspace_id: str,
        browser_session_id: UUID,
        human_control_session_id: UUID | None = None,
        scopes: list[str] | None = None,
        one_time: bool = False,
        client_ip: str | None = None,
        user_agent: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> BrowserUIAccessCreation:
        """创建占位 UI access session，并只返回一次明文 token。"""

        browser_session = await self._get_browser_session(workspace_id=workspace_id, browser_session_id=browser_session_id)
        control_session: BrowserHumanControlSession | None = None
        if human_control_session_id is not None:
            control_session = await self._get_human_control_session(
                workspace_id=workspace_id,
                control_session_id=human_control_session_id,
            )
            if control_session.browser_session_id != browser_session.id:
                raise ValueError("Human control session does not belong to browser session")
            if control_session.status != BrowserHumanControlStatus.ACTIVE.value:
                raise ValueError("UI access can only be created for an active human control session")

        token = self.generate_access_token()
        expires_at = datetime.now(UTC) + timedelta(seconds=self.settings.browser_ui_access_timeout_seconds)
        access_session = BrowserUIAccessSession(
            workspace_id=workspace_id,
            browser_session_id=browser_session.id,
            human_control_session_id=human_control_session_id,
            worker_id=self._worker_id(browser_session),
            access_token_hash=self._hash_token(token),
            remote_control_url=f"http://localhost:8000/ui/browser-control/{{access_session_id}}",
            live_view_url=f"http://localhost:8000/ui/browser-live/{{access_session_id}}",
            devtools_url=None,
            scopes=scopes or ["view"],
            one_time=one_time,
            client_ip=client_ip,
            user_agent=user_agent,
            status=BrowserUIAccessStatus.ACTIVE.value,
            expires_at=expires_at,
            access_metadata={
                **(metadata or {}),
                "placeholder": True,
                "vnc": False,
                "novnc": False,
                "devtools": False,
                "note": "placeholder URL only; no real remote desktop is implemented",
            },
        )
        self.session.add(access_session)
        await self.session.flush()
        access_session.remote_control_url = access_session.remote_control_url.format(access_session_id=access_session.id)
        access_session.live_view_url = access_session.live_view_url.format(access_session_id=access_session.id)
        await self._log_browser(
            browser_session=browser_session,
            level="info",
            message="Browser UI access placeholder created",
            metadata={
                "access_session_id": str(access_session.id),
                "human_control_session_id": str(human_control_session_id) if human_control_session_id else None,
                "placeholder": True,
            },
        )
        await self.audit.log_event(
            workspace_id=workspace_id,
            actor_type="user",
            actor_id=browser_session.user_id,
            event_type="ui_token_created",
            target_type="browser_ui_access_session",
            target_id=str(access_session.id),
            success=True,
            ip_address=client_ip,
            user_agent=user_agent,
            metadata={"scopes": access_session.scopes, "one_time": one_time, "placeholder": True},
        )
        if control_session is not None:
            await self._add_human_control_note(
                workspace_id=workspace_id,
                control_session_id=control_session.id,
                message="ui access placeholder created",
                payload={"access_session_id": str(access_session.id), "placeholder": True},
            )
        await self.session.commit()
        await self.session.refresh(access_session)
        logger.info(
            "Browser UI access placeholder created",
            extra={"workspace_id": workspace_id, "access_session_id": str(access_session.id)},
        )
        return BrowserUIAccessCreation(access_session=access_session, access_token=token)

    async def get_access_session(
        self,
        *,
        workspace_id: str,
        access_session_id: UUID,
    ) -> BrowserUIAccessSession | None:
        """读取当前 workspace 的 UI access session，不返回明文 token。"""

        statement = select(BrowserUIAccessSession).where(
            BrowserUIAccessSession.workspace_id == workspace_id,
            BrowserUIAccessSession.id == access_session_id,
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def revoke_access_session(
        self,
        *,
        workspace_id: str,
        access_session_id: UUID,
        reason: str | None = None,
    ) -> BrowserUIAccessSession:
        """撤销 UI access session。"""

        access_session = await self._get_access_session(workspace_id=workspace_id, access_session_id=access_session_id)
        if access_session.status in {BrowserUIAccessStatus.REVOKED.value, BrowserUIAccessStatus.EXPIRED.value}:
            return access_session
        access_session.status = BrowserUIAccessStatus.REVOKED.value
        access_session.revoked_reason = reason
        browser_session = await self._get_browser_session(workspace_id=workspace_id, browser_session_id=access_session.browser_session_id)
        await self._log_browser(
            browser_session=browser_session,
            level="info",
            message="Browser UI access placeholder revoked",
            metadata={"access_session_id": str(access_session.id), "reason": reason},
        )
        await self.audit.log_event(
            workspace_id=workspace_id,
            actor_type="user",
            actor_id=browser_session.user_id,
            event_type="ui_token_revoked",
            target_type="browser_ui_access_session",
            target_id=str(access_session.id),
            success=True,
            error=reason,
            metadata={"reason": reason},
        )
        await self.session.commit()
        await self.session.refresh(access_session)
        return access_session

    async def expire_access_sessions(self, *, workspace_id: str) -> list[BrowserUIAccessSession]:
        """过期当前 workspace 中已经超时的 UI access sessions。"""

        now = datetime.now(UTC)
        statement = select(BrowserUIAccessSession).where(
            BrowserUIAccessSession.workspace_id == workspace_id,
            BrowserUIAccessSession.status.in_([BrowserUIAccessStatus.ACTIVE.value, BrowserUIAccessStatus.REQUESTED.value]),
            BrowserUIAccessSession.expires_at <= now,
        )
        result = await self.session.execute(statement)
        access_sessions = list(result.scalars().all())
        for access_session in access_sessions:
            access_session.status = BrowserUIAccessStatus.EXPIRED.value
            access_session.revoked_reason = "expired"
            browser_session = await self._get_browser_session(
                workspace_id=workspace_id,
                browser_session_id=access_session.browser_session_id,
            )
            await self._log_browser(
                browser_session=browser_session,
                level="warning",
                message="Browser UI access placeholder expired",
                metadata={"access_session_id": str(access_session.id)},
            )
            await self.audit.log_event(
                workspace_id=workspace_id,
                actor_type="system",
                actor_id=None,
                event_type="ui_token_expired",
                target_type="browser_ui_access_session",
                target_id=str(access_session.id),
                success=True,
                metadata={"expires_at": access_session.expires_at.isoformat()},
            )
        await self.session.commit()
        for access_session in access_sessions:
            await self.session.refresh(access_session)
        return access_sessions

    def generate_access_token(self) -> str:
        """生成一次性 UI access token。"""

        return secrets.token_urlsafe(32)

    async def validate_access_token(
        self,
        *,
        workspace_id: str,
        access_session_id: UUID,
        token: str,
        scope: str | None = None,
        client_ip: str | None = None,
        user_agent: str | None = None,
    ) -> BrowserUIAccessValidation:
        """校验 UI access token，并记录成功/失败日志。"""

        access_session = await self.get_access_session(workspace_id=workspace_id, access_session_id=access_session_id)
        if access_session is None:
            return BrowserUIAccessValidation(access_session=None, valid=False, reason="not_found")

        browser_session = await self._get_browser_session(workspace_id=workspace_id, browser_session_id=access_session.browser_session_id)
        if access_session.status != BrowserUIAccessStatus.ACTIVE.value:
            await self._log_browser(
                browser_session=browser_session,
                level="warning",
                message="Browser UI access token validation failed",
                metadata={"access_session_id": str(access_session.id), "reason": f"status:{access_session.status}"},
            )
            await self._audit_validation(
                workspace_id=workspace_id,
                browser_session=browser_session,
                access_session=access_session,
                valid=False,
                reason=f"status:{access_session.status}",
                scope=scope,
                client_ip=client_ip,
                user_agent=user_agent,
            )
            await self.session.commit()
            return BrowserUIAccessValidation(access_session=access_session, valid=False, reason=f"status:{access_session.status}")

        if self._is_expired(access_session.expires_at):
            access_session.status = BrowserUIAccessStatus.EXPIRED.value
            access_session.revoked_reason = "expired"
            await self._log_browser(
                browser_session=browser_session,
                level="warning",
                message="Browser UI access token validation failed",
                metadata={"access_session_id": str(access_session.id), "reason": "expired"},
            )
            await self._audit_validation(
                workspace_id=workspace_id,
                browser_session=browser_session,
                access_session=access_session,
                valid=False,
                reason="expired",
                scope=scope,
                client_ip=client_ip,
                user_agent=user_agent,
            )
            await self.session.commit()
            await self.session.refresh(access_session)
            return BrowserUIAccessValidation(access_session=access_session, valid=False, reason="expired")

        if scope and scope not in (access_session.scopes or []):
            await self._log_browser(
                browser_session=browser_session,
                level="warning",
                message="Browser UI access token validation failed",
                metadata={"access_session_id": str(access_session.id), "reason": f"scope_denied:{scope}", "scope": scope},
            )
            await self._audit_validation(
                workspace_id=workspace_id,
                browser_session=browser_session,
                access_session=access_session,
                valid=False,
                reason=f"scope_denied:{scope}",
                scope=scope,
                client_ip=client_ip,
                user_agent=user_agent,
            )
            await self.session.commit()
            return BrowserUIAccessValidation(access_session=access_session, valid=False, reason=f"scope_denied:{scope}")

        if access_session.one_time and access_session.used_at is not None:
            await self._audit_validation(
                workspace_id=workspace_id,
                browser_session=browser_session,
                access_session=access_session,
                valid=False,
                reason="one_time_used",
                scope=scope,
                client_ip=client_ip,
                user_agent=user_agent,
            )
            await self.session.commit()
            return BrowserUIAccessValidation(access_session=access_session, valid=False, reason="one_time_used")

        valid = secrets.compare_digest(access_session.access_token_hash, self._hash_token(token))
        if valid and access_session.one_time:
            access_session.used_at = datetime.now(UTC)
        await self._log_browser(
            browser_session=browser_session,
            level="info" if valid else "warning",
            message="Browser UI access token validation succeeded" if valid else "Browser UI access token validation failed",
            metadata={"access_session_id": str(access_session.id), "reason": None if valid else "token_mismatch"},
        )
        await self._audit_validation(
            workspace_id=workspace_id,
            browser_session=browser_session,
            access_session=access_session,
            valid=valid,
            reason=None if valid else "token_mismatch",
            scope=scope,
            client_ip=client_ip,
            user_agent=user_agent,
        )
        await self.session.commit()
        return BrowserUIAccessValidation(
            access_session=access_session,
            valid=valid,
            reason=None if valid else "token_mismatch",
        )

    async def _audit_validation(
        self,
        *,
        workspace_id: str,
        browser_session: BrowserSession,
        access_session: BrowserUIAccessSession,
        valid: bool,
        reason: str | None,
        scope: str | None,
        client_ip: str | None,
        user_agent: str | None,
    ) -> None:
        await self.audit.log_event(
            workspace_id=workspace_id,
            actor_type="user",
            actor_id=browser_session.user_id,
            event_type="ui_token_validated" if valid else "ui_token_validation_failed",
            target_type="browser_ui_access_session",
            target_id=str(access_session.id),
            success=valid,
            error=reason,
            ip_address=client_ip,
            user_agent=user_agent,
            metadata={"scope": scope, "one_time": access_session.one_time},
        )

    async def _get_access_session(self, *, workspace_id: str, access_session_id: UUID) -> BrowserUIAccessSession:
        access_session = await self.get_access_session(workspace_id=workspace_id, access_session_id=access_session_id)
        if access_session is None:
            raise ValueError("UI access session not found")
        return access_session

    async def _get_browser_session(self, *, workspace_id: str, browser_session_id: UUID) -> BrowserSession:
        browser_session = await self.browser_repository.get_session(session_id=browser_session_id, workspace_id=workspace_id)
        if browser_session is None:
            raise ValueError("Browser session not found")
        return browser_session

    async def _get_human_control_session(
        self,
        *,
        workspace_id: str,
        control_session_id: UUID,
    ) -> BrowserHumanControlSession:
        statement = select(BrowserHumanControlSession).where(
            BrowserHumanControlSession.workspace_id == workspace_id,
            BrowserHumanControlSession.id == control_session_id,
        )
        result = await self.session.execute(statement)
        control_session = result.scalar_one_or_none()
        if control_session is None:
            raise ValueError("Human control session not found")
        return control_session

    async def _add_human_control_note(
        self,
        *,
        workspace_id: str,
        control_session_id: UUID,
        message: str,
        payload: dict[str, Any],
    ) -> None:
        event = BrowserHumanControlEvent(
            workspace_id=workspace_id,
            control_session_id=control_session_id,
            event_type=BrowserHumanControlEventType.NOTE.value,
            message=message,
            payload=payload,
        )
        self.session.add(event)
        await self.session.flush()

    async def _log_browser(
        self,
        *,
        browser_session: BrowserSession,
        level: str,
        message: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        await self.browser_repository.create_log(
            workspace_id=browser_session.workspace_id,
            session_id=browser_session.id,
            action_id=None,
            level=level,
            message=message,
            metadata=metadata,
        )

    @staticmethod
    def _hash_token(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    @staticmethod
    def _is_expired(expires_at: datetime) -> bool:
        """兼容 SQLite 返回 naive datetime 的测试环境。"""

        normalized = expires_at if expires_at.tzinfo is not None else expires_at.replace(tzinfo=UTC)
        return normalized <= datetime.now(UTC)

    @staticmethod
    def _worker_id(browser_session: BrowserSession) -> UUID | None:
        value = (browser_session.provider_session_metadata or {}).get("worker_id")
        if value is None:
            return None
        try:
            return UUID(str(value))
        except Exception:
            return None
