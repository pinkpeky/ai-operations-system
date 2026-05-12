"""API Key 测试模块。"""

import pytest

from app.repositories.api_key_repository import APIKeyRepository
from app.repositories.user_repository import UserRepository
from app.repositories.workspace_repository import WorkspaceRepository


@pytest.mark.asyncio
async def test_api_key_stores_hash_and_returns_plain_once(session) -> None:  # type: ignore[no-untyped-def]
    """创建 API Key 时数据库只保存 hash，明文只由创建结果返回。"""

    user = await UserRepository(session).create_user(username="api-user", email="api@example.com")
    workspace = await WorkspaceRepository(session).create_workspace(name="API Workspace", slug="api-workspace")
    repository = APIKeyRepository(session)

    created = await repository.create_api_key(workspace_id=workspace.id, user_id=user.id, name="test-key")

    assert created.plain_key.startswith("aiops_")
    assert created.api_key.key_hash != created.plain_key
    assert created.api_key.key_hash == repository.hash_key(created.plain_key)
    assert created.api_key.workspace_id == workspace.id
    assert created.api_key.user_id == user.id
