"""可观测性 API Schema。"""

from pydantic import BaseModel, Field


class ObservabilitySummaryResponse(BaseModel):
    """任务可观测性概览响应。"""

    pending_count: int = Field(description="pending 任务数量")
    running_count: int = Field(description="running 任务数量")
    failed_count: int = Field(description="failed 任务数量")
    completed_count: int = Field(description="completed 任务数量")
    cancelled_count: int = Field(description="cancelled 任务数量")
    timeout_count: int = Field(description="timeout 任务数量")
    avg_duration_ms: float | None = Field(default=None, description="已记录耗时任务的平均耗时")
