"""Browser action permission policy service."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.remote.services.browser_worker_repository import BrowserWorkerRepository
from app.browser.services.browser_security_audit_service import BrowserSecurityAuditService
from app.core.config import Settings, get_settings
from app.models.browser import BrowserSession, BrowserUIAccessSession
from app.models.enums import BrowserUIAccessStatus


@dataclass(slots=True)
class BrowserActionPolicyResult:
    """Browser action policy check result."""

    allowed: bool
    reason: str | None = None
    metadata: dict[str, Any] | None = None


class BrowserActionPolicyService:
    """校验浏览器动作类型、目标域名、worker 能力、profile 与 UI access scope。"""

    SUPPORTED_ACTIONS = {"navigate", "click", "type_text", "scroll", "screenshot", "get_page_content"}

    def __init__(self, session: AsyncSession, *, settings: Settings | None = None) -> None:
        self.session = session
        self.settings = settings or get_settings()
        self.worker_repository = BrowserWorkerRepository(session)
        self.audit = BrowserSecurityAuditService(session)

    async def check_action_policy(
        self,
        *,
        workspace_id: str,
        browser_session: BrowserSession | None,
        action_type: str,
        target: str | None,
        input_payload: dict[str, Any] | None = None,
    ) -> BrowserActionPolicyResult:
        """执行 browser action policy check，并在拒绝时写审计。"""

        metadata: dict[str, Any] = {"action_type": action_type, "target": target}
        action_result = self.validate_action_type(action_type)
        if not action_result.allowed:
            await self._audit_block(workspace_id=workspace_id, reason=action_result.reason, metadata=metadata)
            return action_result

        domain_result = self.validate_target_domain(action_type=action_type, target=target)
        if not domain_result.allowed:
            await self._audit_block(workspace_id=workspace_id, reason=domain_result.reason, metadata={**metadata, **(domain_result.metadata or {})})
            return domain_result

        if browser_session is not None:
            profile_result = self.validate_profile_access(workspace_id=workspace_id, browser_session=browser_session)
            if not profile_result.allowed:
                await self._audit_block(workspace_id=workspace_id, reason=profile_result.reason, metadata=metadata)
                return profile_result

            worker_result = await self.validate_worker_capability(
                workspace_id=workspace_id,
                browser_session=browser_session,
                action_type=action_type,
            )
            if not worker_result.allowed:
                await self._audit_block(
                    workspace_id=workspace_id,
                    reason=worker_result.reason,
                    metadata={**metadata, **(worker_result.metadata or {})},
                )
                return worker_result

        access_session = (input_payload or {}).get("_ui_access_session")
        scope = (input_payload or {}).get("_ui_access_scope")
        if isinstance(access_session, BrowserUIAccessSession) and scope:
            scope_result = self.validate_ui_access_scope(access_session=access_session, scope=str(scope))
            if not scope_result.allowed:
                await self._audit_block(workspace_id=workspace_id, reason=scope_result.reason, metadata=metadata)
                return scope_result

        return BrowserActionPolicyResult(allowed=True, metadata=metadata)

    def validate_action_type(self, action_type: str) -> BrowserActionPolicyResult:
        """校验 action_type 是否在允许集合中。"""

        if action_type not in self.SUPPORTED_ACTIONS:
            return BrowserActionPolicyResult(allowed=False, reason=f"Unsupported browser action_type: {action_type}")
        return BrowserActionPolicyResult(allowed=True)

    def validate_target_domain(self, *, action_type: str, target: str | None) -> BrowserActionPolicyResult:
        """校验 navigate 目标域名，默认只允许 example.com / localhost / 127.0.0.1。"""

        if action_type != "navigate" or not target:
            return BrowserActionPolicyResult(allowed=True)
        parsed = urlparse(target)
        hostname = (parsed.hostname or "").lower()
        if not hostname:
            return BrowserActionPolicyResult(allowed=False, reason="target_domain_missing")
        if hostname in self.settings.browser_blocked_domain_set:
            return BrowserActionPolicyResult(allowed=False, reason=f"domain_blocked:{hostname}", metadata={"hostname": hostname})
        if self.settings.browser_allow_external_domains:
            return BrowserActionPolicyResult(allowed=True, metadata={"hostname": hostname})
        for allowed in self.settings.browser_allowed_domain_set:
            if hostname == allowed or hostname.endswith(f".{allowed}"):
                return BrowserActionPolicyResult(allowed=True, metadata={"hostname": hostname})
        return BrowserActionPolicyResult(allowed=False, reason=f"domain_not_allowed:{hostname}", metadata={"hostname": hostname})

    def validate_profile_access(self, *, workspace_id: str, browser_session: BrowserSession) -> BrowserActionPolicyResult:
        """校验 session/profile 是否仍在当前 workspace。"""

        if browser_session.workspace_id != workspace_id:
            return BrowserActionPolicyResult(allowed=False, reason="profile_access_denied")
        return BrowserActionPolicyResult(allowed=True)

    async def validate_worker_capability(
        self,
        *,
        workspace_id: str,
        browser_session: BrowserSession,
        action_type: str,
    ) -> BrowserActionPolicyResult:
        """校验 worker allowed_actions 与 capabilities。"""

        worker_id = self._session_worker_id(browser_session)
        if worker_id is None:
            return BrowserActionPolicyResult(allowed=True)
        worker = await self.worker_repository.get_worker(workspace_id=workspace_id, worker_id=worker_id)
        if worker is None:
            return BrowserActionPolicyResult(allowed=False, reason="worker_not_found")
        allowed_actions = worker.allowed_actions or []
        if allowed_actions and action_type not in allowed_actions:
            return BrowserActionPolicyResult(
                allowed=False,
                reason=f"worker_action_not_allowed:{action_type}",
                metadata={"worker_id": str(worker.id), "allowed_actions": allowed_actions},
            )
        capability_name = "page_content" if action_type == "get_page_content" else action_type
        if action_type in {"screenshot", "get_page_content", "click", "type_text", "scroll"}:
            if not bool((worker.capabilities or {}).get(capability_name)):
                return BrowserActionPolicyResult(
                    allowed=False,
                    reason=f"worker_capability_missing:{capability_name}",
                    metadata={"worker_id": str(worker.id), "capability": capability_name},
                )
        return BrowserActionPolicyResult(allowed=True, metadata={"worker_id": str(worker.id)})

    def validate_ui_access_scope(self, *, access_session: BrowserUIAccessSession, scope: str) -> BrowserActionPolicyResult:
        """校验 UI access token scope。"""

        if access_session.status != BrowserUIAccessStatus.ACTIVE.value:
            return BrowserActionPolicyResult(allowed=False, reason=f"ui_access_status:{access_session.status}")
        if scope not in (access_session.scopes or []):
            return BrowserActionPolicyResult(allowed=False, reason=f"ui_access_scope_denied:{scope}")
        return BrowserActionPolicyResult(allowed=True)

    async def _audit_block(self, *, workspace_id: str, reason: str | None, metadata: dict[str, Any]) -> None:
        await self.audit.log_event(
            workspace_id=workspace_id,
            actor_type="system",
            actor_id=None,
            event_type="action_blocked_by_policy",
            target_type="browser_action",
            target_id=None,
            success=False,
            error=reason,
            metadata=metadata,
        )

    @staticmethod
    def _session_worker_id(browser_session: BrowserSession) -> UUID | None:
        value = (browser_session.provider_session_metadata or {}).get("worker_id")
        if value is None:
            return None
        try:
            return UUID(str(value))
        except Exception:
            return None
