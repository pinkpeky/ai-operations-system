"""API Key 管理 API 路由模块。"""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.db.postgres import get_session
from app.repositories.api_key_repository import APIKeyRepository
from app.schemas.api_key import APIKeyCreateRequest, APIKeyCreateResponse, APIKeyResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api-keys", tags=["api-keys"])


@router.post("", response_model=APIKeyCreateResponse, status_code=201)
async def create_api_key(
    request: APIKeyCreateRequest,
    session: AsyncSession = Depends(get_session),
) -> APIKeyCreateResponse:
    """创建 API Key，明文只在本次响应中返回。"""

    try:
        repository = APIKeyRepository(session)
        created = await repository.create_api_key(
            workspace_id=request.workspace_id,
            user_id=request.user_id,
            name=request.name,
        )
        base = APIKeyResponse.from_model(created.api_key).model_dump()
        return APIKeyCreateResponse(**base, api_key=created.plain_key)
    except Exception as exc:
        logger.exception("API key create API failed")
        raise AppError(f"API key create failed: {exc}", status_code=500) from exc
