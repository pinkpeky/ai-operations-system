"""API Key Repository 模块。"""

import hashlib
import logging
import secrets
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.api_key import APIKey
from app.models.enums import APIKeyStatus

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class CreatedAPIKey:
    """创建 API Key 的返回结构。"""

    api_key: APIKey
    plain_key: str


class APIKeyRepository:
    """API Key 数据访问层。"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_api_key(self, *, workspace_id: UUID, user_id: UUID, name: str) -> CreatedAPIKey:
        """创建 API Key，数据库只保存哈希值。"""

        plain_key = self.generate_plain_key()
        api_key = APIKey(
            workspace_id=workspace_id,
            user_id=user_id,
            key_hash=self.hash_key(plain_key),
            name=name,
            status=APIKeyStatus.ACTIVE.value,
        )
        self.session.add(api_key)
        await self.session.commit()
        await self.session.refresh(api_key)
        logger.info("API key created", extra={"api_key_id": str(api_key.id), "workspace_id": str(workspace_id)})
        return CreatedAPIKey(api_key=api_key, plain_key=plain_key)

    def generate_plain_key(self) -> str:
        """生成只返回一次的 API Key 明文。"""

        return f"aiops_{secrets.token_urlsafe(32)}"

    def hash_key(self, plain_key: str) -> str:
        """哈希 API Key 明文。"""

        return hashlib.sha256(plain_key.encode("utf-8")).hexdigest()
