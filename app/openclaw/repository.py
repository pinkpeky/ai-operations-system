"""OpenClaw action log repository."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.openclaw import OpenClawActionLog


class OpenClawActionLogRepository:
    """OpenClaw action log 持久化仓库。"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_log(
        self,
        *,
        workspace_id: str,
        worker_id: UUID | None,
        action_type: str,
        target: str | None,
        input_payload: dict[str, Any],
        output_payload: dict[str, Any],
        success: bool,
        error: str | None,
        duration_ms: int | None,
        provider: str,
        mock: bool,
    ) -> OpenClawActionLog:
        """写入一条 OpenClaw action log。"""

        log = OpenClawActionLog(
            workspace_id=workspace_id,
            worker_id=worker_id,
            action_type=action_type,
            target=target,
            input_payload=input_payload,
            output_payload=output_payload,
            success=success,
            error=error,
            duration_ms=duration_ms,
            provider=provider,
            mock=mock,
        )
        self.session.add(log)
        await self.session.flush()
        return log
