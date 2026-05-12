"""Reranker API 数据模型模块。"""

from pydantic import BaseModel


class RerankerHealthResponse(BaseModel):
    """Reranker Provider 健康检查响应。"""

    provider: str
    model: str
    reachable: bool
    enabled: bool
    error: str | None = None
