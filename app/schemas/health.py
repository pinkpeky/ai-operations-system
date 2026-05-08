"""健康检查响应模型模块。

该模块定义 /health 接口返回的数据结构，便于 API 文档和调用方保持一致。
"""

import logging
from typing import Literal

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ComponentHealth(BaseModel):
    """单个基础组件的健康状态。"""

    name: str = Field(description="Component name")
    status: Literal["ok", "error"] = Field(description="Component health status")
    detail: str = Field(default="ready", description="Human readable status detail")


class HealthResponse(BaseModel):
    """整体健康检查结果。"""

    status: Literal["ok", "degraded"]
    components: list[ComponentHealth]
