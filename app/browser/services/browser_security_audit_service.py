"""Browser security audit log service."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.browser import BrowserSecurityAuditLog


class BrowserSecurityAuditService:
    """集中记录 Browser Worker / UI Access / Policy 安全审计事件。"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def log_event(
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
        ip_address: str | None = None,
        user_agent: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> BrowserSecurityAuditLog:
        """写入一条 workspace-scoped 安全审计日志。"""

        log = BrowserSecurityAuditLog(
            workspace_id=workspace_id,
            actor_type=actor_type,
            actor_id=actor_id,
            event_type=event_type,
            target_type=target_type,
            target_id=target_id,
            success=success,
            error=error,
            ip_address=ip_address,
            user_agent=user_agent,
            audit_metadata=metadata or {},
        )
        self.session.add(log)
        await self.session.flush()
        return log

    async def list_logs(
        self,
        *,
        workspace_id: str,
        event_type: str | None = None,
        limit: int = 100,
    ) -> list[BrowserSecurityAuditLog]:
        """列出当前 workspace 的安全审计日志。"""

        statement = select(BrowserSecurityAuditLog).where(BrowserSecurityAuditLog.workspace_id == workspace_id)
        if event_type:
            statement = statement.where(BrowserSecurityAuditLog.event_type == event_type)
        statement = statement.order_by(BrowserSecurityAuditLog.created_at.desc()).limit(limit)
        result = await self.session.execute(statement)
        return list(result.scalars().all())
