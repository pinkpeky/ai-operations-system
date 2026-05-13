"""查询任务状态内置工具。"""

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskResponse
from app.tools.base import BaseTool, ToolExecutionContext


class GetTaskStatusToolInput(BaseModel):
    """查询任务状态工具输入。"""

    task_id: UUID = Field(description="任务 ID")


class GetTaskStatusToolOutput(BaseModel):
    """查询任务状态工具输出。"""

    task: dict[str, Any]


class GetTaskStatusTool(BaseTool):
    """按 workspace 查询任务状态的工具。"""

    name = "get_task_status_tool"
    description = "Get task status in the current workspace."
    input_schema = GetTaskStatusToolInput
    output_schema = GetTaskStatusToolOutput
    permission_scopes = ["tasks:read"]

    async def execute(self, tool_input: BaseModel, context: ToolExecutionContext) -> BaseModel:
        """查询任务状态。"""

        request = GetTaskStatusToolInput.model_validate(tool_input.model_dump())
        repository = TaskRepository(context.require_session())
        task = await repository.get_task(task_id=request.task_id, workspace_id=context.require_workspace())
        if task is None:
            raise ValueError("Task not found in workspace")
        return GetTaskStatusToolOutput(task=TaskResponse.model_validate(task).model_dump(mode="json"))
