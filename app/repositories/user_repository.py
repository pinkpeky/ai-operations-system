"""用户 Repository 模块。"""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import UserStatus
from app.models.user import User

logger = logging.getLogger(__name__)


class UserRepository:
    """用户数据访问层。"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_user(self, *, username: str, email: str) -> User:
        """创建用户。"""

        user = User(username=username, email=email, status=UserStatus.ACTIVE.value)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        logger.info("User created", extra={"user_id": str(user.id), "username": username})
        return user

    async def list_users(self, *, limit: int = 100) -> list[User]:
        """查询用户列表。"""

        statement = select(User).order_by(User.created_at.desc()).limit(limit)
        result = await self.session.execute(statement)
        return list(result.scalars().all())
