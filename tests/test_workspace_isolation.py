"""Workspace 隔离基础测试模块。"""

import pytest

from app.repositories.task_repository import TaskRepository
from app.repositories.user_repository import UserRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.models.enums import TaskStatus


@pytest.mark.asyncio
async def test_task_query_is_scoped_by_workspace(session) -> None:  # type: ignore[no-untyped-def]
    """任务查询必须按 workspace_id 隔离，避免查全库。"""

    repository = TaskRepository(session)
    await repository.create_task(
        title="workspace a task",
        task_type="demo",
        workspace_id="workspace-a",
        user_id="user-a",
    )
    await repository.create_task(
        title="workspace b task",
        task_type="demo",
        workspace_id="workspace-b",
        user_id="user-b",
    )

    workspace_a_tasks = await repository.list_tasks_by_status(
        status=TaskStatus.PENDING,
        workspace_id="workspace-a",
    )

    assert len(workspace_a_tasks) == 1
    assert workspace_a_tasks[0].workspace_id == "workspace-a"
    assert workspace_a_tasks[0].title == "workspace a task"


@pytest.mark.asyncio
async def test_workspace_and_user_can_be_created(session) -> None:  # type: ignore[no-untyped-def]
    """工作区和用户基础表应可创建。"""

    user = await UserRepository(session).create_user(username="member-user", email="member@example.com")
    workspace = await WorkspaceRepository(session).create_workspace(name="Member Workspace", slug="member-workspace")

    assert str(user.id)
    assert str(workspace.id)
    assert user.status == "active"
    assert workspace.status == "active"
