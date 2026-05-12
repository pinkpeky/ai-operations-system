"""工作区 Repository 模块。"""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import WorkspaceStatus
from app.models.workspace import Workspace

logger = logging.getLogger(__name__)


class WorkspaceRepository:
    """工作区数据访问层。"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_workspace(self, *, name: str, slug: str) -> Workspace:
        """创建工作区。"""

        workspace = Workspace(name=name, slug=slug, status=WorkspaceStatus.ACTIVE.value)
        self.session.add(workspace)
        await self.session.commit()
        await self.session.refresh(workspace)
        logger.info("Workspace created", extra={"workspace_id": str(workspace.id), "slug": slug})
        return workspace

    async def list_workspaces(self, *, limit: int = 100) -> list[Workspace]:
        """查询工作区列表。"""

        statement = select(Workspace).order_by(Workspace.created_at.desc()).limit(limit)
        result = await self.session.execute(statement)
        return list(result.scalars().all())
