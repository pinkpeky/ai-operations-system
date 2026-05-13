"""Browser 数据 Repository。

所有查询都强制带 workspace 范围，避免 browser session/action/log 在多人
环境下串库。Repository 只负责持久化，provider 调用放在 BrowserService。
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.browser import BrowserAction, BrowserActionLog, BrowserSession
from app.models.enums import BrowserActionStatus, BrowserSessionStatus


class BrowserRepository:
    """Browser session、action、log 的数据访问层。"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_session(
        self,
        *,
        workspace_id: str,
        user_id: str | None,
        provider: str,
        metadata: dict[str, Any] | None = None,
        profile_id: UUID | None = None,
        profile_path: str | None = None,
        persistent_context_enabled: bool = False,
    ) -> BrowserSession:
        """创建 browser session 记录。"""

        browser_session = BrowserSession(
            workspace_id=workspace_id,
            user_id=user_id,
            provider=provider,
            profile_id=profile_id,
            profile_path=profile_path,
            persistent_context_enabled=persistent_context_enabled,
            status=BrowserSessionStatus.ACTIVE.value,
            session_metadata=metadata or {},
        )
        self.session.add(browser_session)
        await self.session.flush()
        return browser_session

    async def get_session(self, *, session_id: UUID, workspace_id: str) -> BrowserSession | None:
        """按 workspace 加载单个 browser session。"""

        statement = select(BrowserSession).where(
            BrowserSession.id == session_id,
            BrowserSession.workspace_id == workspace_id,
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def list_sessions(
        self,
        *,
        workspace_id: str,
        status: str | None = None,
        limit: int = 100,
    ) -> list[BrowserSession]:
        """列出一个 workspace 下的 browser sessions。"""

        statement = select(BrowserSession).where(BrowserSession.workspace_id == workspace_id)
        if status is not None:
            statement = statement.where(BrowserSession.status == status)
        statement = statement.order_by(BrowserSession.created_at.desc()).limit(limit)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def update_session_status(
        self,
        *,
        browser_session: BrowserSession,
        status: str,
        metadata_patch: dict[str, Any] | None = None,
        browser_id: str | None = None,
        page_id: str | None = None,
        provider_session_metadata: dict[str, Any] | None = None,
    ) -> BrowserSession:
        """更新 session 状态，并可追加 metadata。"""

        browser_session.status = status
        if browser_id is not None:
            browser_session.browser_id = browser_id
        if page_id is not None:
            browser_session.page_id = page_id
        if provider_session_metadata is not None:
            browser_session.provider_session_metadata = provider_session_metadata
        if metadata_patch:
            browser_session.session_metadata = {**(browser_session.session_metadata or {}), **metadata_patch}
        await self.session.flush()
        return browser_session

    async def create_action(
        self,
        *,
        workspace_id: str,
        session_id: UUID,
        action_type: str,
        target: str | None,
        input_payload: dict[str, Any] | None = None,
        selector: str | None = None,
        target_url: str | None = None,
    ) -> BrowserAction:
        """创建 pending browser action。"""

        action = BrowserAction(
            workspace_id=workspace_id,
            session_id=session_id,
            action_type=action_type,
            target=target,
            selector=selector,
            target_url=target_url,
            input_payload=input_payload or {},
            status=BrowserActionStatus.PENDING.value,
        )
        self.session.add(action)
        await self.session.flush()
        return action

    async def mark_action_running(self, action: BrowserAction) -> BrowserAction:
        """标记 action 为 running。"""

        action.status = BrowserActionStatus.RUNNING.value
        await self.session.flush()
        return action

    async def complete_action(
        self,
        action: BrowserAction,
        *,
        output_payload: dict[str, Any],
        duration_ms: int,
        selector: str | None = None,
        target_url: str | None = None,
        screenshot_path: str | None = None,
        page_title: str | None = None,
    ) -> BrowserAction:
        """标记 action 为 completed。"""

        action.status = BrowserActionStatus.COMPLETED.value
        action.output_payload = output_payload
        action.duration_ms = duration_ms
        action.selector = selector if selector is not None else action.selector
        action.target_url = target_url if target_url is not None else action.target_url
        action.screenshot_path = screenshot_path
        action.page_title = page_title
        action.error = None
        await self.session.flush()
        return action

    async def fail_action(
        self,
        action: BrowserAction,
        *,
        error: str,
        duration_ms: int,
        screenshot_path: str | None = None,
        page_title: str | None = None,
    ) -> BrowserAction:
        """标记 action 为 failed。"""

        action.status = BrowserActionStatus.FAILED.value
        action.error = error
        action.duration_ms = duration_ms
        action.screenshot_path = screenshot_path
        action.page_title = page_title
        await self.session.flush()
        return action

    async def list_actions(
        self,
        *,
        session_id: UUID,
        workspace_id: str,
        limit: int = 100,
    ) -> list[BrowserAction]:
        """列出指定 session 在当前 workspace 下的 actions。"""

        statement = (
            select(BrowserAction)
            .where(BrowserAction.session_id == session_id, BrowserAction.workspace_id == workspace_id)
            .order_by(BrowserAction.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def create_log(
        self,
        *,
        workspace_id: str,
        session_id: UUID,
        action_id: UUID | None,
        level: str,
        message: str,
        metadata: dict[str, Any] | None = None,
    ) -> BrowserActionLog:
        """创建 browser action log。"""

        log = BrowserActionLog(
            workspace_id=workspace_id,
            session_id=session_id,
            action_id=action_id,
            level=level,
            message=message,
            log_metadata=metadata or {},
        )
        self.session.add(log)
        await self.session.flush()
        return log

    async def list_logs(
        self,
        *,
        session_id: UUID,
        workspace_id: str,
        limit: int = 100,
    ) -> list[BrowserActionLog]:
        """列出指定 session 在当前 workspace 下的 logs。"""

        statement = (
            select(BrowserActionLog)
            .where(BrowserActionLog.session_id == session_id, BrowserActionLog.workspace_id == workspace_id)
            .order_by(BrowserActionLog.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())
