"""任务接口数据模型模块。

该模块定义任务创建、Agentic RAG 任务创建和查询接口的数据结构，保证 API 输入输出稳定。
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import TaskStatus
from app.schemas.agent import ContentAgentRequest


class TaskCreateRequest(BaseModel):
    """创建通用任务请求。"""

    title: str = Field(min_length=1, max_length=255, description="任务标题")
    task_type: str = Field(min_length=1, max_length=64, description="任务类型")
    payload: dict[str, Any] = Field(default_factory=dict, description="任务负载")
    account_id: UUID | None = Field(default=None, description="关联账号 ID")
    scheduled_at: datetime | None = Field(default=None, description="计划执行时间")
    max_retries: int = Field(default=3, ge=0, le=20, description="最大重试次数")


class AgenticRAGTaskCreateRequest(BaseModel):
    """创建 Agentic RAG 查询任务请求。"""

    query: str = Field(min_length=1, description="用户问题")
    collection_name: str | None = Field(default=None, min_length=1, max_length=128, description="可选知识库 collection")
    top_k: int = Field(default=3, ge=1, le=20, description="检索返回 chunk 数量")
    debug: bool = Field(default=False, description="是否返回调试信息")
    title: str | None = Field(default=None, min_length=1, max_length=255, description="任务标题")
    scheduled_at: datetime | None = Field(default=None, description="计划执行时间")
    max_retries: int = Field(default=3, ge=0, le=20, description="最大重试次数")


class ContentGenerationTaskCreateRequest(ContentAgentRequest):
    """创建内容生成任务请求。"""

    title: str | None = Field(default=None, min_length=1, max_length=255, description="任务标题")
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
