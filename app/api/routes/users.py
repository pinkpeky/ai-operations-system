"""用户管理 API 路由模块。"""

import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.db.postgres import get_session
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreateRequest, UserListResponse, UserResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserResponse, status_code=201)
async def create_user(
    request: UserCreateRequest,
    session: AsyncSession = Depends(get_session),
) -> UserResponse:
    """创建用户。"""

    try:
        repository = UserRepository(session)
        user = await repository.create_user(username=request.username, email=request.email)
        return UserResponse.from_model(user)
    except Exception as exc:
        logger.exception("User create API failed")
        raise AppError(f"User create failed: {exc}", status_code=500) from exc


@router.get("", response_model=UserListResponse)
async def list_users(
    limit: int = Query(default=100, ge=1, le=500, description="返回数量"),
    session: AsyncSession = Depends(get_session),
) -> UserListResponse:
    """查询用户列表。"""

    try:
        repository = UserRepository(session)
        users = await repository.list_users(limit=limit)
        return UserListResponse(items=[UserResponse.from_model(user) for user in users])
    except Exception as exc:
        logger.exception("User list API failed")
        raise AppError("User list failed", status_code=500) from exc
