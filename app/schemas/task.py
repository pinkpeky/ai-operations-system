"""任务接口数据模型模块。

该模块定义任务创建和查询接口的数据结构，保证 API 输入输出稳定。
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import TaskStatus


class TaskCreateRequest(BaseModel):
    """创建任务请求。"""

    title: str = Field(min_length=1, max_length=255, description="任务标题")
    task_type: str = Field(min_length=1, max_length=64, description="任务类型")
    payload: dict[str, Any] = Field(default_factory=dict, description="任务负载")
    account_id: UUID | None = Field(default=None, description="关联账号 ID")
    scheduled_at: datetime | None = Field(default=None, description="计划执行时间")
    max_retries: int = Field(default=3, ge=0, le=20, description="最大重试次数")


class TaskResponse(BaseModel):
    """任务响应。"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime
    status: str
    title: str
    task_type: str
    payload: dict[str, Any]
    account_id: UUID | None
    retry_count: int
    max_retries: int
    scheduled_at: datetime | None
    started_at: datetime | None
    completed_at: datetime | None
    last_error: str | None


class TaskListResponse(BaseModel):
    """任务列表响应。"""

    status: TaskStatus
    items: list[TaskResponse]
