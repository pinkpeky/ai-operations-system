"""创建任务内置工具。"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.repositories.task_observability_repository import TaskObservabilityRepository
from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskResponse
from app.tools.base import BaseTool, ToolExecutionContext


class CreateTaskToolInput(BaseModel):
    """创建任务工具输入。"""

    title: str = Field(min_length=1, max_length=255, description="任务标题")
    task_type: str = Field(min_length=1, max_length=64, description="任务类型")
    payload: dict[str, Any] = Field(default_factory=dict, description="任务 payload")
    scheduled_at: datetime | None = Field(default=None, description="计划执行时间")
    max_retries: int = Field(default=3, ge=0, le=20, description="最大重试次数")


class CreateTaskToolOutput(BaseModel):
    """创建任务工具输出。"""

    task: dict[str, Any]


class CreateTaskTool(BaseTool):
    """创建 workspace 隔离任务的工具。"""

    name = "create_task_tool"
    description = "Create a task in the current workspace."
    input_schema = CreateTaskToolInput
    output_schema = CreateTaskToolOutput
    permission_scopes = ["tasks:write"]

    async def execute(self, tool_input: BaseModel, context: ToolExecutionContext) -> BaseModel:
        """创建任务并写入任务事件/日志。"""

        request = CreateTaskToolInput.model_validate(tool_input.model_dump())
        session = context.require_session()
        task_repository = TaskRepository(session)
        task = await task_repository.create_task(
            title=request.title,
            task_type=request.task_type,
            payload=request.payload,
            workspace_id=context.require_workspace(),
            user_id=context.user_id,
            scheduled_at=request.scheduled_at,
            max_retries=request.max_retries,
        )
        observability = TaskObservabilityRepository(session)
        await observability.create_event(
            task_id=task.id,
            workspace_id=context.workspace_id,
            event_type="created",
            message="Task created by tool",
            payload={"tool_name": self.name, "task_type": task.task_type},
        )
        await observability.create_log(
            task_id=task.id,
            workspace_id=context.workspace_id,
            level="info",
            message="Task created by tool",
            metadata={"tool_name": self.name, "task_type": task.task_type},
        )
        await session.commit()
        return CreateTaskToolOutput(task=TaskResponse.model_validate(task).model_dump(mode="json"))
