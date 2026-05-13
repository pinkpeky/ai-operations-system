"""Multi-Agent run repository。"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import AgentHandoffStatus, AgentRunStatus
from app.models.multi_agent import AgentHandoff, AgentMessage, AgentRun


class AgentRunRepository:
    """AgentRun / AgentMessage / AgentHandoff 数据访问层。"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_run(
        self,
        *,
        workspace_id: str,
        user_id: str | None,
        session_id: UUID | None,
        root_agent: str,
        run_input: dict[str, Any],
    ) -> AgentRun:
        """创建 run。"""

        run = AgentRun(
            workspace_id=workspace_id,
            user_id=user_id,
            session_id=session_id,
            root_agent=root_agent,
            status=AgentRunStatus.PENDING.value,
            run_input=run_input,
        )
        self.session.add(run)
        await self.session.flush()
        return run

    async def get_run(self, *, run_id: UUID, workspace_id: str) -> AgentRun | None:
        """按 workspace 查询 run。"""

        result = await self.session.execute(
            select(AgentRun).where(AgentRun.id == run_id, AgentRun.workspace_id == workspace_id)
        )
        return result.scalar_one_or_none()

    async def list_runs(self, *, workspace_id: str, limit: int = 100) -> list[AgentRun]:
        """列出当前 workspace 的 runs。"""

        result = await self.session.execute(
            select(AgentRun)
            .where(AgentRun.workspace_id == workspace_id)
            .order_by(AgentRun.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def mark_running(self, run: AgentRun) -> AgentRun:
        """标记 run 开始执行。"""

        run.status = AgentRunStatus.RUNNING.value
        run.started_at = datetime.now(timezone.utc)
        await self.session.flush()
        return run

    async def complete_run(self, run: AgentRun, *, output: dict[str, Any], duration_ms: int) -> AgentRun:
        """标记 run 成功完成。"""

        run.status = AgentRunStatus.COMPLETED.value
        run.run_output = output
        run.error = None
        run.completed_at = datetime.now(timezone.utc)
        run.duration_ms = duration_ms
        await self.session.flush()
        return run

    async def fail_run(self, run: AgentRun, *, error: str, duration_ms: int) -> AgentRun:
        """标记 run 失败。"""

        run.status = AgentRunStatus.FAILED.value
        run.error = error
        run.completed_at = datetime.now(timezone.utc)
        run.duration_ms = duration_ms
        await self.session.flush()
        return run

    async def append_message(
        self,
        *,
        workspace_id: str,
        run_id: UUID,
        from_agent: str | None,
        to_agent: str | None,
        role: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> AgentMessage:
        """写入 run 内消息。"""

        message = AgentMessage(
            workspace_id=workspace_id,
            run_id=run_id,
            from_agent=from_agent,
            to_agent=to_agent,
            role=role,
            content=content,
            message_metadata=metadata or {},
        )
        self.session.add(message)
        await self.session.flush()
        return message

    async def create_handoff(
        self,
        *,
        workspace_id: str,
        run_id: UUID,
        from_agent: str,
        to_agent: str,
        reason: str,
        payload: dict[str, Any],
        status: str = AgentHandoffStatus.COMPLETED.value,
    ) -> AgentHandoff:
        """写入 handoff。"""

        handoff = AgentHandoff(
            workspace_id=workspace_id,
            run_id=run_id,
            from_agent=from_agent,
            to_agent=to_agent,
            reason=reason,
            payload=payload,
            status=status,
        )
        self.session.add(handoff)
        await self.session.flush()
        return handoff

    async def list_messages(self, *, run_id: UUID, workspace_id: str, limit: int = 200) -> list[AgentMessage]:
        """列出 run messages。"""

        result = await self.session.execute(
            select(AgentMessage)
            .where(AgentMessage.run_id == run_id, AgentMessage.workspace_id == workspace_id)
            .order_by(AgentMessage.created_at.asc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def list_handoffs(self, *, run_id: UUID, workspace_id: str, limit: int = 200) -> list[AgentHandoff]:
        """列出 run handoffs。"""

        result = await self.session.execute(
            select(AgentHandoff)
            .where(AgentHandoff.run_id == run_id, AgentHandoff.workspace_id == workspace_id)
            .order_by(AgentHandoff.created_at.asc())
            .limit(limit)
        )
        return list(result.scalars().all())
